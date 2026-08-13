"""Claim-aware StoryBeat (MVP Phase 14).

A beat can never blur "fossil evidence says X" with "simulation predicts Y".
Every beat carries its shot basis and the exact events/assertions/reconstructions/
narrative-claims it rests on.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class BeatKind(str, Enum):
    SOURCE_FACT = "SOURCE_FACT"
    RECONSTRUCTION = "RECONSTRUCTION"
    GRAPH_RELATION = "GRAPH_RELATION"
    SIMULATION_RESULT = "SIMULATION_RESULT"
    EDITORIAL_BRIDGE = "EDITORIAL_BRIDGE"
    UNCERTAINTY = "UNCERTAINTY"


@dataclass
class StoryBeat:
    beat_id: str
    kind: BeatKind
    text: str
    shot_basis: str = "RECONSTRUCTION"
    basis_event_ids: list[str] = field(default_factory=list)
    basis_assertion_ids: list[str] = field(default_factory=list)
    basis_reconstruction_ids: list[str] = field(default_factory=list)
    narrative_claim_ids: list[str] = field(default_factory=list)
    importance: float = 0.5

    @property
    def grounded(self) -> bool:
        """A beat must be grounded in something it is allowed to claim."""
        if self.kind in (BeatKind.EDITORIAL_BRIDGE, BeatKind.UNCERTAINTY):
            return True  # bridges/uncertainty may be ungrounded by design
        return bool(
            self.basis_event_ids or self.basis_assertion_ids
            or self.basis_reconstruction_ids or self.narrative_claim_ids
        )
