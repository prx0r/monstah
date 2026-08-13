"""ShotSpec v2 — every shot states why it exists (MVP Phase 17).

Extends the epistemic basis to bind assertions, reconstructions, and events,
plus explicit control inputs (first/last frame, guide). Deterministic
ScientificRenderer graphics are also first-class shot subjects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..media.ltx import ShotBasis


@dataclass
class ShotBasis2:
    type: ShotBasis = ShotBasis.RECONSTRUCTION
    assertion_ids: list[str] = field(default_factory=list)
    reconstruction_ids: list[str] = field(default_factory=list)
    event_ids: list[str] = field(default_factory=list)


@dataclass
class ShotSubject:
    entity_id: str
    reconstruction_version: str = "R1"
    canonical_visual_assets: list[str] = field(default_factory=list)


@dataclass
class ShotControl:
    preferred: str = "I2V"
    first_frame: str = ""  # uri of first-frame plate
    last_frame: str = ""
    guide: str = ""  # depth/motion guide uri


@dataclass
class ShotSpecV2:
    shot_id: str
    basis: ShotBasis2 = field(default_factory=ShotBasis2)
    subjects: list[ShotSubject] = field(default_factory=list)
    environment: dict[str, Any] = field(default_factory=dict)  # reconstruction_version + canonical_assets
    camera: str = "low tracking"
    prompt: str = ""
    duration: float = 6.0
    control: ShotControl = field(default_factory=ShotControl)
    constraints: list[str] = field(default_factory=list)
    qa: list[str] = field(default_factory=list)

    @property
    def grounded(self) -> bool:
        return bool(self.basis.event_ids or self.basis.assertion_ids or self.basis.reconstruction_ids)

    def is_deterministic(self) -> bool:
        """Data graphics (maps/timelines/confidence) are deterministic, not LTX."""
        return self.control.preferred == "DETERMINISTIC"
