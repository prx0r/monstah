"""Monte Carlo runner on NumPy SeedSequence (§20).

A scenario is never one run. Every run has a DETERMINISTIC identity:

    run i  ->  rng = np.random.default_rng(SeedSequence([master_seed, i]))

so any run (including selected ones) is exactly replayable from
(master_seed, run_index). No generator is ever advanced and reused; each
`resolve_duel` call uses a freshly-seeded generator, keeping reproduction exact.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

import numpy as np

from .d20 import Combatant, resolve_duel


@dataclass
class MCResult:
    runs: int = 0
    outcomes: dict[str, float] = field(default_factory=dict)
    selected: dict[str, int] = field(default_factory=dict)  # label -> run_index
    master_seed: int = 0
    n_rounds: int = 5

    @property
    def dominant_outcome(self) -> str:
        return max(self.outcomes, key=self.outcomes.get) if self.outcomes else ""


def _outcome(hp: int) -> str:
    if hp <= 0:
        return "attacker_wins"
    return "defender_survives"


def run_rng(master_seed: int, run_index: int) -> np.random.Generator:
    """Deterministic per-run RNG: (master_seed, run_index) fully identifies it."""
    return np.random.default_rng(np.random.SeedSequence([master_seed, run_index]))


def replay(
    attacker: Combatant,
    defender: Combatant,
    master_seed: int,
    run_index: int,
    n_rounds: int = 5,
) -> int:
    """Replay a single run exactly. Returns final defender HP."""
    return int(resolve_duel(attacker, defender, run_rng(master_seed, run_index), n_rounds=n_rounds)[-1])


def run_monte_carlo(
    attacker: Combatant,
    defender: Combatant,
    *,
    n: int = 1000,
    n_rounds: int = 5,
    master_seed: int = 42,
) -> MCResult:
    """Run `n` independently-seeded duels and aggregate outcome frequencies."""
    outcomes: Counter = Counter()
    for i in range(n):
        hp = replay(attacker, defender, master_seed, i, n_rounds=n_rounds)
        outcomes[_outcome(hp)] += 1

    total = sum(outcomes.values()) or 1
    dist = {k: v / total for k, v in outcomes.items()}
    dominant = max(dist, key=dist.get)

    # select representative / surprising / median runs by run_index (replayable)
    selected: dict[str, int] = {}
    for i in range(n):
        out = _outcome(replay(attacker, defender, master_seed, i, n_rounds=n_rounds))
        if out == dominant and "representative" not in selected:
            selected["representative"] = i
        if out != dominant and "surprising" not in selected:
            selected["surprising"] = i
        if "median" not in selected and out == dominant:
            selected["median"] = i
        if len(selected) >= 3:
            break

    return MCResult(runs=n, outcomes=dist, selected=selected, master_seed=master_seed, n_rounds=n_rounds)
