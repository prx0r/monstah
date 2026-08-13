"""OpportunityScorer: demand × (1/supply) × production economics."""

from __future__ import annotations

from monstah.discovery.opportunity import OpportunityScorer, TopicSignal


def test_high_demand_low_supply_wins():
    s = OpportunityScorer(supply={"blue": 0.1, "red": 0.9})
    o1 = s.score(TopicSignal(topic="blue", current=60, baseline=30, velocity=1.0))
    o2 = s.score(TopicSignal(topic="red", current=90, baseline=30, velocity=1.0))
    # blue ocean (low supply) should beat saturated red even with lower demand
    assert o1.score > o2.score
    assert o1.factors["supply_penalty"] > o2.factors["supply_penalty"]


def test_velocity_boosts_rising_topic():
    s = OpportunityScorer()
    rising = s.score(TopicSignal(topic="x", current=80, baseline=40, velocity=1.0))
    flat = s.score(TopicSignal(topic="x", current=80, baseline=80, velocity=0.0))
    assert rising.score > flat.score
    assert rising.factors["velocity"] == 1.0


def test_zero_demand_scores_zero():
    s = OpportunityScorer()
    o = s.score(TopicSignal(topic="x", current=0, baseline=0, velocity=0))
    assert o.score == 0.0
