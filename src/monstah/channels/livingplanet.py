"""Living Planet theme: ecology graph stories, NON-COMBAT (FOOD WEB WARS).

Evidence adapter: GloBI (Global Biotic Interactions) directed edges. Content is
graph/data stories — "who eats whom / the food web" — with no battle engine.
This proves the channel abstraction is not battle-specific.
"""

from __future__ import annotations

from typing import Any

from ..core.models import Environment, Reference
from ..discovery import Candidate, Taxon
from ..ingest.globi import GlobiClient
from .base import Channel, ChannelManifest, EvidenceAdapter

TAXA = [
    ("Orcinus orca", "Killer Whale", "carnivore"),
    ("Carcharodon carcharias", "Great White Shark", "carnivore"),
    ("Arctocephalus pusillus", "Fur Seal", "carnivore"),
    ("Engraulis", "Anchovy", "herbivore"),
    ("Thunnus", "Tuna", "carnivore"),
    ("Sepia", "Cuttlefish", "carnivore"),
    ("Physeter macrocephalus", "Sperm Whale", "carnivore"),
]


class LivingPlanetAdapter(EvidenceAdapter):
    def __init__(self, *, cache_dir: str | None = None) -> None:
        self.globi = GlobiClient(cache_dir=cache_dir)

    def load_taxa(self, limit: int = 20) -> list[Taxon]:
        out: list[Taxon] = []
        for scientific, label, diet in TAXA[:limit]:
            t = Taxon(
                ref=Reference(namespace="worms", key=scientific.lower().replace(" ", "-")),
                name=label, min_ma=0.0, max_ma=0.0, env={"sea"}, diet=diet, region="global",
            )
            t.set_evidence("scientific_name", scientific)
            out.append(t)
        return out

    def environments(self) -> list[Environment]:
        return [Environment(kind="ocean", name="Marine Food Web", region="global",
                            constraints={"domain": "pelagic"})]


class LivingPlanetChannel(Channel):
    """Overrides produce_graph to actually query GloBI for a real edge story."""

    def __init__(self, manifest: ChannelManifest, adapter: LivingPlanetAdapter, **kw: Any) -> None:
        super().__init__(manifest, adapter, **kw)
        self._adapter = adapter

    def produce_graph(self, candidate: Candidate, taxa_by_ref: dict[str, Taxon], overlap=None):
        a = taxa_by_ref[candidate.entities[0].key]
        b = taxa_by_ref[candidate.entities[1].key]
        # query the real interaction edge for the story
        edges = []
        try:
            edges = self._adapter.globi.interactions(a.facts.evidence.get("scientific_name").value, limit=10)
        except Exception:
            edges = []
        evidence = (
            f"{len(edges)} real GloBI interaction records for {a.name}; "
            f"temporal/species co-occurrence: {overlap.summary() if overlap else 'n/a'}."
        )
        story = type(
            "Ep", (), {
                "title": f"{a.name} in the marine food web",
                "scenario_id": candidate.template, "channel": self.theme,
                "hook": f"What does {a.name} actually interact with?",
                "evidence": evidence,
                "conclusion": "Graph story from GloBI interaction edges; no battle simulation.",
                "render": lambda: evidence,
            }
        )()
        out = super().produce_graph(candidate, taxa_by_ref, overlap)
        out.story = story
        return out


def living_planet_channel(*, n_runs: int = 1000) -> "Channel":
    manifest = ChannelManifest(
        name="living-planet",
        title="Living Planet",
        description="Ecology graph stories via GloBI interaction edges (non-combat)",
    )
    return LivingPlanetChannel(manifest, LivingPlanetAdapter(), mode="historical", n_runs=n_runs)
