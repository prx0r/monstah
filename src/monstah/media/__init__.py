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
from .control import ControlFrameCompositor, ControlPlanner
from .ltx import Canonicality, ControlMode, Project, RendererManifest, ShotBundle, ShotBasis, ScenarioMode, ShotSpec as LtxShotSpec
from .providers import (
    BhlProvider,
    CanonicalAssetResolver,
    GbifImageProvider,
    ImageProvider,
    ImageResolver,
    INaturalistProvider,
    WikimediaProvider,
)
from .qa import (
    QAResult,
    ReconstructionConstraintSet,
    Verdict,
    binding_qa,
    epistemic_qa,
    event_qa,
    run_qa,
    visual_identity_qa,
)
from .renderer import LTX25ApiRenderer, OfflineRenderer, RendererBackend, RenderJob, default_renderer
from .scientific_renderer import ScientificRenderer
from .shot_spec2 import ShotControl, ShotSpecV2, ShotSubject, ShotBasis2
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
    "ControlFrameCompositor",
    "ControlMode",
    "ControlPlanner",
    "EntityVersion",
    "EpistemicStatus",
    "GbifImageProvider",
    "ImageProvider",
    "ImageResolver",
    "INaturalistProvider",
    "LTX25ApiRenderer",
    "LtxShotSpec",
    "OfflineRenderer",
    "Project",
    "R2Store",
    "RenderJob",
    "RendererBackend",
    "RendererManifest",
    "ScenarioMode",
    "ScientificRenderer",
    "ShotBasis",
    "ShotBasis2",
    "ShotBundle",
    "ShotControl",
    "ShotSpec",
    "ShotSpecV2",
    "ShotSubject",
    "WikimediaProvider",
    "canonicality_for_mode",
    "compile_shots",
    "default_renderer",
    "license_tier",
    "license_usability",
    "to_ltx_shots",
]
