"""Scenario Discovery Engine.

Instead of a human deciding "what video should I make today", enumerate graph
configurations and score them. The database writes the editorial calendar.

Content emerges from graph queries: temporal+spatial overlap -> plausibility,
plus novelty / recognizability / scientific & visual interest.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from ..core.models import Reference

SCENARIO_TYPES = (
    "predation",
    "escape",
    "hunt",
    "ambush",
    "scavenge",
    "migration",
    "competition",
    "survival",
    "environmental_change",
    "group_defence",
    "pack_hunt",
    "resource_competition",
    "ecosystem_collapse",
    "colonization",
)


@dataclass
class Candidate:
    template: str
    entities: list[Reference]
    environment: Reference | None
    mode: str = "historical"
    score: float = 0.0
    factors: dict[str, float] = field(default_factory=dict)
    note: str = ""

    def __str__(self) -> str:
        names = ", ".join(e.key for e in self.entities)
        return f"[{self.score:.2f}] {self.template}: {names} ({self.mode})"


@dataclass
class Taxon:
    ref: Reference
    name: str
    min_ma: float
    max_ma: float
    env: set[str]
    diet: str = ""
    traits: dict = field(default_factory=dict)


class ScenarioDiscovery:
    """Pairwise enumeration over taxa + environments, scored for content."""

    WEIGHTS = {
        "temporal_overlap": 0.30,
        "spatial_overlap": 0.20,
        "environment_match": 0.15,
        "interaction_strength": 0.15,
        "novelty": 0.10,
        "recognizability": 0.10,
    }

    def __init__(self, taxa: Iterable[Taxon]) -> None:
        self.taxa = list(taxa)

    def temporal_overlap(self, a: Taxon, b: Taxon) -> float:
        # living taxa (both at the present) always coexist in time
        if a.max_ma <= 0 and b.max_ma <= 0:
            return 1.0
        lo = max(a.min_ma, b.min_ma)
        hi = min(a.max_ma, b.max_ma)
        return max(0.0, min(1.0, (hi - lo) / 20.0))

    def spatial_overlap(self, a: Taxon, b: Taxon) -> float:
        shared = a.env & b.env
        if not shared:
            return 0.0
        return len(shared) / max(1, min(len(a.env), len(b.env)))

    def environment_match(self, a: Taxon, b: Taxon) -> float:
        return 1.0 if (a.env & b.env) else 0.0

    def interaction_strength(self, a: Taxon, b: Taxon) -> float:
        if a.diet == "carnivore" and b.diet != "carnivore":
            return 1.0
        if b.diet == "carnivore" and a.diet != "carnivore":
            return 1.0
        if a.diet == b.diet == "carnivore":
            return 0.7  # competition
        return 0.3

    def recognizability(self, a: Taxon, b: Taxon) -> float:
        return min(1.0, (len(a.name) + len(b.name)) / 40.0)

    def novelty(self, a: Taxon, b: Taxon) -> float:
        return 0.5  # placeholder; real value comes from scenario history

    def score_pair(self, a: Taxon, b: Taxon) -> Candidate | None:
        to = self.temporal_overlap(a, b)
        if to <= 0:
            return None
        so = self.spatial_overlap(a, b)
        em = self.environment_match(a, b)
        inter = self.interaction_strength(a, b)
        fac = {
            "temporal_overlap": to,
            "spatial_overlap": so,
            "environment_match": em,
            "interaction_strength": inter,
            "novelty": self.novelty(a, b),
            "recognizability": self.recognizability(a, b),
        }
        score = sum(self.WEIGHTS[k] * v for k, v in fac.items())
        tpl = "competition" if (a.diet == b.diet) else "predation"
        return Candidate(
            template=tpl,
            entities=[a.ref, b.ref],
            environment=None,
            mode="historical",
            score=score,
            factors=fac,
        )

    def generate(self, top_n: int = 20) -> list[Candidate]:
        cands: list[Candidate] = []
        n = len(self.taxa)
        for i in range(n):
            for j in range(i + 1, n):
                c = self.score_pair(self.taxa[i], self.taxa[j])
                if c:
                    cands.append(c)
        cands.sort(key=lambda c: c.score, reverse=True)
        return cands[:top_n]
