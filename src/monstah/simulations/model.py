"""SimulationModel classes (MVP Phase 12-13).

Monstah simulation branches into distinct model classes with different
epistemic standing. The Open5e/d20 engine is honestly a GAME_PROXY — it must
never drift into being "the prehistoric simulator." A SimulationRun pins its
scenario digest, model identity, seed, states, events, and outcome.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ModelClass(str, Enum):
    GAME_PROXY = "GAME_PROXY"
    MECHANISTIC_MODEL = "MECHANISTIC_MODEL"
    STATISTICAL_MODEL = "STATISTICAL_MODEL"
    GRAPH_MODEL = "GRAPH_MODEL"
    NO_SIMULATION = "NO_SIMULATION"


@dataclass
class SimulationModel:
    """Metadata + epistemic standing of a simulation model."""

    model_id: str
    model_version: str
    model_class: ModelClass
    scientific_status: str = "GAME_PROXY"  # honest label
    inputs: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)

    def describe(self) -> str:
        return f"{self.model_id} v{self.model_version} [{self.model_class.value}]"


@dataclass
class SimulationRun:
    """A pinned, replayable simulation run."""

    run_id: str
    scenario_digest: str
    model: SimulationModel
    seed: int
    initial_state: dict[str, Any] = field(default_factory=dict)
    events: list[dict] = field(default_factory=list)
    final_state: dict[str, Any] = field(default_factory=dict)
    outcome: str = ""

    def digest(self) -> str:
        blob = json.dumps(
            {
                "run_id": self.run_id,
                "scenario_digest": self.scenario_digest,
                "model": self.model.model_id,
                "model_version": self.model.model_version,
                "seed": self.seed,
                "events": [e.get("event_id") for e in self.events],
                "outcome": self.outcome,
            },
            sort_keys=True, separators=(",", ":"),
        )
        return hashlib.sha256(blob.encode()).hexdigest()


def game_proxy_model(version: str = "d20-2.5") -> SimulationModel:
    """The honest label for the current Open5e/d20 engine."""
    return SimulationModel(
        model_id="open5e-d20",
        model_version=version,
        model_class=ModelClass.GAME_PROXY,
        scientific_status="GAME_PROXY",
        inputs=["statblock:armor_class", "statblock:attack_bonus", "statblock:damage_dice"],
        assumptions=["D&D attack-vs-AC resolution is a game abstraction, not biomechanics"],
        outputs=["outcome_distribution", "canonical_event_log"],
    )
