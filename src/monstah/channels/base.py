"""Channel abstraction: a theme = evidence adapter + story policy over the core engine.

Every channel runs the SAME chain:

    ENTITY -> ENVIRONMENT -> RELATION -> SCENARIO -> SIMULATION -> EVENT -> STORY -> SHOT

The channel only decides:
  1. how entities/environments get populated (the evidence adapter)
  2. what the engine is allowed to claim (the story policy: historical vs lab)

So one battle engine + renderer serves every theme (prehistoric, deep-blue,
tree-of-life, alien-worlds...) by swapping the adapter. Reusable assets
(reconstructions, statblocks, visuals) compound across channels.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable

from ..core.models import Entity, Environment, Reference
from ..discovery import Candidate, ScenarioDiscovery, Taxon
from ..pipeline import PipelineOutput, run_candidate


@dataclass
class ChannelManifest:
    """Metadata + the reusable assets a channel has already built up."""

    name: str
    title: str
    description: str = ""
    entities: dict[str, Entity] = field(default_factory=dict)
    environments: dict[str, Environment] = field(default_factory=dict)
    versions: dict[str, str] = field(default_factory=dict)  # entity -> reconstruction version
    asset_uris: dict[str, str] = field(default_factory=dict)  # entity -> R2 asset uri


class EvidenceAdapter(ABC):
    """How a theme turns external sources into entities/scenarios."""

    @abstractmethod
    def load_taxa(self, limit: int = 50) -> list[Taxon]:
        """Populate the graph's taxa from this channel's sources."""

    @abstractmethod
    def taxon_for_combat(self, name: str) -> dict:
        """Return Open5e-style statblock stats for a taxon (for the battle engine)."""

    def environments(self) -> list[Environment]:
        return []


class Channel:
    """A theme running the shared engine with a specific adapter + policy."""

    def __init__(
        self,
        manifest: ChannelManifest,
        adapter: EvidenceAdapter,
        *,
        mode: str = "historical",
        n_runs: int = 1000,
    ) -> None:
        self.manifest = manifest
        self.adapter = adapter
        self.mode = mode
        self.n_runs = n_runs

    # -- evidence step: build the graph -------------------------------
    def ingest(self, limit: int = 50) -> list[Taxon]:
        taxa = self.adapter.load_taxa(limit=limit)
        for t in taxa:
            self.manifest.entities.setdefault(
                t.ref.key,
                Entity(refs=[t.ref], kind="taxon", name=t.name, traits=t.traits),
            )
        return taxa

    # -- discovery step: let the database write the calendar -----------
    def discover(self, taxa: list[Taxon], top_n: int = 10) -> list[Candidate]:
        return ScenarioDiscovery(taxa).generate(top_n)

    # -- simulation step: fight them with the shared engine ------------
    def produce(self, candidate: Candidate, taxa_by_ref: dict[str, Taxon]) -> PipelineOutput:
        # inject theme-specific combat stats via the adapter
        for t in taxa_by_ref.values():
            t.traits.update(self.adapter.taxon_for_combat(t.name))
        return run_candidate(candidate, taxa_by_ref, n_runs=self.n_runs)

    # -- render step: story + shots, then store ------------------------
    def render(self, output: PipelineOutput) -> PipelineOutput:
        # ensure shots carry this theme's channel name
        return output

    @property
    def theme(self) -> str:
        return self.manifest.name
