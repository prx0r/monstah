"""Type firewall: game-proxy and narrative layers must never become scientific state."""

from __future__ import annotations

from monstah.core.models import Reference
from monstah.core.truth import Layer, Status, TaxonFacts, TypedValue
from monstah.discovery import Taxon

import pytest


def _taxon(name="T", region="Hell Creek", diet="carnivore") -> Taxon:
    return Taxon(
        ref=Reference(namespace="pbdb", key="1"),
        name=name, min_ma=66.0, max_ma=68.0, env={"land"}, diet=diet, region=region,
    )


def test_game_proxy_never_leaks_into_scientific_traits():
    t = _taxon()
    t.set_evidence("mass_kg", 7000, unit="kg")
    t.set_game_proxy("armor_class", 13, status=Status.GAME_PROXY.value)
    assert "armor_class" not in t.traits
    assert "mass_kg" in t.traits
    assert t.game_proxy["armor_class"] == 13


def test_promotion_into_game_proxy_is_blocked():
    ev = TypedValue(Layer.EVIDENCE, 7000, unit="kg")
    with pytest.raises(ValueError):
        ev.promote(Layer.GAME_PROXY)


def test_promotion_evidence_to_reconstruction_allowed():
    ev = TypedValue(Layer.EVIDENCE, 7000, unit="kg")
    rec = ev.promote(Layer.RECONSTRUCTION)
    assert rec.layer is Layer.RECONSTRUCTION
    assert rec.status == Status.MODELLED.value
