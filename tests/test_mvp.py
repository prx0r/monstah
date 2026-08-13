"""MVP guide commits 02–11: versioning, reference packs, visual specs/QA,
canonical registry, scenario manifest, persistence."""

from __future__ import annotations

import pytest

from monstah.assets.canonical import AssetStatus, CanonicalAsset, CanonicalAssetRegistry
from monstah.assets.image_backend import ImageCandidate, LocalSpecBackend, ViewSpec
from monstah.assets.qa import QASeverity, ReconstructionVisualQA
from monstah.assets.reference_pack import MORPHOLOGY_SLOTS, ReferencePack, portfolio_select
from monstah.assets.visual_spec import Certainty, EnvironmentVisualSpec, VisualReconstructionSpec
from monstah.media.asset import AssetCandidate, AssetRole
from monstah.reconstruction.versioning import (
    ReconstructionRegistry,
    ReconstructionStatus,
    ReconstructionVersion,
    bump_version,
)
from monstah.reconstruction.world import SnapshotEntity, build_world_snapshot
from monstah.scenarios.manifest import build_scenario_manifest


# --- commit 02: versioning -----------------------------------------------
def test_reconstruction_lifecycle_approval_requires_review():
    r = ReconstructionVersion("trex", "R1", basis_assertions=["a1"])
    assert r.usable_for_render is False  # DRAFT
    with pytest.raises(ValueError):
        r.mark(ReconstructionStatus.APPROVED)  # must review first
    r.mark(ReconstructionStatus.REVIEWED)
    r.mark(ReconstructionStatus.APPROVED)
    assert r.usable_for_render is True


def test_registry_auto_supersedes():
    reg = ReconstructionRegistry()
    reg.put(ReconstructionVersion("trex", "R1"))
    reg.put(ReconstructionVersion("trex", "R2"))
    assert reg.get("trex", "R1").status is ReconstructionStatus.SUPERSEDED
    assert reg.get("trex", "R2").supersedes == "R1"
    assert reg.head("trex").version == "R2"
    assert bump_version("R1") == "R2"


# --- commit 03: reference pack diversity ---------------------------------
def _asset(pid, role, score, view=""):
    c = AssetCandidate(provider="i", provider_id=pid, entity_id="trex", license="CC BY", role=role,
                       taxonomic_confidence=1.0, width=1200, height=800, view=view,
                       image_quality=0.9, viewpoint_value=0.9, provenance_quality=0.9,
                       reconstruction_relevance=0.9)
    c.compute_score()
    c.score = score  # force scores for a deterministic test
    return c


def test_portfolio_select_fills_distinct_roles():
    cands = [
        _asset("1", AssetRole.FOSSIL_REFERENCE, 0.9, "lateral"),
        _asset("2", AssetRole.FOSSIL_REFERENCE, 0.8, "dorsal"),
        _asset("3", AssetRole.ANATOMICAL_REFERENCE, 0.7, "detail"),
        _asset("4", AssetRole.ANATOMICAL_REFERENCE, 0.6),
    ]
    pack = ReferencePack(entity_id="trex", slots=MORPHOLOGY_SLOTS)
    sel = portfolio_select(cands, MORPHOLOGY_SLOTS)
    roles = {c.role for c in sel}
    assert AssetRole.FOSSIL_REFERENCE in roles
    assert AssetRole.ANATOMICAL_REFERENCE in roles
    # no duplicate candidate
    assert len({c.provider_id for c in sel}) == len(sel)


def test_reference_pack_digest_stable():
    cands = [_asset("1", AssetRole.FOSSIL_REFERENCE, 0.9, "lateral"),
             _asset("2", AssetRole.FOSSIL_REFERENCE, 0.8, "dorsal")]
    p1 = ReferencePack(entity_id="trex", slots=MORPHOLOGY_SLOTS).build(cands)
    p2 = ReferencePack(entity_id="trex", slots=MORPHOLOGY_SLOTS).build(cands)
    assert p1.digest == p2.digest


