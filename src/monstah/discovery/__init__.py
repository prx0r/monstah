"""Discovery package: scenario generation, historical overlap, novelty, opportunity."""

from .historical_overlap import OverlapResult, check_historical_overlap, temporal_overlap
from .opportunity import GoogleTrendsAdapter, Opportunity, OpportunityScorer, TopicSignal
from .scenario_generator import Candidate, ScenarioDiscovery, SCENARIO_TYPES, Taxon

__all__ = [
    "Candidate",
    "GoogleTrendsAdapter",
    "Opportunity",
    "OpportunityScorer",
    "OverlapResult",
    "SCENARIO_TYPES",
    "ScenarioDiscovery",
    "Taxon",
    "TopicSignal",
    "check_historical_overlap",
    "temporal_overlap",
]
