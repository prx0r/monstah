"""Reconstruction package: versioned models of worlds, taxa, environments.

Per MVP guide: Sources → Claims → Assertions → Reconstruction → WorldSnapshot.
LTX may only receive an APPROVED reconstruction.
"""

from .taxon import EnvironmentReconstruction, TaxonReconstruction
from .versioning import (
    ReconstructionRegistry,
    ReconstructionStatus,
    ReconstructionVersion,
    bump_version,
)
from .world import (
    SnapshotEntity,
    SnapshotEnvironment,
    SnapshotRelation,
    SpatialExtent,
    TemporalExtent,
    WorldSnapshot,
    build_world_snapshot,
    snapshot_from_manifest,
)

__all__ = [
    "EnvironmentReconstruction",
    "ReconstructionRegistry",
    "ReconstructionStatus",
    "ReconstructionVersion",
    "SnapshotEntity",
    "SnapshotEnvironment",
    "SnapshotRelation",
    "SpatialExtent",
    "TemporalExtent",
    "TaxonReconstruction",
    "WorldSnapshot",
    "build_world_snapshot",
    "bump_version",
    "snapshot_from_manifest",
]
