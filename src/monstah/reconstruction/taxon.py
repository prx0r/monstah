"""TaxonReconstruction and EnvironmentReconstruction (MVP Phase 2).

Both wrap a `ReconstructionVersion` and add domain-specific parameters. LTX may
only receive an APPROVED reconstruction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .versioning import ReconstructionStatus, ReconstructionVersion


@dataclass
class TaxonReconstruction:
    entity_id: str
    version: ReconstructionVersion
    morphology: dict[str, Any] = field(default_factory=dict)  # skull/torso/limbs/tail/integument
    dimensions: dict[str, Any] = field(default_factory=dict)  # body_length/hip_height
    appearance: dict[str, Any] = field(default_factory=dict)  # constrained/inferred/open/speculative

    @property
    def approved_for_render(self) -> bool:
        return self.version.usable_for_render


@dataclass
class EnvironmentReconstruction:
    environment_id: str
    version: ReconstructionVersion
    composition: dict[str, Any] = field(default_factory=dict)  # geology/flora/fauna/climate
    views: dict[str, Any] = field(default_factory=dict)  # wide/low-ground/river/vegetation/atmosphere

    @property
    def approved_for_render(self) -> bool:
        return self.version.usable_for_render
