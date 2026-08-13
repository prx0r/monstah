"""LTX renderer binding: shots must carry canonicality from the truth layer."""

from __future__ import annotations

from monstah.media import Canonicality, LtxShotSpec
from monstah.media.shots import EntityVersion, ShotSpec, canonicality_for_mode, compile_shots, to_ltx_shots


def test_canonicality_mapping():
    assert canonicality_for_mode("historical") == Canonicality.CANONICAL_EVENT
    assert canonicality_for_mode("lab") == Canonicality.COUNTERFACTUAL
    assert canonicality_for_mode("graph") == Canonicality.RECONSTRUCTION


def test_compile_shots_produce_ltx_specs():
    shots = compile_shots(
        entity_versions=[EntityVersion(entity="T. rex", version="R17", asset_uri="r2:x")],
        environment="hell-creek",
        event_log=[{"t": 0, "actor": "T. rex", "action": "CHASE"}],
    )
    ltx = to_ltx_shots(shots, mode="historical")
    assert len(ltx) == 1
    s = ltx[0]
    assert s.canonicality == Canonicality.CANONICAL_EVENT
    assert s.entity_versions == ["T. rex:R17"]
    assert s.environment_version == "hell-creek"


def test_ltx_spec_validates_required_fields():
    s = LtxShotSpec(
        shot_id="x-001",
        project="monstah",
        canonicality="COUNTERFACTUAL",
        prompt="a shot",
        duration_s=6,
        aspect_ratio="16:9",
        constraints=["no invented outcomes"],
    )
    assert s.canonicality == Canonicality.COUNTERFACTUAL
    assert s.fps == 24
