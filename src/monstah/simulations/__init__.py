"""Simulations package.

The shared battle engine. d20 combat resolution (Open5e/SRD statblocks) is the
production engine; esper ECS provides an alternative tick-driven system for
multi-party or behavioral battles. The old hand-tuned utility-AI encounter
model was removed (superseded by d20).
"""

from .d20 import Combatant, attack_roll, damage_vec, parse_dice, resolve_duel, run_duel_events
from .ecs_battle import build_entities, run_battle
from .model import ModelClass, SimulationModel, SimulationRun, game_proxy_model
from .montecarlo import MCResult, replay, run_monte_carlo, run_rng

__all__ = [
    "Combatant",
    "MCResult",
    "ModelClass",
    "SimulationModel",
    "SimulationRun",
    "attack_roll",
    "build_entities",
    "damage_vec",
    "game_proxy_model",
    "parse_dice",
    "replay",
    "resolve_duel",
    "run_battle",
    "run_duel_events",
    "run_monte_carlo",
    "run_rng",
]
