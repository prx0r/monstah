"""ReferencePack — constrained portfolio selection (MVP Phase 3).

Do NOT use simple top-N scoring (it yields five near-identical images). Instead
solve: maximize evidence/reuse score subject to required roles + viewpoint
diversity, via greedy slot-filling in priority order.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..media.asset import AssetCandidate, AssetRole


@dataclass
class PackSlot:
    """A required piece of the evidence pack."""

    role: AssetRole
    view: str = ""
    count: int = 1
    priority: int = 10  # lower fills first
    required: bool = True


@dataclass
class ReferencePack:
    """A curated, diversified evidence pack for one entity/environment."""

    entity_id: str
    reconstruction_version: str = "R1"
    slots: list[PackSlot] = field(default_factory=list)
    selected: list[AssetCandidate] = field(default_factory=list)

    def build(self, candidates: list[AssetCandidate]) -> "ReferencePack":
        """Constrained portfolio selection (greedy, priority-ordered)."""
        self.selected = portfolio_select(candidates, self.slots)
        return self

    @property
    def digest(self) -> str:
        import hashlib

        blob = "|".join(sorted(c.original_uri for c in self.selected))
        return hashlib.sha256(blob.encode()).hexdigest()


def portfolio_select(candidates: list[AssetCandidate], slots: list[PackSlot]) -> list[AssetCandidate]:
    """Fill required role/view slots greedily; honor diversity; never duplicate a candidate."""
    by_key = {c.provider_id or c.original_uri: c for c in candidates}
    used: set[str] = set()
    result: list[AssetCandidate] = []

    for slot in sorted(slots, key=lambda s: s.priority):
        # candidates matching this slot's role (+ view if specified), unused
        pool = [
            c for c in by_key.values()
            if c.provider_id not in used and c.role == slot.role
            and (not slot.view or (slot.view in (c.view or "")))
        ]
        pool.sort(key=lambda c: c.score, reverse=True)
        chosen = pool[: slot.count]
        for c in chosen:
            if c.provider_id:
                used.add(c.provider_id)
            result.append(c)
    return result


# --- canonical slot layouts -------------------------------------------------
MORPHOLOGY_SLOTS = [
    PackSlot(AssetRole.FOSSIL_REFERENCE, "lateral", priority=1),
    PackSlot(AssetRole.FOSSIL_REFERENCE, "dorsal", priority=2),
    PackSlot(AssetRole.ANATOMICAL_REFERENCE, "detail", priority=3),  # skull/teeth
    PackSlot(AssetRole.FOSSIL_REFERENCE, "", priority=4),
    PackSlot(AssetRole.ANATOMICAL_REFERENCE, "", priority=5),
    PackSlot(AssetRole.HISTORICAL_RECONSTRUCTION, "", priority=6, required=False),
]

ENVIRONMENT_SLOTS = [
    PackSlot(AssetRole.ENVIRONMENT_REFERENCE, "geology", priority=1),
    PackSlot(AssetRole.ENVIRONMENT_REFERENCE, "flora", priority=2),
    PackSlot(AssetRole.ENVIRONMENT_REFERENCE, "context", priority=3),
    PackSlot(AssetRole.ENVIRONMENT_REFERENCE, "", priority=4),
    PackSlot(AssetRole.HISTORICAL_RECONSTRUCTION, "", priority=5, required=False),
]


def pack_for_taxon(entity_id: str, candidates: list[AssetCandidate], version: str = "R1") -> ReferencePack:
    return ReferencePack(entity_id=entity_id, reconstruction_version=version,
                         slots=list(MORPHOLOGY_SLOTS)).build(candidates)


def pack_for_environment(entity_id: str, candidates: list[AssetCandidate], version: str = "R1") -> ReferencePack:
    return ReferencePack(entity_id=entity_id, reconstruction_version=version,
                         slots=list(ENVIRONMENT_SLOTS)).build(candidates)
