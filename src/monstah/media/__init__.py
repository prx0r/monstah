"""Media package: LTX renderer binding, storage (R2), shot compilation."""

from .ltx import Canonicality, ControlMode, Project, RendererManifest, ShotBundle, ShotSpec as LtxShotSpec
from .shots import (
    EntityVersion,
    ShotSpec,
    canonicality_for_mode,
    compile_shots,
    to_ltx_shots,
)
from .storage import R2Store

__all__ = [
    "Canonicality",
    "ControlMode",
    "EntityVersion",
    "LtxShotSpec",
    "Project",
    "R2Store",
    "RendererManifest",
    "ShotBundle",
    "ShotSpec",
    "canonicality_for_mode",
    "compile_shots",
    "to_ltx_shots",
]
