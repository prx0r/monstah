"""Ancient Oceans theme: marine prehistory (ANCIENT OCEANS).

Reuses the prehistoric evidence adapter but keeps only marine fauna, binding
oceanic paleoenvironments. Same shared battle engine.
"""

from __future__ import annotations

from monstah.core.models import Environment, Reference
from monstah.core.truth import Status
from monstah.discovery import Candidate, Taxon
from monstah.domains.paleo.seed import SEED_TAXA, seed_environments
from channels.base import Channel, ChannelManifest, EvidenceAdapter
from channels.prehistoric.channel import _derive_combat

MARINE_ENV = {"marine", "sea", "coastal"}


class AncientOceansAdapter(EvidenceAdapter):
    def __init__(self, *, cache_dir: str | None = None) -> None:
        self._cache = cache_dir
        self._envs = [e for e in seed_environments() if e["kind"] in ("marine", "coastal")]

    def load_taxa(self, limit: int = 50) -> list[Taxon]:
        out: list[Taxon] = []
        marine = [s for s in SEED_TAXA if set(s.env) & MARINE_ENV]
        for s in marine[:limit]:
            lo, hi = s.age_range()
            t = Taxon(
                ref=Reference(namespace="paleo", key=s.name.lower().replace(" ", "-")),
                name=s.name, min_ma=lo, max_ma=hi, env=set(s.env),
                diet=s.diet, region=s.region if s.region not in ("", "global") else "global",
            )
            t.set_evidence("mass_kg", s.traits.get("mass_kg", 2000.0), unit="kg")
            t.set_evidence("era", s.era)
            t.set_evidence("habitat", "marine", status=Status.OBSERVED.value)
            for k, v in _derive_combat(s.name).items():
                t.set_game_proxy(k, v, status=Status.GAME_PROXY.value, source="derived")
            out.append(t)
        return out

    def environments(self) -> list[Environment]:
        return [
            Environment(kind="paleocean", name=e["name"], region=e.get("loc", ""),
                        constraints={"era": e["era"], "min_ma": e["min_ma"], "max_ma": e["max_ma"]})
            for e in self._envs
        ]


def ancient_oceans_channel(*, n_runs: int = 1000) -> Channel:
    manifest = ChannelManifest(
        name="ancient-oceans",
        title="Ancient Oceans",
        description="Marine prehistory: mesozoic/oceanic reconstruction",
    )
    return Channel(manifest, AncientOceansAdapter(), mode="historical", n_runs=n_runs)
