"""Media package: assets, storage (R2), shot compilation."""

from .shots import EntityVersion, ShotSpec, compile_shots
from .storage import R2Store

__all__ = ["EntityVersion", "R2Store", "ShotSpec", "compile_shots"]
