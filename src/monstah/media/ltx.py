"""LTX renderer binding.

LTX is a replaceable renderer DOWNSTREAM of canonical project state. It must
never decide scientific truth. This module binds our pipeline's shots to the
LTX ShotSpec schema (see media/ltx/templates/shot-spec.schema.json), carrying
the epistemic `canonicality` from the truth layer through to the render.

The renderer abstraction keeps LTX-2.3 as the backend today and leaves a
future LTX-2.5 (or any renderer) swappable via RendererManifest.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Canonicality(str, Enum):
    """Epistemic status of a shot's content (must come from the truth layer)."""

    CANONICAL_EVENT = "CANONICAL_EVENT"
    RECONSTRUCTION = "RECONSTRUCTION"
    NARRATIVE_PROJECTION = "NARRATIVE_PROJECTION"
    COUNTERFACTUAL = "COUNTERFACTUAL"


class ControlMode(str, Enum):
    T2V = "T2V"
    I2V = "I2V"
    FIRST_LAST = "FIRST_LAST"
    KEYFRAME = "KEYFRAME"
    ICLORA = "ICLORA"
    RETAKE = "RETAKE"
    EXTEND = "EXTEND"


class Project(str, Enum):
    ROBOBLADEZ = "robobladez"
    MONSTAH = "monstah"
    OTHER = "other"


class ShotSpec(BaseModel):
    """A single renderable shot, JSON-serializable per the LTX schema."""

    shot_id: str
    project: Project = Project.MONSTAH
    canonicality: Canonicality = Canonicality.RECONSTRUCTION
    entity_versions: list[str] = Field(default_factory=list)
    environment_version: str | None = None
    event_ids: list[str] = Field(default_factory=list)
    prompt: str
    negative_prompt: str = ""
    duration_s: float = 6.0
    fps: int = 24
    aspect_ratio: str = "16:9"
    audio: dict[str, Any] = Field(default_factory=dict)
    camera: dict[str, Any] = Field(default_factory=dict)
    references: list[dict[str, Any]] = Field(default_factory=list)
    control_mode: ControlMode = ControlMode.I2V
    constraints: list[str] = Field(default_factory=list)
    qa: list[str] = Field(default_factory=list)


class RendererManifest(BaseModel):
    """Describes which renderer + backend produced the shots (replaceable)."""

    renderer_family: str = "ltx"
    renderer_version: str = "2.3"
    backend: str = "comfyui"
    model_variant: str = "ltx-2-3-fast"
    checkpoint_digest: str = ""
    workflow_id: str = ""
    workflow_version: str = ""
    seed: int = 0
    prompt_enhancement: bool = False
    output: dict[str, Any] = Field(
        default_factory=lambda: {"resolution": "1920x1080", "fps": 24, "generate_audio": True}
    )


@dataclass
class ShotBundle:
    """The render-ready output for one episode."""

    project: str
    manifest: RendererManifest
    shots: list[ShotSpec] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project": self.project,
            "manifest": self.manifest.model_dump(),
            "shots": [s.model_dump() for s in self.shots],
        }
