"""Narrative package: significance, story compilation, citations."""

from .significance import Significance, detect_significance
from .story import EpisodeSpec, NarrativeClaim, compile_story

__all__ = [
    "EpisodeSpec",
    "NarrativeClaim",
    "Significance",
    "compile_story",
    "detect_significance",
]
