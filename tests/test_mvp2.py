"""MVP commits 12-20: simulation models, story beats, episode spec,
scientific renderer, ShotSpec v2, control planner/compositor, renderers."""

from __future__ import annotations

from monstah.media.control import ControlFrameCompositor, ControlPlanner
from monstah.media.ltx import ShotBasis
from monstah.media.renderer import OfflineRenderer
from monstah.media.scientific_renderer import ScientificRenderer
from monstah.media.shot_spec2 import ShotBasis2, ShotControl, ShotSpecV2, ShotSubject
from monstah.simulations.model import ModelClass, game_proxy_model
from monstah.story.beats import BeatKind, StoryBeat


# --- commit 12-13: simulation model classes ------------------------------
def test_game_proxy_model_is_honest():
    m = game_proxy_model()
    assert m.model_class is ModelClass.GAME_PROXY
    assert "game abstraction" in m.assumptions[0]
    assert m.describe().startswith("open5e-d20")


def test_simulation_run_has_identity():
    from monstah.simulations.model import SimulationRun

    m = game_proxy_model()
    r = SimulationRun(run_id="r1", scenario_digest="s", model=m, seed=1,
                      events=[{"event_id": "e1"}], outcome="attacker_wins")
    assert r.digest()
    r2 = SimulationRun(run_id="r1", scenario_digest="s", model=m, seed=1,
                       events=[{"event_id": "e1"}], outcome="attacker_wins")
    assert r.digest() == r2.digest()


# --- commit 14: claim-aware story beat ------------------------------------
def test_story_beat_grounding():
    grounded = StoryBeat("b1", BeatKind.SIMULATION_RESULT, "sim says X",
                         basis_event_ids=["sim://s/run/0/event/0"])
    assert grounded.grounded
    ungrounded = StoryBeat("b2", BeatKind.SIMULATION_RESULT, "sim says X")
    assert not ungrounded.grounded
    bridge = StoryBeat("b3", BeatKind.EDITORIAL_BRIDGE, "meanwhile...")
    assert bridge.grounded  # bridges are grounded by design


# --- commit 15: executable episode spec -----------------------------------
def test_episode_spec_compiles_script():
    from monstah.story.episode import EpisodeSpec

    ep = EpisodeSpec(episode_id="e1", hook="Which predator ruled?")
    ep.beats = [StoryBeat("b1", BeatKind.RECONSTRUCTION, "T. rex was robust", basis_reconstruction_ids=["r"])]
    script = ep.compile_script()
    assert "Which predator ruled?" in script
    assert "RECONSTRUCTION" in script


# --- commit 16: deterministic scientific renderer -------------------------
def test_scientific_renderer_is_deterministic():
    sr = ScientificRenderer()
    a = sr.temporal_range_svg([{"name": "T. rex", "min_ma": 66, "max_ma": 68}])
    b = sr.temporal_range_svg([{"name": "T. rex", "min_ma": 66, "max_ma": 68}])
    assert a == b and a.startswith("<svg")
    assert "T. rex" in a


# --- commit 17-19: shot spec v2 + control ---------------------------------
def test_control_planner_mode_mapping():
    planner = ControlPlanner()
    sim_shot = ShotSpecV2(shot_id="s1", basis=ShotBasis2(type=ShotBasis.SIMULATION_EVENT,
                                                         event_ids=["sim://e0"]))
    assert planner.mode_for(sim_shot) == "FIRST_LAST"
    recon_shot = ShotSpecV2(shot_id="s2", basis=ShotBasis2(type=ShotBasis.RECONSTRUCTION),
                            subjects=[ShotSubject(entity_id="trex")])
    assert planner.mode_for(recon_shot) == "I2V"
    data_shot = ShotSpecV2(shot_id="s3", control=ShotControl(preferred="DETERMINISTIC"))
    assert planner.mode_for(data_shot) == "DETERMINISTIC"


def test_control_frame_compositor_builds_plates():
    comp = ControlFrameCompositor()
    shot = ShotSpecV2(shot_id="s1", basis=ShotBasis2(type=ShotBasis.SIMULATION_EVENT, event_ids=["e0"]),
                      subjects=[ShotSubject(entity_id="trex", reconstruction_version="R1")])
    plates = comp.first_last_plates(shot, canonical={("trex", "lateral"): "asset:trex"})
    assert len(plates) == 2
    assert plates[0].view == "first" and plates[1].view == "last"


# --- commit 20: renderers ---------------------------------------------------
def test_offline_renderer_produces_manifest():
    r = OfflineRenderer()
    shot = ShotSpecV2(shot_id="s1", basis=ShotBasis2(type=ShotBasis.RECONSTRUCTION),
                      subjects=[ShotSubject(entity_id="trex")])
    job = r.submit(shot)
    assert r.poll(job) == "ready"
    res = r.fetch(job)
    assert res["manifest"]["basis_type"] == "RECONSTRUCTION"


def test_ltx_api_renderer_requires_key():
    from monstah.media.renderer import LTX25ApiRenderer

    r = LTX25ApiRenderer(api_key="")
    try:
        r.submit(ShotSpecV2(shot_id="s1"))
        assert False, "should have raised"
    except RuntimeError as e:
        assert "key" in str(e)
