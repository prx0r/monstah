"""Monte Carlo runner (§20).

A scenario is never one run. Run many seeded simulations, aggregate outcomes
into distributions, then offer a selection of representative runs
(representative / close / surprising / median).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from .encounter import Participant, resolve_outcome, run_encounter


@dataclass
class MCResult:
    runs: int = 0
    outcomes: dict[str, float] = field(default_factory=dict)
    selected: dict[str, int] = field(default_factory=dict)  # label -> seed

    @property
    def dominant_outcome(self) -> str:
        return max(self.outcomes, key=self.outcomes.get) if self.outcomes else ""


def run_monte_carlo(
    predator: Participant,
    prey: Participant,
    *,
    n: int = 1000,
    seed_range: int = 2**31,
    scenario_id: str = "scenario",
) -> MCResult:
    """Run `n` seeded encounters and aggregate outcome frequencies."""
    outcomes = Counter()
    for seed in range(n):
        events = run_encounter(predator, prey, seed=seed)
        outcomes[resolve_outcome(events, predator.name, prey.name)] += 1

    total = sum(outcomes.values()) or 1
    dist = {k: v / total for k, v in outcomes.items()}

    # representative selection
    dominant = max(dist, key=dist.get)
    selected: dict[str, int] = {}
    for seed in range(n):
        events = run_encounter(predator, prey, seed=seed)
        outcome = resolve_outcome(events, predator.name, prey.name)
        if outcome == dominant and "representative" not in selected:
            selected["representative"] = seed
        if outcome != dominant and "surprising" not in selected:
            selected["surprising"] = seed
        if "median" not in selected and outcome == dominant:
            selected.setdefault("median", seed)
        if len(selected) >= 3:
            break

    return MCResult(runs=n, outcomes=dist, selected=selected)
