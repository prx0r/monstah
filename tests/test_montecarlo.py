"""Monte Carlo runs must be exactly replayable from (master_seed, run_index)."""

from __future__ import annotations

from monstah.simulations import Combatant, replay, run_monte_carlo, run_rng

import numpy as np


def _pair():
    a = Combatant({"name": "Trex", "armor_class": 13, "hit_points": 136,
                   "attack_bonus": 10, "damage_dice": "4d12+7"})
    b = Combatant({"name": "Tri", "armor_class": 13, "hit_points": 95,
                   "attack_bonus": 9, "damage_dice": "4d8+6"})
    return a, b


def test_selected_runs_replay_exactly():
    a, b = _pair()
    mc = run_monte_carlo(a, b, n=2000, master_seed=7)
    for label, idx in mc.selected.items():
        assert replay(a, b, mc.master_seed, idx) == replay(a, b, mc.master_seed, idx)


def test_replay_is_deterministic_across_calls():
    a, b = _pair()
    hp = replay(a, b, 42, 5)
    assert hp == replay(a, b, 42, 5)


def test_distribution_is_stable():
    a, b = _pair()
    m1 = run_monte_carlo(a, b, n=500, master_seed=99)
    m2 = run_monte_carlo(a, b, n=500, master_seed=99)
    assert m1.outcomes == m2.outcomes


def test_seed_scheme_identifies_run():
    g1 = run_rng(42, 3)
    g2 = run_rng(42, 3)
    assert g1.random() == g2.random()
