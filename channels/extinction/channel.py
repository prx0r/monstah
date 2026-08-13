"""Extinction theme — mass-extinction / ecosystem-collapse editorial policy.

Same PBDB + Macrostrat substrate as Prehistoric; the editorial policy is a
timeline story: BEFORE → EVENT → AFTER → SURVIVORS → RADIATION. Non-combat;
produces a graph/timeline story grounded in the taxa that existed across the
event boundary.
"""

from __future__ import annotations

from typing import Any

from monstah.core.models import Environment, Reference
from monstah.core.truth import Status
from monstah.discovery import Candidate, Taxon
from monstah.domains.paleo.seed import SEED_TAXA
from monstah.story.beats import BeatKind, StoryBeat
from monstah.story.episode import EpisodeSpec
from channels.base import Channel, ChannelManifest, EvidenceAdapter

# (label, min_ma, max_ma) around a mass-extinction boundary
EVENTS = [
    {"name": "K-Pg extinction", "min_ma": 66.0, "max_ma": 66.05, "before": "Cretaceous", "after": "Paleogene"},
    {"name": "Permian-Triassic", "min_ma": 251.9, "max_ma": 252.0, "before": "Permian", "after": "Triassic"},
    {"name": "End-Devonian", "min_ma": 358.9, "max_ma": 359.0, "before": "Devonian", "after": "Carboniferous"},
]


class ExtinctionAdapter(EvidenceAdapter):
    def __init__(self, *, offline: bool = False, event: str = "K-Pg extinction") -> None:
        self.offline = offline
        self.event = next(e for e in EVENTS if e["name"] == event)

    def load_taxa(self, limit: int = 50) -> list[Taxon]:
        lo, hi = self.event["min_ma"], self.event["max_ma"]
        out: list[Taxon] = []
        for s in SEED_TAXA:
            s_lo, s_hi = s.age_range()
            # taxa whose range straddles the boundary (survivors/casualties)
            if s_hi >= lo:
                t = Taxon(
                    ref=Reference(namespace="paleo", key=s.name.lower().replace(" ", "-")),
                    name=s.name, min_ma=s_lo, max_ma=s_hi, env=set(s.env),
                    diet=s.diet, region=s.region if s.region not in ("", "global") else "global",
                )
                t.set_evidence("mass_kg", s.traits.get("mass_kg", 2000.0), unit="kg")
                t.set_evidence("era", s.era, status=Status.OBSERVED.value)
                out.append(t)
                if len(out) >= limit:
                    break
        return out

    def environments(self) -> list[Environment]:
        return [Environment(kind="paleoenvironment", name=self.event["name"], region="global",
                            constraints={"min_ma": self.event["min_ma"], "max_ma": self.event["max_ma"]})]


class ExtinctionChannel(Channel):
    """Produces a before→event→after→survivors timeline story (non-combat)."""

    def __init__(self, manifest: ChannelManifest, adapter: ExtinctionAdapter, **kw: Any) -> None:
        super().__init__(manifest, adapter, **kw)
        self._adapter = adapter

    def produce_graph(self, candidate: Candidate, taxa_by_ref: dict[str, Taxon], overlap=None):
        ev = self._adapter.event
        before = [t for t in taxa_by_ref.values() if t.max_ma > ev["max_ma"]]
        after = [t for t in taxa_by_ref.values() if t.min_ma <= ev["min_ma"]]
        survivors = [t for t in taxa_by_ref.values() if t.max_ma > ev["max_ma"] and t.min_ma <= ev["min_ma"]]
        beats = [
            StoryBeat("b1", BeatKind.SOURCE_FACT, f"{ev['before']}: {len(before)} reconstructed taxa present.",
                      basis_assertion_ids=[]),
            StoryBeat("b2", BeatKind.UNCERTAINTY, f"At ~{ev['min_ma']} Ma the {ev['name']} occurred."),
            StoryBeat("b3", BeatKind.SOURCE_FACT, f"After: {len(after)} taxa persist into the {ev['after']}."),
            StoryBeat("b4", BeatKind.RECONSTRUCTION, f"{len(survivors)} taxa straddle the boundary (potential survivors).",
                      basis_reconstruction_ids=[t.ref.uri for t in survivors]),
        ]
        ep = EpisodeSpec(episode_id=f"extinction:{ev['name']}",
                         hook=ev["name"], thesis="ecosystem collapse across the boundary",
                         question=f"What survived the {ev['name']}?", beats=beats)
        out = super().produce_graph(candidate, taxa_by_ref, overlap)
        out.story = ep
        return out


def extinction_channel(*, n_runs: int = 500, offline: bool = False, event: str = "K-Pg extinction") -> Channel:
    manifest = ChannelManifest(
        name="extinction",
        title="Extinction",
        description="Mass-extinction / ecosystem-collapse timeline stories",
    )
    return ExtinctionChannel(manifest, ExtinctionAdapter(offline=offline, event=event), mode="historical", n_runs=n_runs)
