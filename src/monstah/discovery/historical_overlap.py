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
    """Width of shared time interval (Ma); 0 if disjoint."""
    lo = max(a_min, b_min)
    hi = min(a_max, b_max)
    return max(0.0, hi - lo)


def check_historical_overlap(
    *,
    a_range: tuple[float, float],
    b_range: tuple[float, float],
    a_env: set[str],
    b_env: set[str],
    a_region: str,
    b_region: str,
    spatial_shared: bool | None = None,
) -> OverlapResult:
    res = OverlapResult()
    res.temporal_window = temporal_overlap(*a_range, *b_range)
    res.temporal = res.temporal_window > 0
    res.spatial = spatial_shared if spatial_shared is not None else (a_region == b_region or a_region == "global" or b_region == "global")
    res.environment = bool(a_env & b_env)
    if not res.temporal:
        res.reasons.append(f"no shared time interval (window={res.temporal_window:.2f} Ma)")
    if not res.spatial:
        res.reasons.append("no geographic overlap")
    if not res.environment:
        res.reasons.append("incompatible environments")
    return res
