"""Immutable ScenarioManifest (MVP Phase 11).

A scenario pins the exact world snapshot, participant reconstruction versions,
environment, relation basis, mode, validity, and model version. Its digest is
the simulation/story root.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from ..reconstruction.world import WorldSnapshot


@dataclass
class ScenarioManifest:
    """The immutable pin-set a scenario runs under."""

    scenario_id: str
    world_snapshot_digest: str
    participant_reconstructions: dict[str, str] = field(default_factory=dict)  # entity -> version
    environment_reconstruction: str = ""
    relation_basis: list[str] = field(default_factory=list)
    mode: str = "historical"  # historical | lab
    validity: str = "VALID"  # VALID | INVALID | COUNTERFACTUAL
    model_version: str = ""
    assumptions: dict[str, Any] = field(default_factory=dict)

    def digest(self) -> str:
        blob = json.dumps(
            {
                "scenario_id": self.scenario_id,
                "world_snapshot_digest": self.world_snapshot_digest,
                "participants": dict(sorted(self.participant_reconstructions.items())),
                "environment": self.environment_reconstruction,
                "relations": sorted(self.relation_basis),
                "mode": self.mode,
                "validity": self.validity,
                "model_version": self.model_version,
                "assumptions": self.assumptions,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(blob.encode()).hexdigest()

    @property
    def historical_proceeds(self) -> bool:
        """Historical content may only proceed if validity is established."""
        return self.validity == "VALID"


def build_scenario_manifest(
    scenario_id: str,
    world: WorldSnapshot,
    *,
    participant_reconstructions: dict[str, str] | None = None,
    environment_reconstruction: str = "",
    relation_basis: list[str] | None = None,
    mode: str = "historical",
    validity: str = "VALID",
    model_version: str = "",
    assumptions: dict[str, Any] | None = None,
) -> ScenarioManifest:
    return ScenarioManifest(
        scenario_id=scenario_id,
        world_snapshot_digest=world.digest(),
        participant_reconstructions=participant_reconstructions or {},
        environment_reconstruction=environment_reconstruction,
        relation_basis=relation_basis or [],
        mode=mode,
        validity=validity,
        model_version=model_version,
        assumptions=assumptions or {},
    )
