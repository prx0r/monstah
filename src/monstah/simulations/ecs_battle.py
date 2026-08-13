"""esper-based battle simulation.

Uses esper (MIT, pure-Python ECS) as the ENTITY backbone. Entities are plain
int IDs; combat stats are components (pure data); systems hold all logic and
run in a fixed per-tick order, giving a deterministic, tick-driven battle loop
that mirrors D&D initiative/action economy. Combat resolution reuses the d20
model (attack roll vs AC, damage dice) from `d20.py`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import esper
import numpy as np

from ..core.models import Reference
from .d20 import Combatant, attack_roll, damage_vec


# --- Components (pure data) --------------------------------------------------
@dataclass
class Stats:
    name: str
    ref: Reference | None = None
    armor_class: int = 10
    hit_points: int = 30
    max_hp: int = 30
    attack_bonus: int = 0
    damage_dice: str = "1d6"
    speed: float = 8.0
    stamina: float = 10.0
    diet: str = "carnivore"


@dataclass
class Position:
    x: float = 0.0
    y: float = 0.0


@dataclass
class Target:
    entity_id: int | None = None


@dataclass
class Alive:
    hp: int = 30


@dataclass
class Team:
    label: str = "A"


# --- Events emitted by systems ----------------------------------------------
@dataclass
class CombatEvent:
    t: float
    actor: str
    action: str
    detail: str = ""
    payload: dict = field(default_factory=dict)


def build_entities(combatants: list[Combatant]) -> list[int]:
    """Register combatants as ECS entities (Stats + Alive + Team)."""
    ids = []
    for i, c in enumerate(combatants):
        e = esper.create_entity()
        esper.add_component(e, Stats(
            name=c.name,
            ref=c.ref,
            armor_class=c.armor_class,
            hit_points=c.hit_points,
            max_hp=c.hit_points,
            attack_bonus=c.attack_bonus,
            damage_dice=c.damage_dice,
            speed=c.speed,
            stamina=c.stamina,
            diet=c.diet,
        ))
        esper.add_component(e, Alive(hp=c.hit_points))
        esper.add_component(e, Team(label="A" if i % 2 == 0 else "B"))
        ids.append(e)
    return ids


class AttackSystem(esper.Processor):
    """Each tick, every combatant on team A attacks team B using the d20 model.

    Runs in fixed order; updates Alive.hp in place so the battle is deterministic.
    """

    def __init__(self, rng: np.random.Generator, events: list[CombatEvent], tick: float = 1.0) -> None:
        self.rng = rng
        self.events = events
        self.tick = tick
        self.t = 0.0

    def process(self) -> None:
        self.t += self.tick
        attackers = [(e, s, a) for e, (s, a) in esper.get_components(Stats, Alive) if a.hp > 0]
        targets = [(e, s, a) for e, (s, a) in esper.get_components(Stats, Alive) if a.hp > 0]
        for a_e, a_s, a_a in attackers:
            if a_a.hp <= 0:
                continue
            # target the lowest-hp living enemy (simple heuristic)
            alive = [t for t in targets if t[2].hp > 0]
            if not alive:
                break
            t_e, t_s, t_a = min(alive, key=lambda t: t[2].hp)
            hit = attack_roll(self.rng, a_s.attack_bonus, t_s.armor_class, 1)[0]
            if hit:
                dmg = int(damage_vec(self.rng, a_s.damage_dice, 1)[0])
                t_a.hp = max(0, t_a.hp - dmg)
                self.events.append(CombatEvent(
                    t=self.t, actor=a_s.name, action="ATTACK",
                    detail=f"hits {t_s.name} for {dmg} (hp {t_a.hp})",
                ))
            else:
                self.events.append(CombatEvent(
                    t=self.t, actor=a_s.name, action="ATTACK",
                    detail=f"misses {t_s.name}",
                ))


def run_battle(
    a: Combatant,
    b: Combatant,
    rng: np.random.Generator,
    *,
    max_ticks: int = 60,
) -> tuple[str, list[CombatEvent]]:
    """Run an esper battle to resolution. Returns (outcome, event log).

    esper 3.8 uses a module-level current world; each battle runs in its own
    uniquely-named world so runs never contaminate each other.
    """
    import uuid

    world_name = f"battle_{uuid.uuid4().hex[:8]}"
    esper.switch_world(world_name)
    try:
        ids = build_entities([a, b])
        events: list[CombatEvent] = []
        system = AttackSystem(rng, events, tick=1.0)
        esper.add_processor(system)

        for _ in range(max_ticks):
            esper.process()
            living = [e for e, (s, al) in esper.get_components(Stats, Alive) if al.hp > 0]
            if len(living) <= 1:
                break
        # resolve outcome
        alive = [e for e, (s, al) in esper.get_components(Stats, Alive) if al.hp > 0]
        a_alive = any(esper.component_for_entity(e, Stats).name == a.name for e in alive)
        b_alive = any(esper.component_for_entity(e, Stats).name == b.name for e in alive)
        if a_alive and not b_alive:
            outcome = "attacker_wins"
        elif b_alive and not a_alive:
            outcome = "defender_wins"
        elif a_alive and b_alive:
            outcome = "disengagement"
        else:
            outcome = "mutual_destruction"
        return outcome, events
    finally:
        esper.switch_world("__base__")
        esper.delete_world(world_name)
