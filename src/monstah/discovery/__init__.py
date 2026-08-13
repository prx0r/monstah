"""Discovery package: scenario generation, historical overlap, novelty."""

from .historical_overlap import OverlapResult, check_historical_overlap, temporal_overlap
from .scenario_generator import Candidate, ScenarioDiscovery, SCENARIO_TYPES, Taxon

__all__ = [
    "Candidate",
    "OverlapResult",
    "SCENARIO_TYPES",
    "ScenarioDiscovery",
    "Taxon",
    "check_historical_overlap",
    "temporal_overlap",
]
