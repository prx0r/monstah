"""Paleo domain: reconstruct extinct-world entities from PBDB + Macrostrat."""

from __future__ import annotations

from typing import Any

from ..core.identity import MACROSTRAT, PBDB, Crosswalk
from ..core.models import Entity, Environment, Reference
from ..discovery.scenario_generator import Taxon
from ..evidence.models import Reconstruction, Source, Uncertainty
from ..ingest.macrostrat import MacrostratClient
from ..ingest.pbdb import PbdbClient


class PaleoLoader:
    """Build a 100-iconic-taxa MVP corpus: PBDB identity + Macrostrat context."""

    def __init__(
        self,
        pbdb: PbdbClient | None = None,
        macrostrat: MacrostratClient | None = None,
        cache_dir: str | None = "~/.cache/monstah",
    ) -> None:
        import os

        cache_dir = os.path.expanduser(cache_dir) if cache_dir else None
        self.pbdb = pbdb or PbdbClient(cache_dir=cache_dir)
        self.macrostrat = macrostrat or MacrostratClient(cache_dir=cache_dir)

    def load_taxon(self, name: str) -> Entity:
        rec = self.pbdb.taxon(name)["records"][0]
        tno = str(rec.get("taxon_no", ""))
        cw = Crosswalk(entity=Reference(namespace=PBDB, key=tno), names=[name])
        cw.set(PBDB, tno)
        return Entity(
            refs=cw.references,
            kind="taxon",
            name=name,
            traits={
                "rank": rec.get("taxon_rank"),
                "firstapp_max_ma": rec.get("firstapp_max_ma"),
                "lastapp_min_ma": rec.get("lastapp_min_ma"),
            },
        )

    def environment_for_occurrence(self, occ: dict) -> Environment:
        lat, lng = occ.get("lat"), occ.get("lng")
        age = occ.get("max_ma") or occ.get("min_ma")
        ctx: dict[str, Any] = {}
        if lat is not None and lng is not None and age is not None:
            units = self.macrostrat.unit_strat(lat=float(lat), lng=float(lng), age=float(age))
            if units:
                u = units[0]
                ctx["formation"] = u.get("strat_name")
                ctx["lithology"] = [l.get("name") for l in u.get("lith", []) if isinstance(l, dict)]
        return Environment(
            kind="paleoenvironment",
            name=occ.get("formation") or f"loc {lat},{lng}",
            region=occ.get("cc") or "",
            constraints={"age_ma": age, "lat": lat, "lng": lng, "context": ctx},
        )

    def to_taxon(self, entity: Entity) -> Taxon:
        return Taxon(
            ref=entity.refs[0],
            name=entity.name,
            min_ma=entity.traits.get("lastapp_min_ma") or 0.0,
            max_ma=entity.traits.get("firstapp_max_ma") or 66.0,
            env={"land"},
            diet="carnivore" if "saur" in entity.name.lower() or "rex" in entity.name.lower() else "herbivore",
            traits=entity.traits,
        )
