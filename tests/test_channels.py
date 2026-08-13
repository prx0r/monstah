"""Channel contract: combat and non-combat channels share one pipeline shape."""

from __future__ import annotations

import pytest

from monstah.channels import get_channel, list_channels
from monstah.channels.base import Channel


@pytest.fixture(scope="module")
def prehistoric():
    return get_channel("prehistoric", n_runs=200, offline=True)


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

    ch = get_channel("prehistoric", n_runs=100, offline=True)
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
    ch = get_channel("living-planet", n_runs=100, offline=True)
    taxa = ch.ingest(limit=5)
    by_ref = {t.ref.key: t for t in taxa}
    cands = ch.discover(taxa, top_n=1)
    assert cands
    out = ch.produce(cands[0], by_ref)
    # non-combat: no simulation outcomes
    assert out.mc.outcomes == {}
    assert out.story is not None
    # graph shots must NOT be labeled as canonical simulation events
    ch.render(out)
    assert out.bundle.shots[0].canonicality.value in ("RECONSTRUCTION", "GRAPH_DERIVED")


def test_evidence_chain_is_persisted_to_durable_store(tmp_path):
    import tempfile
    from monstah.data.duck import DuckStore

    ch = get_channel("prehistoric", n_runs=50, offline=True)
    # point at a throwaway durable store
    store = DuckStore(tmp_path / "test.duckdb")
    ch._analytics = store
    taxa = ch.ingest(limit=8)
    by = {t.ref.key: t for t in taxa}
    cands = ch.discover(taxa, top_n=1)
    ch.run(cands[0], by)
    # assertions/claims/reconstructions were persisted, not just held in memory
    assert store.count("assertions") >= 8
    assert store.count("claims") >= 8
    assert store.count("reconstructions") >= 8
    assert store.count("sim_results") >= 1
    assert store.count("events") >= 1
    store.close()


def test_deepblue_is_obis_driven():
    from monstah.channels.deepblue import DeepBlueAdapter

    ad = DeepBlueAdapter(offline=True)
    taxa = ad.load_taxa(limit=3)
    assert taxa
    # evidence facts are populated (scientific_name, mass) even offline
    assert taxa[0].facts.evidence.get("scientific_name") is not None
