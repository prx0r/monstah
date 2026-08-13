"""Historical overlap query (§16).

Historical Mode is strict: a scenario requires temporal overlap + geographic
overlap + environment compatibility. If any fails, the historical scenario is
invalid (no pretending). Lab Mode only suspends the co-occurrence constraint.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..core.models import Reference


@dataclass
class OverlapResult:
    temporal: bool = False
    spatial: bool = False
    environment: bool = False
    temporal_window: float = 0.0
    reasons: list[str] = field(default_factory=list)

    @property
    def valid_historical(self) -> bool:
        return self.temporal and self.spatial and self.environment

    def summary(self) -> str:
        parts = []
        parts.append(f"temporal={'yes' if self.temporal else 'no'}")
        parts.append(f"spatial={'yes' if self.spatial else 'no'}")
        parts.append(f"environment={'yes' if self.environment else 'no'}")
        return ", ".join(parts)


def temporal_overlap(a_min: float, a_max: float, b_min: float, b_max: float) -> float:
    """Width of shared time interval (Ma); 0 if disjoint. Living taxa overlap."""
    if a_max <= 0 and b_max <= 0:
        return 1.0
    lo = max(a_min, b_min)
    hi = min(a_max, b_max)
    return max(0.0, hi - lo)


def check_historical_overlap(
    *,
    a_range: tuple[float, float],
    b_range: tuple[float, float],
    a_env: set[str],
    b_env: set[str],
    a_region: str = "",
    b_region: str = "",
) -> OverlapResult:
    res = OverlapResult()
    res.temporal_window = temporal_overlap(*a_range, *b_range)
    res.temporal = res.temporal_window > 0
    res.spatial = _spatial_overlap(a_region, b_region)
    res.environment = bool(a_env & b_env)
    if not res.temporal:
        res.reasons.append(f"no shared time interval (window={res.temporal_window:.2f} Ma)")
    if not res.spatial:
        res.reasons.append(f"no geographic overlap ({a_region!r} vs {b_region!r})")
    if not res.environment:
        res.reasons.append("incompatible environments")
    return res


def _spatial_overlap(a_region: str, b_region: str) -> bool:
    """Strict geographic overlap from evidence-sourced regions.

    Unknown regions do NOT grant overlap; they are reported as a validity gap
    rather than silently passed (no bypassing historical validity).
    """
    if not a_region or not b_region:
        return False
    if "global" in (a_region, b_region):
        return True
    return a_region == b_region
