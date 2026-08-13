"""Historical validity must be strict: temporal + spatial + environment.

Geographic validity must come from real regions, never a hardcoded bypass.
"""

from __future__ import annotations

from monstah.core.models import Reference
from monstah.discovery import check_historical_overlap, temporal_overlap


def test_temporal_disjoint_invalid():
    o = check_historical_overlap(
        a_range=(100, 120), b_range=(60, 80),
        a_env={"land"}, b_env={"land"},
        a_region="A", b_region="A",
    )
    assert o.temporal is False
    assert o.valid_historical is False


def test_environment_incompatible_invalid():
    o = check_historical_overlap(
        a_range=(66, 68), b_range=(66, 68),
        a_env={"land"}, b_env={"sea"},
        a_region="Hell Creek", b_region="Hell Creek",
    )
    assert o.valid_historical is False


def test_geographic_mismatch_invalid():
    o = check_historical_overlap(
        a_range=(66, 68), b_range=(66, 68),
        a_env={"land"}, b_env={"land"},
        a_region="Hell Creek", b_region="Morrison",
    )
    assert o.spatial is False
    assert o.valid_historical is False


def test_unknown_region_is_not_a_bypass():
    # empty region must NOT silently grant overlap
    o = check_historical_overlap(
        a_range=(66, 68), b_range=(66, 68),
        a_env={"land"}, b_env={"land"},
        a_region="", b_region="",
    )
    assert o.spatial is False


def test_global_region_is_valid():
    o = check_historical_overlap(
        a_range=(66, 68), b_range=(66, 68),
        a_env={"land"}, b_env={"land"},
        a_region="global", b_region="Hell Creek",
    )
    assert o.valid_historical is True


def test_living_taxa_overlap_in_time():
    assert temporal_overlap(0, 0, 0, 0) == 1.0
