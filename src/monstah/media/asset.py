"""Canonical asset layer: image discovery, license policy, ranking.

SOURCE IMAGE != CANONICAL RECONSTRUCTION. For extant taxa a source photo can
directly represent the animal; for extinct taxa a museum photo / fossil plate /
paleoart is EVIDENCE, and the approved `TREX_RECON_R17` is the thing LTX animates.

License is part of asset identity. We store it independently from occurrence data.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AssetRole(str, Enum):
    OBSERVATIONAL_REFERENCE = "OBSERVATIONAL_REFERENCE"
    FOSSIL_REFERENCE = "FOSSIL_REFERENCE"
    ANATOMICAL_REFERENCE = "ANATOMICAL_REFERENCE"
    ENVIRONMENT_REFERENCE = "ENVIRONMENT_REFERENCE"
    HISTORICAL_RECONSTRUCTION = "HISTORICAL_RECONSTRUCTION"
    CANONICAL_RECONSTRUCTION = "CANONICAL_RECONSTRUCTION"
    EDITORIAL = "EDITORIAL"


class EpistemicStatus(str, Enum):
    OBSERVED_PHOTOGRAPH = "OBSERVED_PHOTOGRAPH"
    PRIMARY_SPECIMEN_IMAGE = "PRIMARY_SPECIMEN_IMAGE"
    HISTORICAL_ILLUSTRATION = "HISTORICAL_ILLUSTRATION"
    MODERN_RECONSTRUCTION = "MODERN_RECONSTRUCTION"
    GENERATED_RECONSTRUCTION = "GENERATED_RECONSTRUCTION"


# --- license policy ---------------------------------------------------------
# ALLOW / REVIEW / REJECT tiers drive usability scoring.
ALLOWED_LICENSES = {
    "public-domain", "pd", "cc0", "cc-by", "cc-by-sa", "cc-by-4.0", "cc-by-sa-4.0",
    "cc0-1.0", "public domain", "no known copyright restrictions",
}
REVIEW_LICENSES = {
    "cc-by-nc", "cc-by-nc-sa", "cc-by-nc-nd", "gfdl", "cc-by-nd",
}
REJECT_MARKERS = ("all rights reserved", "all-rights-reserved", "proprietary", "copyrighted")


def license_usability(license_text: str) -> float:
    """1.0 ALLOW, 0.5 REVIEW, 0.0 REJECT/UNKNOWN. Nothing is assumed reusable."""
    t = (license_text or "").strip().lower().replace(" ", "-")
    if not t:
        return 0.0
    if any(m in t for m in ("all-rights-reserved", "proprietary", "copyrighted", "unknown", "unclear")):
        return 0.0
    # unconditional reuse
    if t in ("public-domain", "pd", "cc0", "cc0-1.0", "no-known-copyright-restrictions", "public-domain-mark"):
        return 1.0
    if t.startswith("cc0"):
        return 1.0
    # CC BY / CC BY-SA allow (any version suffix); NC/ND variants review
    if t.startswith("cc-by") and not any(x in t for x in ("-nc", "-nd")):
        return 1.0
    # recognized restricted
    if any(x in t for x in ("-nc", "-nd", "gfdl")):
        return 0.5
    return 0.0  # unrecognized non-empty license -> REJECT/UNKNOWN, never REVIEW


def license_tier(license_text: str) -> str:
    u = license_usability(license_text)
    return "ALLOW" if u >= 1.0 else ("REVIEW" if u >= 0.5 else "REJECT")


# --- asset candidate ---------------------------------------------------------
class AssetCandidate(BaseModel):
    """A discovered, license-filtered image candidate."""

    id: str = ""
    entity_id: str = ""
    provider: str = ""
    provider_id: str = ""
    asset_type: str = "image"

    original_uri: str = ""
    preview_uri: str = ""

    creator: str = ""
    license: str = ""
    attribution: str = ""
    source_url: str = ""

    taxon_id: str = ""
    taxonomic_confidence: float = 0.0

    width: int = 0
    height: int = 0

    role: AssetRole = AssetRole.OBSERVATIONAL_REFERENCE
    epistemic_status: EpistemicStatus = EpistemicStatus.OBSERVED_PHOTOGRAPH
    view: str = ""  # lateral | dorsal | front | three_quarter | detail | habitat | ...

    # ranking inputs (0..1 each), defaulted to neutral
    image_quality: float = 0.5
    viewpoint_value: float = 0.5
    provenance_quality: float = 0.5
    reconstruction_relevance: float = 0.5

    score: float = 0.0

    def compute_score(self) -> float:
        """Not popularity — evidence fit."""
        self.score = (
            self.taxonomic_confidence
            * license_usability(self.license)
            * self._resolution_factor()
            * self.image_quality
            * self.viewpoint_value
            * self.provenance_quality
            * self.reconstruction_relevance
        )
        return self.score

    def _resolution_factor(self) -> float:
        longest = max(self.width, self.height)
        if longest == 0:
            return 0.3
        return min(1.0, longest / 1200.0)


class AssetPack(BaseModel):
    """A curated reference pack for one entity (what LTX gets conditioned on)."""

    entity_id: str
    reconstruction_version: str = "R1"
    role: AssetRole = AssetRole.OBSERVATIONAL_REFERENCE
    candidates: list[AssetCandidate] = Field(default_factory=list)

    def best(self, n: int = 5) -> list[AssetCandidate]:
        for c in self.candidates:
            c.compute_score()
        return sorted(self.candidates, key=lambda c: c.score, reverse=True)[:n]
