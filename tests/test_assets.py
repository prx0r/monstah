"""Canonical asset layer: license policy + ranking (no network)."""

from __future__ import annotations

from monstah.media.asset import (
    AssetCandidate,
    AssetPack,
    AssetRole,
    EpistemicStatus,
    license_tier,
    license_usability,
)


def test_license_policy():
    assert license_tier("CC BY 4.0") == "ALLOW"
    assert license_tier("CC BY-SA 3.0") == "ALLOW"
    assert license_tier("CC0") == "ALLOW"
    assert license_tier("Public Domain") == "ALLOW"
    assert license_tier("CC BY-NC-SA") == "REVIEW"
    assert license_tier("All rights reserved") == "REJECT"
    assert license_tier("") == "REJECT"  # never assume reuse


def test_asset_score_ranks_evidence_fit_not_popularity():
    good = AssetCandidate(provider="i", entity_id="e", license="CC BY 4.0",
                          taxonomic_confidence=0.95, width=1200, height=900,
                          image_quality=0.9, viewpoint_value=0.9, provenance_quality=0.9,
                          reconstruction_relevance=0.9)
    bad_lic = AssetCandidate(provider="i", entity_id="e", license="All rights reserved",
                             taxonomic_confidence=0.95, width=1200, height=900,
                             image_quality=0.9, viewpoint_value=0.9, provenance_quality=0.9,
                             reconstruction_relevance=0.9)
    assert good.compute_score() > bad_lic.compute_score()
    assert bad_lic.compute_score() == 0.0


def test_source_image_vs_canonical_reconstruction_roles():
    obs = AssetCandidate(provider="gbif", entity_id="e", license="CC BY", role=AssetRole.OBSERVATIONAL_REFERENCE,
                         epistemic_status=EpistemicStatus.OBSERVED_PHOTOGRAPH)
    canon = AssetCandidate(provider="wikimedia", entity_id="e", license="CC BY-SA",
                           role=AssetRole.CANONICAL_RECONSTRUCTION,
                           epistemic_status=EpistemicStatus.GENERATED_RECONSTRUCTION)
    assert obs.role is AssetRole.OBSERVATIONAL_REFERENCE
    assert canon.epistemic_status is EpistemicStatus.GENERATED_RECONSTRUCTION


def test_asset_pack_orders_by_score():
    pack = AssetPack(entity_id="e", reconstruction_version="R17")
    low = AssetCandidate(provider="i", entity_id="e", license="CC BY-NC", taxonomic_confidence=0.5)
    high = AssetCandidate(provider="i", entity_id="e", license="CC BY", taxonomic_confidence=0.9,
                          width=2000, height=1500, image_quality=0.9, viewpoint_value=0.9,
                          provenance_quality=0.9, reconstruction_relevance=0.9)
    pack.candidates = [low, high]
    assert pack.best(1)[0] is high
