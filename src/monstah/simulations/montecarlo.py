"""Monte Carlo runner on NumPy SeedSequence (§20).

A scenario is never one run. Seed the master run, derive independent child
streams via `SeedSequence.spawn` (no cross-run correlation), aggregate outcome
frequencies, then select representative / surprising / median runs.

Kept CPU-bound and memory-light: vectorized d20 duels across many rounds.
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
    selected: dict[str, int] = field(default_factory=dict)  # label -> seed
    master_seed: int = 0

    @property
    def dominant_outcome(self) -> str:
        return max(self.outcomes, key=self.outcomes.get) if self.outcomes else ""


def _outcome(hp: int) -> str:
    if hp <= 0:
        return "attacker_wins"
    return "defender_survives"


def run_monte_carlo(
    attacker: Combatant,
    defender: Combatant,
    *,
    n: int = 1000,
    n_rounds: int = 5,
    master_seed: int = 42,
) -> MCResult:
    """Run `n` seeded duels using independent child RNG streams."""
    ss = np.random.SeedSequence(master_seed)
    child_seeds = ss.spawn(n)

    outcomes: Counter = Counter()
    # vectorize the aggregate pass: batch duels per chunk to stay light
    CHUNK = 500
    pool: list[np.random.Generator] = [np.random.default_rng(s) for s in child_seeds]
    for start in range(0, n, CHUNK):
        gens = pool[start : start + CHUNK]
        for g in gens:
            hp = resolve_duel(attacker, defender, g, n_rounds=n_rounds)[-1]
            outcomes[_outcome(hp)] += 1

    total = sum(outcomes.values()) or 1
    dist = {k: v / total for k, v in outcomes.items()}
    dominant = max(dist, key=dist.get)

    # representative / surprising / median run selection (re-run, cheaply)
    selected: dict[str, int] = {}
    for seed, g in zip(child_seeds, pool):
        hp = resolve_duel(attacker, defender, g, n_rounds=n_rounds)[-1]
        out = _outcome(hp)
        if out == dominant and "representative" not in selected:
            selected["representative"] = int(seed.entropy) if hasattr(seed, "entropy") else 0
        if out != dominant and "surprising" not in selected:
            selected["surprising"] = int(seed.entropy) if hasattr(seed, "entropy") else 0
        if "median" not in selected and out == dominant:
            selected["median"] = int(seed.entropy) if hasattr(seed, "entropy") else 0
        if len(selected) >= 3:
            break

    return MCResult(runs=n, outcomes=dist, selected=selected, master_seed=master_seed)
