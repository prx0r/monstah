"""Significance detector (§34).

Not every simulation deserves content. Detect upsets, close escapes, unexpected
behavior, high uncertainty, rare relationships, and score story candidates.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Significance:
    scenario_id: str = ""
    score: float = 0.0
    signals: list[str] = field(default_factory=list)
    factors: dict[str, float] = field(default_factory=dict)

    @property
    def worth_content(self) -> bool:
        return self.score >= 0.5


def detect_significance(
    *,
    scenario_id: str,
    outcome_dist: dict[str, float],
    uncertainty: float = 0.0,
    rare_relationship: bool = False,
    counterintuitive: bool = False,
) -> Significance:
    """Score a Monte Carlo outcome distribution for story potential."""
    sig = Significance(scenario_id=scenario_id)
    total = sum(outcome_dist.values()) or 1.0
    # surprise: how close is the distribution to 50/50?
    dominant = max(outcome_dist.values()) if outcome_dist else 0.0
    surprise = 1.0 - dominant / total
    scientific_value = min(1.0, uncertainty + surprise)
    confidence = max(outcome_dist.values()) if outcome_dist else 0.0
    factors = {
        "surprise": surprise,
        "scientific_value": scientific_value,
        "confidence": confidence,
        "rare_relationship": float(rare_relationship),
        "counterintuitive": float(counterintuitive),
    }
    score = (
        0.35 * surprise
        + 0.25 * scientific_value
        + 0.15 * confidence
        + 0.15 * factors["rare_relationship"]
        + 0.10 * factors["counterintuitive"]
    )
    sig.score = round(score, 3)
    sig.factors = factors
    if surprise > 0.15:
        sig.signals.append("close_outcome")
    if rare_relationship:
        sig.signals.append("rare_relationship")
    if counterintuitive:
        sig.signals.append("counterintuitive")
    if uncertainty > 0.3:
        sig.signals.append("high_uncertainty")
    return sig
