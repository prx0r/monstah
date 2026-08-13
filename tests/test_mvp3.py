"""MVP commits 21-32: QA layers, narration, assembler, manifest, produce harness."""

from __future__ import annotations

import tempfile

from monstah.media.ltx import ShotBasis
from monstah.media.qa import ReconstructionConstraintSet, run_qa
from monstah.media.shot_spec2 import ShotBasis2, ShotControl, ShotSpecV2
from monstah.production.manifest import EpisodeManifest
from monstah.production.produce import produce_episode
from monstah.production.run import ProductionRun, RunStage
from monstah.story.narration import NarrativeClause, compile_narration


# --- commit 22-23: QA layers + uncertainty-aware constraints -------------
def test_constraint_set_from_spec_treats_open_as_tolerant():
    from monstah.assets.visual_spec import Certainty, VisualReconstructionSpec

    spec = VisualReconstructionSpec(entity_id="trex", reconstruction_id="r",
                                    morphology={"horn_count": 2},
                                    appearance={"horn_count": Certainty.CONSTRAINED,
                                                "coloration": Certainty.OPEN})
    cs = ReconstructionConstraintSet.from_spec(spec)
    assert "horn_count" in cs.hard
    assert "coloration" in cs.open  # OPEN => QA must not reject variation


def test_run_qa_four_layers():
    from monstah.assets.visual_spec import Certainty, VisualReconstructionSpec

    spec = VisualReconstructionSpec(entity_id="trex", reconstruction_id="r",
                                    morphology={"horn_count": 2},
                                    appearance={"horn_count": Certainty.CONSTRAINED},
                                    forbidden=["feathers"])
    cs = ReconstructionConstraintSet.from_spec(spec)
    shot = ShotSpecV2(shot_id="s1", basis=ShotBasis2(type=ShotBasis.SIMULATION_EVENT,
                                                     event_ids=["sim://e0"]))
    results = run_qa(shot, renderer_manifest={"m": 1}, constraints=cs,
                     events=[{"event_id": "sim://e0"}], claims=["feathers present"])
    layers = {r.layer for r in results}
    assert {"binding", "visual_identity", "event", "epistemic"} <= layers


# --- commit 25: narration compiled from claims ----------------------------
def test_narration_qualifies_by_status():
    out = compile_narration([
        NarrativeClause(text="in western North America", status="OBSERVED"),
        NarrativeClause(text="a large theropod", status="RECONSTRUCTED"),
        NarrativeClause(text="predation was common", status="MODELLED"),
    ])
    assert "Fossils place these animals in" in out
    assert "In our simulation" in out


# --- commit 27: episode manifest ------------------------------------------
def test_episode_manifest_traceable():
    m = EpisodeManifest(episode_id="e1", world_snapshot_digest="w", scenario_digest="s",
                        event_ids=["sim://e0"], assertions=["a1"])
    assert m.digest()
    assert "sim://e0" in m.to_dict()["event_ids"]


# --- commit 29: production run state machine ------------------------------
def test_production_run_resume(tmp_path):
    r = ProductionRun.create("prehistoric", str(tmp_path))
    r.mark(RunStage.INGESTED, "d1")
    r.mark(RunStage.SIMULATED, "d2")
    r.save()
    loaded = ProductionRun.load(r.state_file())
    assert loaded.stage is RunStage.SIMULATED
    assert loaded.can_resume_from() is RunStage.STORY_READY


# --- commit 28: produce vertical harness ----------------------------------
def test_produce_episode_full_slice():
    out = tempfile.mkdtemp()
    res = produce_episode("prehistoric", world_id="hell-creek", out_dir=out, n_runs=50)
    assert res.episode_manifest.digest()
    assert res.render_jobs
    assert res.qa
    assert res.run.stage is RunStage.PUBLISHED
    assert res.assembly["master"] == "16:9"
