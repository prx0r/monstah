"""Reconstruction versioning + lifecycle (MVP Phase 2).

Key rule: **LTX may only receive an APPROVED reconstruction.** Not a raw
evidence bundle, not a draft, not merely "R1".
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ReconstructionStatus(str, Enum):
    DRAFT = "DRAFT"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    SUPERSEDED = "SUPERSEDED"


@dataclass
class ReconstructionVersion:
    """A versioned reconstruction of an entity or environment."""

    entity: str  # entity_id or environment_id
    version: str
    basis_assertions: list[str] = field(default_factory=list)
    derivation_method: str = ""
    assumptions: dict[str, Any] = field(default_factory=dict)
    uncertainties: dict[str, Any] = field(default_factory=dict)
    supersedes: str | None = None
    status: ReconstructionStatus = ReconstructionStatus.DRAFT

    def mark(self, status: ReconstructionStatus) -> "ReconstructionVersion":
        if status == ReconstructionStatus.APPROVED and self.status is not ReconstructionStatus.APPROVED:
            if self.status is not ReconstructionStatus.REVIEWED:
                raise ValueError("a reconstruction must be REVIEWED before it can be APPROVED")
        self.status = status
        return self

    @property
    def usable_for_render(self) -> bool:
        """LTX may only receive an APPROVED reconstruction."""
        return self.status is ReconstructionStatus.APPROVED

    def digest(self) -> str:
        """Stable identity over the reconstruction's evidence basis."""
        blob = json.dumps(
            {
                "entity": self.entity,
                "version": self.version,
                "basis_assertions": sorted(self.basis_assertions),
                "derivation_method": self.derivation_method,
                "assumptions": self.assumptions,
                "supersedes": self.supersedes,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(blob.encode()).hexdigest()


class ReconstructionRegistry:
    """Versioned store per entity: current + superseded versions."""

    def __init__(self) -> None:
        self._by_entity: dict[str, dict[str, ReconstructionVersion]] = {}

    def put(self, rec: ReconstructionVersion) -> None:
        versions = self._by_entity.setdefault(rec.entity, {})
        if versions and rec.supersedes is None:
            # auto-supersede the current head
            current = self.head(rec.entity)
            if current and current.status is not ReconstructionStatus.SUPERSEDED:
                current.status = ReconstructionStatus.SUPERSEDED
                rec.supersedes = current.version
        versions[rec.version] = rec

    def get(self, entity: str, version: str) -> ReconstructionVersion | None:
        return self._by_entity.get(entity, {}).get(version)

    def head(self, entity: str) -> ReconstructionVersion | None:
        versions = self._by_entity.get(entity, {})
        if not versions:
            return None
        return max(versions.values(), key=lambda v: _version_key(v.version))

    def all(self, entity: str) -> list[ReconstructionVersion]:
        return sorted(self._by_entity.get(entity, {}).values(), key=lambda v: _version_key(v.version))


def _version_key(v: str) -> int:
    import re

    m = re.search(r"(\d+)$", v)
    return int(m.group(1)) if m else 0


def bump_version(version: str) -> str:
    import re

    m = re.search(r"(\d+)$", version)
    if not m:
        return f"{version}1"
    return version[: m.start()] + str(int(m.group(1)) + 1)
