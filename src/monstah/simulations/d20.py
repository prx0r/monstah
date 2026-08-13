"""d20 combat resolution (adapted from D&D 5e / Open5e statblocks).

Reuses the mature SRD/OGL attack-vs-AC resolution model instead of hand-tuned
weights:

    hit roll    : d20 + attack_bonus   >= armor_class  (nat 20 auto-hit)
    damage      : damage_dice  (e.g. "3d8+5")
    pool        : hit_points  -> 0  =  killed

This mirrors Open5e `actions[].attack_bonus` + `actions[].damage_dice` against
`armor_class`. Deterministic: everything is driven by a seeded NumPy generator.
"""

from __future__ import annotations

import re
from typing import Any

import numpy as np

_DICE_RE = re.compile(r"(\d+)d(\d+)([+-]\d+)?")


def parse_dice(dice: str) -> tuple[int, int, int]:
    """'3d8+5' -> (num=3, sides=8, mod=+5). Returns (1,6,0) on failure."""
    m = _DICE_RE.match(dice.strip())
    if not m:
        return 1, 6, 0
    return int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)


def attack_roll(
    rng: np.random.Generator,
    attack_bonus: int,
    armor_class: int,
    n: int,
) -> np.ndarray:
    """Vectorized hit checks: return boolean array of hits (n trials)."""
    roll = rng.integers(1, 21, size=n, dtype=np.int64)
    crit = roll == 20
    hit = (roll + attack_bonus) >= armor_class
    return hit | crit


def damage_vec(
    rng: np.random.Generator,
    dice: str,
    n: int,
    *,
    critical_only: np.ndarray | None = None,
) -> np.ndarray:
    """Vectorized damage for a dice string; doubles dice on criticals."""
    num, sides, mod = parse_dice(dice)
    base = rng.integers(1, sides + 1, size=(n, num), dtype=np.int64).sum(axis=1)
    if critical_only is not None:
        base = base + base * critical_only
    return base + mod


class Combatant:
    """A statblock-derived combatant (Open5e schema)."""

    __slots__ = ("name", "ref", "armor_class", "hit_points", "attack_bonus",
                 "damage_dice", "speed", "stamina", "perception", "diet")

    def __init__(self, stats: dict) -> None:
        self.name = stats.get("name", "combatant")
        self.ref = stats.get("ref")
        self.armor_class = int(stats.get("armor_class", 10))
        self.hit_points = int(stats.get("hit_points", 30))
        self.attack_bonus = int(stats.get("attack_bonus", 0))
        self.damage_dice = stats.get("damage_dice", "1d6")
        self.speed = float(stats.get("speed", 8.0))
        self.stamina = float(stats.get("stamina", 10.0))
        self.perception = float(stats.get("perception", 60.0))
        self.diet = stats.get("diet", "carnivore")

    @classmethod
    def from_open5e(cls, mon: dict, attack_bonus: int = 0) -> "Combatant":
        """Build from a raw Open5e statblock (picks first damaging action)."""
        dice = "1d6"
        ab = attack_bonus
        db = 0
        for action in mon.get("actions", []) or []:
            dmg = action.get("damage_dice")
            if dmg:
                dice = dmg
                ab = int(action.get("attack_bonus", ab or 0))
                db = int(action.get("damage_bonus", 0))
                break
        if db:
            if re.search(r"[+-]\d+$", dice):
                pass  # dice already carries a mod
            else:
                dice = f"{dice}+{db}"
        hp_dice = mon.get("hit_dice", "")
        stamina = 10.0
        if isinstance(hp_dice, str):
            m = re.match(r"(\d+)d", hp_dice)
            if m:
                stamina = float(m.group(1)) / 3.0
        speed = 8.0
        sp = mon.get("speed")
        if isinstance(sp, dict):
            speed = float(sp.get("walk", 30)) / 4.0
        elif isinstance(sp, (int, float)):
            speed = float(sp) / 4.0
        return cls(
            {
                "name": mon.get("name", "combatant"),
                "armor_class": mon.get("armor_class", 10),
                "hit_points": mon.get("hit_points", 30),
                "attack_bonus": ab,
                "damage_dice": dice,
                "speed": speed,
                "stamina": stamina,
                "perception": 60.0,
                "diet": "herbivore",
            }
        )


def resolve_duel(
    attacker: Combatant,
    defender: Combatant,
    rng: np.random.Generator,
    *,
    n_rounds: int = 5,
) -> np.ndarray:
    """Simulate `n_rounds` attack rounds (attacker strikes each round).

    Vectorized over rounds. Returns remaining defender HP vector.
    """
    damage = np.zeros(n_rounds, dtype=np.int64)
    dmg = damage_vec(rng, attacker.damage_dice, n_rounds)
    hit = attack_roll(rng, attacker.attack_bonus, defender.armor_class, n_rounds)
    damage[hit] = dmg[hit]
    hp = defender.hit_points - np.cumsum(damage)
    return hp


def run_duel_events(
    attacker: Combatant,
    defender: Combatant,
    rng: np.random.Generator,
    *,
    n_rounds: int = 5,
) -> list[dict]:
    """Emit the canonical event log of one duel (real sim events, not fabricated).

    Returns per-round events: hits/misses with damage and HP, plus the resolved
    outcome. This is the SIMULATION -> EVENT link the shot graph consumes.
    """
    events: list[dict] = []
    hp = defender.hit_points
    for r in range(n_rounds):
        hit = attack_roll(rng, attacker.attack_bonus, defender.armor_class, 1)[0]
        if hit:
            dmg = int(damage_vec(rng, attacker.damage_dice, 1)[0])
            hp = max(0, hp - dmg)
            events.append(
                {
                    "t": float(r),
                    "actor": attacker.name,
                    "action": "ATTACK",
                    "detail": f"hits {defender.name} for {dmg} (hp {hp})",
                }
            )
        else:
            events.append(
                {"t": float(r), "actor": attacker.name, "action": "ATTACK", "detail": f"misses {defender.name}"}
            )
        if hp <= 0:
            events.append(
                {"t": float(r + 0.5), "actor": attacker.name, "action": "FEED", "detail": f"{defender.name} defeated"}
            )
            break
    if hp > 0:
        events.append(
            {"t": float(n_rounds), "actor": "system", "action": "DISENGAGE", "detail": f"{defender.name} survives"}
        )
    return events
