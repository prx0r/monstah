"""Evidence chain integrity: narrative claims resolve to real Assertions/Sources."""

from __future__ import annotations

from monstah.core.models import Reference
from monstah.discovery import Taxon
from monstah.evidence.builder import build_evidence_pack, source_from


def _taxon(key="1", name="Trex", region="Hell Creek") -> Taxon:
    t = Taxon(ref=Reference(namespace="paleo", key=key), name=name,
              min_ma=66, max_ma=68, env={"land"}, diet="carnivore", region=region)
    t.set_evidence("mass_kg", 7000, unit="kg", status="LITERATURE_ESTIMATE")
    return t


def test_evidence_chain_ids_are_persistable():
    t = _taxon()
    src = source_from("paleo", "1", title="Trex")
    pack = build_evidence_pack(t.ref, t.facts, src)
    assert pack.source is not None
    assert len(pack.claims) == 1
    assert len(pack.assertions) == 1
    # the Claim and the Assertion carry distinct, real, non-empty IDs
    assert pack.claims[0].id
    assert pack.assertions[0].id
    # assertion provenance points at the actual source reference
    assert pack.assertions[0].provenance.source.uri == "paleo:1"


def test_reconstruction_references_persisted_assertion_ids():
    t = _taxon()
    src = source_from("paleo", "1")
    pack = build_evidence_pack(t.ref, t.facts, src)
    from monstah.evidence.builder import build_reconstruction

    rec = build_reconstruction(t.ref, t.facts, src, assertions=pack.assertions)
    # reconstruction assertion ids match the real persisted assertion ids
    assert set(rec.assertions) == {a.id for a in pack.assertions}


def test_narrative_claim_resolves_to_real_assertion():
    from monstah.pipeline import _evidence_claims

    t = _taxon()
    src = source_from("paleo", "1")
    pack = build_evidence_pack(t.ref, t.facts, src)
    claims = _evidence_claims(t, t, {"1": pack.assertions})
    assert claims
    claim = claims[0]
    # assertion_ids are the real persisted assertion UUIDs
    assert claim.assertion_ids == [pack.assertions[0].id]
    # source_ids resolve to the real source reference uri
    assert claim.source_ids == ["paleo:1"]
    assert claim.resolves
