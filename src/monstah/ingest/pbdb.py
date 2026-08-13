"""Paleobiology Database (PBDB) Data Service 1.2 client.

The stable production data service. Yields taxa, fossil occurrences,
collections, references, and ecological attributes programmatically.
"""

from __future__ import annotations

from typing import Any, Iterator

from ..core.identity import PBDB, Crosswalk
from ..core.models import Reference
from .base import HttpApi


class PbdbClient(HttpApi):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__("https://paleobiodb.org/data1.2", **kwargs)

    # --- records ---

    def taxon(
        self,
        taxon_name: str,
        *,
        vocab: str = "pbdb",
        show: str = "attr,app,class,ref",
    ) -> dict:
        return self.get("taxa/single.json", {"name": taxon_name, "vocab": vocab, "show": show})

    def taxa(
        self,
        *,
        base_name: str | None = None,
        taxon_rank: str | None = None,
        min_ma: float | None = None,
        max_ma: float | None = None,
        limit: int = 50,
        show: str = "attr,class,ref",
    ) -> list[dict]:
        params: dict[str, Any] = {"limit": limit, "show": show}
        if base_name:
            params["base_name"] = base_name
        if taxon_rank:
            params["taxon_rank"] = taxon_rank
        if min_ma is not None:
            params["min_ma"] = min_ma
        if max_ma is not None:
            params["max_ma"] = max_ma
        return self.get("taxa/list.json", params)["records"]

    def occurrences(
        self,
        *,
        taxon_name: str | None = None,
        base_name: str | None = None,
        continent: str | None = None,
        min_ma: float | None = None,
        max_ma: float | None = None,
        limit: int = 100,
        show: str = "coords,geo,env,ref",
    ) -> list[dict]:
        params: dict[str, Any] = {"limit": limit, "show": show}
        if taxon_name:
            params["taxon_name"] = taxon_name
        if base_name:
            params["base_name"] = base_name
        if continent:
            params["continent"] = continent
        if min_ma is not None:
            params["min_ma"] = min_ma
        if max_ma is not None:
            params["max_ma"] = max_ma
        return self.get("occs/list.json", params)["records"]

    # --- helpers ---

    def crosswalk(self, taxon_name: str) -> Crosswalk:
        """Build a crosswalk from a PBDB taxon record (pbdb id + classification)."""
        rec = self.taxon(taxon_name)["records"][0]
        cw = Crosswalk(
            entity=Reference(namespace=PBDB, key=str(rec.get("taxon_no", ""))),
            names=[rec.get("taxon_name", taxon_name)],
        )
        cw.set(PBDB, str(rec.get("taxon_no", "")))
        return cw

    def _first_occ(self, taxon_name: str, field: str) -> float | None:
        recs = self.taxa(base_name=taxon_name, limit=1, show="attr")
        if not recs:
            return None
        return recs[0].get(field)

    def temporal_overlap(self, a: str, b: str) -> bool:
        """Do two taxa share any time interval (by first/last appearance)?"""
        a_first, a_last = self._first_occ(a, "firstapp_max_ma"), self._first_occ(a, "lastapp_min_ma")
        b_first, b_last = self._first_occ(b, "firstapp_max_ma"), self._first_occ(b, "lastapp_min_ma")
        if None in (a_first, a_last, b_first, b_last):
            return True  # unknown range => do not exclude
        return a_first >= b_last and b_first >= a_last
