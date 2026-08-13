"""CanonicalAsset registry — immutable, content-addressed (MVP Phase 9).

The rendering layer asks `canonical_assets.resolve(entity_id, version, view)`,
never `find_some_image("Tyrannosaurus")`. Each approved asset is immutable and
content-hashed; changes supersede rather than mutate.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .image_backend import ImageCandidate


class AssetStatus(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    SUPERSEDED = "SUPERSEDED"


@dataclass
class CanonicalAsset:
    """An immutable, approved visual reconstruction asset."""

    asset_id: str
    entity_id: str
    reconstruction_version: str
    visual_version: str
    view: str
    role: str
    file_sha256: str
    reference_pack_id: str = ""
    generator_manifest: dict[str, Any] = field(default_factory=dict)
    status: AssetStatus = AssetStatus.DRAFT
    supersedes: str | None = None

    @classmethod
    def from_candidate(
        cls,
        candidate: ImageCandidate,
        *,
        entity_id: str,
        reconstruction_version: str,
        visual_version: str,
        reference_pack_id: str = "",
        role: str = "CANONICAL_RECONSTRUCTION",
    ) -> "CanonicalAsset":
        return cls(
            asset_id=f"asset:{entity_id}:{visual_version}:{candidate.view}:{candidate.sha256()[:10]}",
            entity_id=entity_id,
            reconstruction_version=reconstruction_version,
            visual_version=visual_version,
            view=candidate.view,
            role=role,
            file_sha256=candidate.sha256(),
            reference_pack_id=reference_pack_id,
            generator_manifest=candidate.generator_manifest,
        )


class CanonicalAssetRegistry:
    """Immutable store: assets are added, superseded, never mutated."""

    def __init__(self) -> None:
        self._by_key: dict[tuple[str, str], CanonicalAsset] = {}

    def register(self, asset: CanonicalAsset) -> CanonicalAsset:
        # supersede the current approved asset for this entity+view (any visual version)
        key = (asset.entity_id, asset.view)
        existing = self._by_key.get(key)
        if existing and existing.status is AssetStatus.APPROVED:
            existing.status = AssetStatus.SUPERSEDED
            asset.supersedes = existing.asset_id
        asset.status = AssetStatus.APPROVED
        self._by_key[key] = asset
        return asset

    def resolve(self, entity_id: str, reconstruction_version: str, view: str) -> CanonicalAsset | None:
        """The canonical render lookup. Returns only APPROVED assets."""
        a = self._by_key.get((entity_id, view))
        if a and a.status is AssetStatus.APPROVED:
            return a
        return None
