"""Visual reconstruction specs (MVP Phase 4, 7, 8).

A machine-readable reconstruction spec is the source of truth for image
generation; a provider-specific prompt is derived FROM it, never stored as truth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Certainty(str, Enum):
    CONSTRAINED = "CONSTRAINED"
    INFERRED = "INFERRED"
    RECONSTRUCTED = "RECONSTRUCTED"
    OPEN = "OPEN"
    SPECULATIVE = "SPECULATIVE"


@dataclass
class VisualReconstructionSpec:
    """What an approved reconstruction must look like (machine-readable)."""

    entity_id: str
    reconstruction_id: str
    reference_pack_id: str = ""
    morphology: dict[str, Any] = field(default_factory=dict)  # skull/torso/limbs/tail/integument
    dimensions: dict[str, Any] = field(default_factory=dict)  # body_length/hip_height
    appearance: dict[str, Any] = field(default_factory=dict)  # trait -> Certainty
    required_views: list[str] = field(default_factory=lambda: ["lateral", "three_quarter", "front", "dorsal"])
    forbidden: list[str] = field(default_factory=list)

    def allowed_to_claim(self, trait: str) -> bool:
        """Certainty policy: what the media may assert about a trait."""
        return self.appearance.get(trait, Certainty.OPEN) in (
            Certainty.CONSTRAINED,
            Certainty.INFERRED,
            Certainty.RECONSTRUCTED,
        )


@dataclass
class EnvironmentVisualSpec:
    """Canonical environment reconstruction spec."""

    environment_id: str
    reconstruction_id: str
    composition: dict[str, Any] = field(default_factory=dict)  # geology/flora/fauna/climate
    views: dict[str, Any] = field(default_factory=dict)  # wide/low-ground/river/vegetation/atmosphere
    reference_pack_id: str = ""
    forbidden: list[str] = field(default_factory=list)
