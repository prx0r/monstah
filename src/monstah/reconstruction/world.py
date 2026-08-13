"""WorldSnapshot — the immutable statement of "which world did we reconstruct?"

Hierarchy:
    Sources → Claims → Assertions → Reconstruction → WorldSnapshot

A WorldSnapshot aggregates one world's versioned reconstructions and their
evidence, and produces a STABLE digest. Given the same persisted evidence
versions the digest is identical; changing any reconstruction version changes it.
This is the canonical input to discovery/media.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from ..core.models import Reference


@dataclass
class TemporalExtent:
    min_ma: float | None = None
    max_ma: float | None = None


@dataclass
class SpatialExtent:
    geometry_ref: str = ""
    paleocoordinates: dict[str, Any] = field(default_factory=dict)


@dataclass
class SnapshotEntity:
    """An entity in the world, bound to a specific reconstruction + its assertions."""

    entity_id: str
    reconstruction_id: str
    reconstruction_version: str
    assertion_ids: list[str] = field(default_factory=list)


@dataclass
class SnapshotEnvironment:
    reconstruction_id: str = ""
    reconstruction_version: str = ""
    assertion_ids: list[str] = field(default_factory=list)


@dataclass
class SnapshotRelation:
    relation_id: str = ""
    assertion_ids: list[str] = field(default_factory=list)


@dataclass
class WorldSnapshot:
    """Immutable statement of a reconstructed world + its evidence closure."""

    world_id: str
    world_version: str = "R1"
    temporal_extent: TemporalExtent = field(default_factory=TemporalExtent)
    spatial_extent: SpatialExtent = field(default_factory=SpatialExtent)
    environment: SnapshotEnvironment = field(default_factory=SnapshotEnvironment)
    entities: list[SnapshotEntity] = field(default_factory=list)
    relations: list[SnapshotRelation] = field(default_factory=list)
    uncertainty_summary: dict[str, Any] = field(default_factory=dict)

    def evidence_closure(self) -> dict[str, Any]:
        """The exact inputs that determine identity (sorted, for stable digest)."""
        return {
            "world_id": self.world_id,
            "world_version": self.world_version,
            "temporal": {"min_ma": self.temporal_extent.min_ma, "max_ma": self.temporal_extent.max_ma},
            "environment": {
                "reconstruction_version": self.environment.reconstruction_version,
                "assertion_ids": sorted(self.environment.assertion_ids),
            },
            "entities": sorted(
                [
                    {
                        "entity_id": e.entity_id,
                        "reconstruction_version": e.reconstruction_version,
                        "assertion_ids": sorted(e.assertion_ids),
                    }
                    for e in self.entities
                ],
                key=lambda x: x["entity_id"],
            ),
            "relations": sorted([r.relation_id for r in self.relations]),
        }

    def digest(self) -> str:
        """Stable content hash. Same evidence versions -> same digest."""
        blob = json.dumps(self.evidence_closure(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode()).hexdigest()


def build_world_snapshot(
    world_id: str,
    *,
    entities: list[SnapshotEntity],
    environment: SnapshotEnvironment | None = None,
    temporal_extent: TemporalExtent | None = None,
    spatial_extent: SpatialExtent | None = None,
    relations: list[SnapshotRelation] | None = None,
    world_version: str = "R1",
    uncertainty_summary: dict[str, Any] | None = None,
) -> WorldSnapshot:
    return WorldSnapshot(
        world_id=world_id,
        world_version=world_version,
        temporal_extent=temporal_extent or TemporalExtent(),
        spatial_extent=spatial_extent or SpatialExtent(),
        environment=environment or SnapshotEnvironment(),
        entities=entities,
        relations=relations or [],
        uncertainty_summary=uncertainty_summary or {},
    )


def snapshot_from_manifest(
    world_id: str,
    entities: dict[str, Reference],
    versions: dict[str, str],
    assertions: dict[str, list],
) -> WorldSnapshot:
    """Aggregate a channel manifest into a WorldSnapshot.

    `entities`: entity_key -> Reference
    `versions`: entity_key -> reconstruction version
    `assertions`: entity_key -> list[Assertion]
    """
    snapshot_entities: list[SnapshotEntity] = []
    for key, ref in entities.items():
        ver = versions.get(key, "R1")
        a_ids = [a.id for a in assertions.get(key, [])]
        snapshot_entities.append(
            SnapshotEntity(
                entity_id=ref.uri,
                reconstruction_id=f"recon:{key}:{ver}",
                reconstruction_version=ver,
                assertion_ids=a_ids,
            )
        )
    return build_world_snapshot(
        world_id=world_id,
        entities=snapshot_entities,
        temporal_extent=TemporalExtent(min_ma=0.0, max_ma=0.0),
    )