# --- commit 04/05: visual spec + backend ----------------------------------
def test_local_spec_backend_generates_candidates():
    spec = VisualReconstructionSpec(entity_id="trex", reconstruction_id="recon:trex:R1",
                                    morphology={"skull": "large", "torso": "massive", "limbs": "2", "tail": "heavy"},
                                    appearance={"coloration": Certainty.OPEN})
    refs = ReferencePack(entity_id="trex", slots=MORPHOLOGY_SLOTS).build(
        [_asset("1", AssetRole.FOSSIL_REFERENCE, 0.9, "lateral")])
    out = LocalSpecBackend().generate(spec, refs, ViewSpec(name="lateral"))
    assert out
    assert out[0].generator == "local-spec"
    assert out[0].sha256()


def test_visual_qa_classifies_by_severity():
    spec = VisualReconstructionSpec(entity_id="trex", reconstruction_id="r",
                                    morphology={"skull": "x"}, appearance={"coloration": Certainty.OPEN},
                                    forbidden=["feathers"])
    from monstah.assets.image_backend import ImageCandidate

    cand = ImageCandidate(id="c", entity_id="trex", reconstruction_id="r", view="lateral",
                          generator_manifest={"spec": {"morphology": {"torso": "x"}, "forbidden": ["feathers"]}})
    qa = ReconstructionVisualQA(spec).assess(cand)
    severities = {f.severity for f in qa.findings}
    assert QASeverity.P0_FACTUAL in severities
    assert QASeverity.P1_RECONSTRUCTION in severities
    assert QASeverity.P2_VISUAL in severities
    assert qa.passes is False


# --- commit 09: canonical asset registry ---------------------------------
def test_canonical_registry_immutable_and_resolves():
    reg = CanonicalAssetRegistry()
    a1 = CanonicalAsset(asset_id="a1", entity_id="trex", reconstruction_version="R1", visual_version="V1",
                        view="lateral", role="CANONICAL_RECONSTRUCTION", file_sha256="x" * 64)
    a2 = CanonicalAsset(asset_id="a2", entity_id="trex", reconstruction_version="R1", visual_version="V2",
                        view="lateral", role="CANONICAL_RECONSTRUCTION", file_sha256="y" * 64)
    reg.register(a1)
    reg.register(a2)  # supersedes a1
    assert a1.status is AssetStatus.SUPERSEDED
    assert reg.resolve("trex", "R1", "lateral").asset_id == "a2"


# --- commit 11: scenario manifest ----------------------------------------
def test_scenario_manifest_digest_and_historical_gate():
    world = build_world_snapshot("hc", entities=[
        SnapshotEntity(entity_id="trex", reconstruction_id="r", reconstruction_version="R1", assertion_ids=["a"])])
    m = build_scenario_manifest("scen", world, participant_reconstructions={"trex": "R1"}, validity="VALID")
    assert m.historical_proceeds is True
    assert m.digest()
    m2 = build_scenario_manifest("scen", world, participant_reconstructions={"trex": "R1"}, validity="VALID")
    assert m.digest() == m2.digest()


# --- commit 10: persistence ----------------------------------------------
def test_store_manager_persists_to_duck(tmp_path):
    from monstah.data.duck import DuckStore
    from monstah.production.persistence import StoreManager

    mgr = StoreManager(duck=DuckStore(tmp_path / "p.duckdb"), postgres=None)
    world = build_world_snapshot("hc", entities=[
        SnapshotEntity(entity_id="trex", reconstruction_id="r", reconstruction_version="R1", assertion_ids=["a"])])
    mgr.write_world_snapshot(world)
    mgr.write_episode("prehistoric", "predation", "T. rex", {"story": "x"})
    assert mgr.duck.count("world_snapshots") >= 1
    assert mgr.duck.count("episodes") >= 1
    mgr.close()
