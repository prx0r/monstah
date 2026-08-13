"""Simulations package."""

from .d20 import Combatant, attack_roll, damage_vec, parse_dice, resolve_duel
from .ecs_battle import build_entities, run_battle
from .encounter import ACTIONS, Participant, SimEvent, build_run, resolve_outcome, run_encounter
from .montecarlo import MCResult, run_monte_carlo

__all__ = [
    "ACTIONS",
    "Combatant",
    "MCResult",
    "Participant",
    "SimEvent",
    "attack_roll",
    "build_entities",
    "build_run",
    "damage_vec",
    "parse_dice",
    "resolve_duel",
    "resolve_outcome",
    "run_battle",
    "run_encounter",
    "run_monte_carlo",
]
