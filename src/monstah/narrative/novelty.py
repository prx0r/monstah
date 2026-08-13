"""ContentHistory and novelty scoring (§22).

Track everything already published so repetition is penalized and genuinely
novel combinations are promoted. Novelty is no longer a constant placeholder —
it's derived from the actual scenario history.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable

from ..core.models import Reference


@dataclass
class ContentHistory:
    """Records which entity/relation combinations have been covered."""

    seen_pairs: set[tuple[str, str]] = field(default_factory=set)
    entity_usage: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    relation_usage: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    total: int = 0

    def record(self, template: str, entities: Iterable[Reference]) -> None:
        keys = sorted(e.key for e in entities)
        self.seen_pairs.add(tuple(keys))
        for e in entities:
            self.entity_usage[e.key] += 1
        self.relation_usage[template] += 1
        self.total += 1

    def pair_novelty(self, entities: Iterable[Reference]) -> float:
        """1.0 if never covered, decaying with prior coverage."""
        keys = tuple(sorted(e.key for e in entities))
        if keys not in self.seen_pairs:
            return 1.0
        # repeat of a covered pair: heavily penalized
        return 0.05

    def entity_novelty(self, entity_key: str) -> float:
        n = self.entity_usage.get(entity_key, 0)
        if n == 0:
            return 1.0
        return max(0.05, 1.0 / (1.0 + n))


class NoveltyScorer:
    """Combines pair + entity novelty into the discovery factor."""

    def __init__(self, history: ContentHistory | None = None) -> None:
        self.history = history or ContentHistory()

    def score(self, template: str, entities: Iterable[Reference]) -> float:
        ents = list(entities)
        pair = self.history.pair_novelty(ents)
        entity = min(self.history.entity_novelty(e.key) for e in ents) if ents else 1.0
        return round(0.6 * pair + 0.4 * entity, 3)

    def commit(self, template: str, entities: Iterable[Reference]) -> None:
        self.history.record(template, entities)
