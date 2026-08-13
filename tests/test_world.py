"""WorldSnapshot: immutable world aggregation + stable digest."""

from __future__ import annotations

from monstah.reconstruction.world import (
    SnapshotEntity,
    build_world_snapshot,
    snapshot_from_manifest,
)


def _snapshot(version="R1", assertion_ids=None):
    return build_world_snapshot(
        world_id="hell-creek",
        entities=[
            SnapshotEntity(entity_id="paleo:trex", reconstruction_id="recon:trex:R1",
                           reconstruction_version=version,
                           assertion_ids=assertion_ids or ["a1"]),
        ],
    )


def test_snapshot_digest_is_stable():
    assert _snapshot().digest() == _snapshot().digest()


def test_snapshot_digest_changes_with_version():
    assert _snapshot(version="R1").digest() != _snapshot(version="R2").digest()


def test_snapshot_digest_changes_with_assertions():
    assert _snapshot(assertion_ids=["a1"]).digest() != _snapshot(assertion_ids=["a2"]).digest()


def test_snapshot_from_manifest():
    from monstah.core.models import Reference
    from monstah.evidence.builder import build_evidence_pack, source_from
    from monstah.discovery import Taxon

    t = Taxon(ref=Reference(namespace="paleo", key="1"), name="Trex", min_ma=66, max_ma=68,
              env={"land"}, diet="carnivore", region="Hell Creek")
    t.set_evidence("mass_kg", 7000, unit="kg", status="LITERATURE_ESTIMATE")
    src = source_from("paleo", "1", title="Trex")
    pack = build_evidence_pack(t.ref, t.facts, src)
    snap = snapshot_from_manifest(
        "hell-creek",
        entities={t.ref.key: t.ref},
        versions={t.ref.key: "R1"},
        assertions={t.ref.key: pack.assertions},
    )
    assert snap.digest()
    assert snap.entities[0].reconstruction_version == "R1"
    assert snap.entities[0].assertion_ids == [pack.assertions[0].id]
