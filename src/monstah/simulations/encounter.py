"""Simple utility-AI encounter simulation (§19).

Each participant is a capability model (mass, speed, bite force, stamina,
perception radius, diet...). Behavior is decided by utility scoring over a
small action set. Produces a deterministic event log given a seed.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable

from ..core.models import Reference, SimulationRun

ACTIONS = (
    "APPROACH",
    "RETREAT",
    "CHASE",
    "AMBUSH",
    "ATTACK",
    "DEFEND",
    "FEED",
    "REST",
    "REPOSITION",
    "SEEK_COVER",
)


@dataclass
class Participant:
    ref: Reference
    name: str
    diet: str = "herbivore"
    mass_kg: float = 1000.0
    speed: float = 8.0          # m/s
    bite_force: float = 500.0   # N
    stamina: float = 10.0       # units of endurance
    perception: float = 100.0   # m detection radius
    defence: float = 0.3        # 0..1 armour
    agility: float = 0.5        # turning/evasion


@dataclass
class SimEvent:
    t: float
    actor: str
    action: str
    detail: str = ""
    payload: dict = field(default_factory=dict)


def _utility(participant: Participant, dist: float, state: dict) -> dict[str, float]:
    """Return action -> utility, a naive but deterministic utility AI."""
    predator = participant.diet == "carnivore"
    injured = state.get(f"{participant.name}:hp", 1.0) < 0.5
    stamina_frac = state.get(f"{participant.name}:stamina", participant.stamina) / max(1, participant.stamina)
    u = {}
    u["REST"] = (1.0 - stamina_frac) * 2.0
    u["SEEK_COVER"] = 0.1
    u["RETREAT"] = (injured and not predator) * 1.5
    if predator:
        reach = max(1.0, min(10.0, participant.mass_kg / 800.0))
        u["CHASE"] = 1.0 - dist / max(1.0, participant.perception)
        u["AMBUSH"] = 0.15  # setup behavior, never outranks an active chase
        # attack clearly dominates once within reach, so the tie never
        # leaves the predator looping in chase.
        u["ATTACK"] = u["CHASE"] + (2.0 if dist <= reach else 0.0)
    else:
        u["APPROACH"] = 0.2
        u["DEFEND"] = dist < 15.0
    # prefer the max
    best = max(u, key=lambda k: u[k])
    return {k: (v if k == best else 0.0) for k, v in u.items()}


def run_encounter(
    predator: Participant,
    prey: Participant,
    *,
    seed: int = 1,
    max_steps: int = 200,
    dt: float = 0.5,
    nudge: Callable[[dict], dict] | None = None,
) -> list[SimEvent]:
    """Step an encounter until resolution (contact/escape/stamina) or time out."""
    rng = random.Random(seed)
    state = {
        f"{predator.name}:hp": 1.0,
        f"{prey.name}:hp": 1.0,
        f"{predator.name}:stamina": predator.stamina,
        f"{prey.name}:stamina": prey.stamina,
        "dist": rng.uniform(predator.perception * 0.6, predator.perception * 0.9),
        "running": True,
    }
    if nudge:
        state.update(nudge(state))
    events: list[SimEvent] = []
    t = 0.0
    prey_escaped = False
    caught = False

    for _ in range(max_steps):
        t += dt
        if not state["running"]:
            break
        # distances change per frame
        dist = state["dist"]
        for actor, p in ((predator, predator), (prey, prey)):
            util = _utility(p, dist, state)
            action = max(util, key=lambda k: util[k])
            ev = SimEvent(t=t, actor=p.name, action=action)
            if action == "CHASE":
                new_dist = max(1.0, dist - p.speed * dt * 0.6)
                state["dist"] = new_dist
                state[f"{p.name}:stamina"] -= 0.3 * dt
                ev.detail = f"gap closes to {new_dist:.0f}m"
            elif action == "RETREAT" and p is prey:
                new_dist = dist + p.speed * dt * 0.8
                state["dist"] = new_dist
                ev.detail = f"gap widens to {new_dist:.0f}m"
            elif action == "ATTACK":
                reach = max(1.0, min(10.0, p.mass_kg / 800.0))
                if dist < reach:
                    dmg = p.bite_force / 5000.0 * (1.0 - prey.defence)
                    other = prey.name
                    state[f"{other}:hp"] = max(0.0, state[f"{other}:hp"] - dmg)
                    ev.detail = f"bite lands, {other} hp={state[f'{other}:hp']:.2f}"
                    caught = state[f"{other}:hp"] <= 0.0
            elif action == "DEFEND":
                ev.detail = "braced, armour holds"
            elif action == "REST":
                state[f"{p.name}:stamina"] = min(p.stamina, state.get(f"{p.name}:stamina", p.stamina) + 1.0)
                ev.detail = "recovers stamina"
            events.append(ev)
            if caught:
                state["running"] = False
                events.append(SimEvent(t=t, actor=predator.name, action="FEED", detail=f"{prey.name} killed"))
                break
        if state.get(f"{prey.name}:stamina", prey.stamina) <= 0:
            state["running"] = False
            events.append(SimEvent(t=t, actor=prey.name, action="REST", detail="prey exhausted"))
        if state["dist"] > predator.perception * 1.6:
            state["running"] = False
            prey_escaped = True
            events.append(SimEvent(t=t, actor=prey.name, action="RETREAT", detail="escaped beyond detection"))

    if not prey_escaped and not caught:
        events.append(SimEvent(t=t, actor="system", action="REST", detail="timed out, disengagement"))

    return events


def resolve_outcome(events: list[SimEvent], predator_name: str, prey_name: str) -> str:
    if any(e.action == "FEED" for e in events):
        return "predator_success"
    if any("escaped" in e.detail for e in events):
        return "prey_escape"
    return "disengagement"


def build_run(scenario_id: str, seed: int, events: list[SimEvent], outcome: str) -> SimulationRun:
    return SimulationRun(
        scenario=scenario_id,
        seed=seed,
        result={
            "outcome": outcome,
            "events": [e.__dict__ for e in events],
        },
    )
