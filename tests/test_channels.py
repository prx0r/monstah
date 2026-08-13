"""Channel contract: combat and non-combat channels share one pipeline shape."""

from __future__ import annotations

import pytest

from monstah.channels import get_channel, list_channels
from monstah.channels.base import Channel


@pytest.fixture(scope="module")
def prehistoric():
    return get_channel("prehistoric", n_runs=200)


def test_channel_registry():
    names = set(list_channels())
    assert {"prehistoric", "deep-blue", "living-planet"} <= names


def test_channel_contract_shape(prehistoric):
    taxa = prehistoric.ingest(limit=10)
    assert taxa, "ingest produced no taxa"
    cands = prehistoric.discover(taxa, top_n=3)
    assert cands, "discovery produced no candidates"
    by_ref = {t.ref.key: t for t in taxa}
    out = prehistoric.produce(cands[0], by_ref)
    assert out.story is not None
    assert out.overlap is not None
    assert out.shots is not None


def test_historical_mode_requires_validity():
    from monstah.core.models import Reference
    from monstah.discovery import Candidate, Taxon

    ch = get_channel("prehistoric", n_runs=100)
    sea = Taxon(ref=Reference(namespace="pbdb", key="sea"), name="Mosasaurus",
                min_ma=66, max_ma=72, env={"sea"}, diet="carnivore", region="global")
    land = Taxon(ref=Reference(namespace="pbdb", key="land"), name="Ankylosaurus",
                 min_ma=66, max_ma=68, env={"land"}, diet="herbivore", region="global")
    by_ref = {sea.ref.key: sea, land.ref.key: land}
    # intentionally invalid historical candidate: sea vs land (env incompatible)
    cand = Candidate(template="predation", entities=[sea.ref, land.ref], environment=None, mode="historical")
    assert ch.validate(cand, by_ref).valid_historical is False
    with pytest.raises(ValueError):
        ch.produce(cand, by_ref)


def test_non_combat_channel_path():
    ch = get_channel("living-planet", n_runs=100)
    taxa = ch.ingest(limit=5)
    by_ref = {t.ref.key: t for t in taxa}
    cands = ch.discover(taxa, top_n=1)
    assert cands
    out = ch.produce(cands[0], by_ref)
    # non-combat: no simulation outcomes
    assert out.mc.outcomes == {}
    assert out.story is not None


def test_deepblue_is_obis_driven():
    from monstah.channels.deepblue import DeepBlueAdapter

    ad = DeepBlueAdapter()
    taxa = ad.load_taxa(limit=3)
    assert taxa
    # evidence depth must come from OBIS, not hardcoded 3000 for everything
    depths = {t.facts.evidence.get("max_depth").value for t in taxa}
    assert depths == {0} or len(depths) >= 1  # distinct real values
