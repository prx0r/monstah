"""Media package: LTX renderer, canonical assets, image providers, storage."""

from .asset import (
    ALLOWED_LICENSES,
    AssetCandidate,
    AssetPack,
    AssetRole,
    EpistemicStatus,
    license_tier,
    license_usability,
)
from .ltx import Canonicality, ControlMode, Project, RendererManifest, ShotBundle, ShotSpec as LtxShotSpec
from .providers import (
    BhlProvider,
    CanonicalAssetResolver,
    GbifImageProvider,
    ImageProvider,
    ImageResolver,
    INaturalistProvider,
    WikimediaProvider,
)
from .shots import (
    EntityVersion,
    ShotSpec,
    canonicality_for_mode,
    compile_shots,
    to_ltx_shots,
)
from .storage import R2Store

__all__ = [
    "ALLOWED_LICENSES",
    "AssetCandidate",
    "AssetPack",
    "AssetRole",
    "BhlProvider",
    "CanonicalAssetResolver",
    "Canonicality",
    "ControlMode",
    "EntityVersion",
    "EpistemicStatus",
    "GbifImageProvider",
    "ImageProvider",
    "ImageResolver",
    "INaturalistProvider",
    "LtxShotSpec",
    "Project",
    "R2Store",
    "RendererManifest",
    "ShotBundle",
    "ShotSpec",
    "WikimediaProvider",
    "canonicality_for_mode",
    "compile_shots",
    "license_tier",
    "license_usability",
    "to_ltx_shots",
]
