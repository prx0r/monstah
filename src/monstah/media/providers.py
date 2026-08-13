"""Provider-agnostic image discovery + resolver.

Like LTX, the image system is provider-agnostic: `ImageResolver` merges
candidates from every provider, then `AssetPack` scores them by evidence fit.
License is part of asset identity and stored independently.

Providers:
  - GBIF         (extant: observational photos + occurrence metadata)
  - iNaturalist  (extant: research-grade open-license photos, up to 2048px)
  - Wikimedia    (museum skeletons, fossils, plates, diagrams, public-domain)
  - BHL          (historic scientific plates — REQUIRES an API key)
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import httpx

from ..config import get_settings
from .asset import (
    ALLOWED_LICENSES,
    AssetCandidate,
    AssetRole,
    EpistemicStatus,
    license_tier,
    license_usability,
)

_DEFAULT_CACHE = Path(get_settings().pbdb_cache).expanduser() / "images"


class ImageProvider(ABC):
    name = "base"

    def __init__(self, *, cache_dir: str | None = None, offline: bool = False) -> None:
        self._cache = Path(cache_dir or _DEFAULT_CACHE)
        self.offline = offline
        self._client = httpx.Client(
            timeout=25,
            follow_redirects=True,
            headers={"User-Agent": "monstah/0.1 (world reconstruction engine)"},
        )

    @abstractmethod
    def search(self, entity: str, query: str = "") -> list[AssetCandidate]:
        """Return license-filtered candidate images for an entity."""

    def _cache_get(self, key: str) -> Any | None:
        fp = self._cache / f"{self.name}_{hashlib.sha1(key.encode()).hexdigest()[:16]}.json"
        if fp.exists():
            return json.loads(fp.read_text())
        return None

    def _cache_put(self, key: str, data: Any) -> None:
        self._cache.mkdir(parents=True, exist_ok=True)
        fp = self._cache / f"{self.name}_{hashlib.sha1(key.encode()).hexdigest()[:16]}.json"
        fp.write_text(json.dumps(data))

    def close(self) -> None:
        self._client.close()


# --- GBIF -------------------------------------------------------------------
class GbifImageProvider(ImageProvider):
    name = "gbif"

    def search(self, entity: str, query: str = "") -> list[AssetCandidate]:
        if self.offline:
            return []
        key = f"species/{entity}"
        cached = self._cache_get(key)
        if cached is None:
            r = self._client.get("https://api.gbif.org/v1/species/search", params={"q": entity, "limit": 1})
            cached = r.json()["results"][0]["key"] if r.json().get("results") else None
            self._cache_put(key, cached)
        if not cached:
            return []
        return self._occurrences_for_taxon(cached, entity)

    def _occurrences_for_taxon(self, taxon_key: int, entity: str) -> list[AssetCandidate]:
        key = f"occ/{taxon_key}"
        cached = self._cache_get(key)
        if cached is None:
            r = self._client.get(
                "https://api.gbif.org/v1/occurrence/search",
                params={"taxonKey": taxon_key, "mediaType": "StillImage", "limit": 50},
            )
            cached = r.json().get("results", [])
            self._cache_put(key, cached)
        out: list[AssetCandidate] = []
        for occ in cached:
            for m in occ.get("media", []) or []:
                lic = m.get("license") or occ.get("license", "")
                if license_usability(lic) <= 0:
                    continue
                out.append(
                    AssetCandidate(
                        provider=self.name,
                        provider_id=str(occ.get("key", "")),
                        entity_id=entity,
                        original_uri=m.get("identifier", ""),
                        preview_uri=m.get("identifier", ""),
                        creator=m.get("creator", ""),
                        license=lic,
                        source_url=occ.get("references", ""),
                        taxon_id=str(taxon_key),
                        taxonomic_confidence=0.9,
                        width=m.get("width", 0),
                        height=m.get("height", 0),
                        role=AssetRole.OBSERVATIONAL_REFERENCE,
                        epistemic_status=EpistemicStatus.OBSERVED_PHOTOGRAPH,
                        provenance_quality=0.8,
                    )
                )
        return out


# --- iNaturalist ------------------------------------------------------------
class INaturalistProvider(ImageProvider):
    name = "inaturalist"

    def search(self, entity: str, query: str = "") -> list[AssetCandidate]:
        if self.offline:
            return []
        key = f"obs/{entity}"
        cached = self._cache_get(key)
        if cached is None:
            r = self._client.get(
                "https://api.inaturalist.org/v1/observations",
                params={"taxon_name": entity, "quality_grade": "research", "photos": "true", "per_page": 20},
            )
            cached = r.json().get("results", [])
            self._cache_put(key, cached)
        out: list[AssetCandidate] = []
        for obs in cached:
            taxon = obs.get("taxon", {}) or {}
            for p in obs.get("photos", []) or []:
                lic = (p.get("license_code") or "").replace("cc-by-", "cc-by-") if p.get("license_code") else ""
                if license_usability(lic) <= 0:
                    continue
                # actually select the open-data original (size suffix -> /original)
                uri = p.get("url", "")
                uri = uri.replace("/square", "/original").replace("/medium", "/original").replace("/small", "/original")
                urls = p.get("original_dimensions", {})
                out.append(
                    AssetCandidate(
                        provider=self.name,
                        provider_id=str(p.get("id", "")),
                        entity_id=entity,
                        original_uri=uri,
                        preview_uri=p.get("url", ""),
                        creator=p.get("attribution", ""),
                        license=lic,
                        source_url=obs.get("uri", ""),
                        taxon_id=str(taxon.get("id", "")),
                        taxonomic_confidence=0.85,
                        width=urls.get("width", 0),
                        height=urls.get("height", 0),
                        role=AssetRole.OBSERVATIONAL_REFERENCE,
                        epistemic_status=EpistemicStatus.OBSERVED_PHOTOGRAPH,
                        provenance_quality=0.85,
                        image_quality=0.8,
                    )
                )
        return out


# --- Wikimedia Commons ------------------------------------------------------
class WikimediaProvider(ImageProvider):
    name = "wikimedia"

    def search(self, entity: str, query: str = "") -> list[AssetCandidate]:
        if self.offline:
            return []
        key = f"commons/{entity}"
        cached = self._cache_get(key)
        if cached is None:
            r = self._client.get(
                "https://commons.wikimedia.org/w/api.php",
                params={"action": "query", "format": "json", "list": "search", "srsearch": entity, "srlimit": 10},
            )
            titles = [h["title"] for h in r.json()["query"]["search"]]
            cached = self._imageinfo(titles)
            self._cache_put(key, cached)
        out: list[AssetCandidate] = []
        for info in cached:
            lic = (info.get("extmetadata") or {}).get("LicenseShortName", {}).get("value", "")
            if license_usability(lic) <= 0:
                continue
            role, epistemic, tconf = _classify_wikimedia(info.get("title", ""))
            meta = info.get("extmetadata") or {}
            out.append(
                AssetCandidate(
                    provider=self.name,
                    provider_id=info.get("title", ""),
                    entity_id=entity,
                    original_uri=info.get("url", ""),  # raw file, not the description page
                    preview_uri=info.get("thumburl", ""),
                    creator=meta.get("Artist", {}).get("value", ""),
                    license=lic,
                    source_url=info.get("descriptionurl", ""),
                    taxon_id="",
                    taxonomic_confidence=tconf,
                    width=info.get("width", 0),
                    height=info.get("height", 0),
                    role=role,
                    epistemic_status=epistemic,
                    provenance_quality=0.7,
                    viewpoint_value=0.6,
                )
            )
        return out

    def _imageinfo(self, titles: list[str]) -> list[dict]:
        if not titles:
            return []
        r = self._client.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query", "format": "json", "prop": "imageinfo", "titles": "|".join(titles),
                "iiprop": "url|size|extmetadata", "iiurlwidth": "1200",
            },
        )
        pages = (r.json().get("query") or {}).get("pages", {})
        return [p["imageinfo"][0] for p in pages.values() if p.get("imageinfo")]


def _classify_wikimedia(title: str) -> tuple[AssetRole, EpistemicStatus, float]:
    """Lightweight title-based classification of a Commons file.

    We do NOT blanket-tag every hit as a fossil specimen.
    """
    t = title.lower()
    if any(k in t for k in ("skull", "skeleton", "fossil", "specimen", "bone", "tooth")):
        return AssetRole.FOSSIL_REFERENCE, EpistemicStatus.PRIMARY_SPECIMEN_IMAGE, 0.9
    if any(k in t for k in ("illustration", "drawing", "reconstruction", "artwork", "plate", "engraving", "painting")):
        return AssetRole.ANATOMICAL_REFERENCE, EpistemicStatus.HISTORICAL_ILLUSTRATION, 0.7
    if any(k in t for k in ("map", "range", "distribution", "diagram")):
        return AssetRole.ENVIRONMENT_REFERENCE, EpistemicStatus.OBSERVED_PHOTOGRAPH, 0.6
    if any(k in t for k in ("habitat", "environment", "location", "beach", "forest", "ocean")):
        return AssetRole.ENVIRONMENT_REFERENCE, EpistemicStatus.OBSERVED_PHOTOGRAPH, 0.6
    # default: likely a photograph
    return AssetRole.OBSERVATIONAL_REFERENCE, EpistemicStatus.OBSERVED_PHOTOGRAPH, 0.6


# --- BHL (key-gated) --------------------------------------------------------
class BhlProvider(ImageProvider):
    """Historic scientific plates. BHL now requires an API access token."""

    name = "bhl"

    def __init__(self, *, api_key: str = "", **kw: Any) -> None:
        super().__init__(**kw)
        self.api_key = api_key

    def search(self, entity: str, query: str = "") -> list[AssetCandidate]:
        if self.offline:
            return []
        if not self.api_key:
            raise RuntimeError("BHL requires an API key (set BHL_API_KEY); skipping historic plates")
        r = self._client.get(
            "https://www.biodiversitylibrary.org/api3",
            params={"op": "PageSearch", "term": entity, "format": "json", "apikey": self.api_key},
        )
        data = r.json()
        out: list[AssetCandidate] = []
        for item in (data.get("Result", {}).get("Page", []) or []):
            url = item.get("FullSizeImageUrl", "")
            if not url:
                continue
            # read actual rights metadata; do NOT manufacture public-domain
            rights = item.get("RightsStatement", "") or item.get("RightsHolder", "") or ""
            lic = "public-domain" if "public domain" in rights.lower() else "unknown"
            if license_usability(lic) <= 0:
                continue
            out.append(
                AssetCandidate(
                    provider=self.name,
                    provider_id=str(item.get("PageID", "")),
                    entity_id=entity,
                    original_uri=url,
                    preview_uri=item.get("ThumbnailUrl", ""),
                    creator=item.get("Authors", ""),
                    license=lic,
                    source_url=item.get("PageUrl", ""),
                    taxonomic_confidence=0.6,
                    role=AssetRole.HISTORICAL_RECONSTRUCTION,
                    epistemic_status=EpistemicStatus.HISTORICAL_ILLUSTRATION,
                    provenance_quality=0.7,
                )
            )
        return out


# --- resolver ---------------------------------------------------------------
class ImageResolver:
    """Merge + score SOURCE candidates across all providers.

    Source assets are EVIDENCE/reference material, never direct LTX conditioning
    for extinct taxa. Role assigned by the provider is preserved unless an
    explicit `role` override is requested.
    """

    def __init__(self, providers: list[ImageProvider] | None = None, *, offline: bool = False) -> None:
        self.offline = offline
        if providers is None:
            self.providers: list[ImageProvider] = [
                GbifImageProvider(offline=offline),
                INaturalistProvider(offline=offline),
                WikimediaProvider(offline=offline),
            ]
        else:
            self.providers = providers

    def search(self, entity: str, *, role: AssetRole | None = None) -> list[AssetCandidate]:
        import logging

        cands: list[AssetCandidate] = []
        for p in self.providers:
            try:
                for c in p.search(entity):
                    # preserve the provider-assigned role; only override if the
                    # caller explicitly requests one (with a classification intent)
                    if role is not None:
                        c.role = role
                    c.compute_score()
                    cands.append(c)
            except Exception as e:
                logging.getLogger("monstah.media").warning("provider %s failed for %r: %s", p.name, entity, e)
                continue
        cands.sort(key=lambda c: c.score, reverse=True)
        return cands

    def best(self, entity: str, n: int = 5, **kw: Any) -> list[AssetCandidate]:
        return self.search(entity, **kw)[:n]

    def close(self) -> None:
        for p in self.providers:
            try:
                p.close()
            except Exception:
                pass


class CanonicalAssetResolver:
    """Resolves APPROVED canonical reconstruction assets for an entity+version.

    SOURCE IMAGE != CANONICAL RECONSTRUCTION. The render layer must ask
    `canonical_assets.resolve(entity, version)`, NOT `ImageResolver.best(name)`.

    - Extinct taxa: NEVER returns raw source references; only a stored approved
      canonical reconstruction (e.g. R2 visual_reconstructions) is eligible.
    - Extant taxa: an explicit policy MAY allow observational source photos to
      represent canonical morphology.
    """

    def __init__(
        self,
        *,
        source: ImageResolver | None = None,
        store=None,
        allow_observational_as_canonical: bool = False,
    ) -> None:
        self.source = source or ImageResolver()
        self.store = store  # optional R2/local store of canonical reconstructions
        self.allow_observational_as_canonical = allow_observational_as_canonical

    def resolve(self, entity: str, version: str = "R1", *, extinct: bool = True) -> list[AssetCandidate]:
        """Return canonical reconstruction references eligible for LTX I2V."""
        # 1. approved canonical reconstruction assets (the only thing LTX may use)
        canonical = self._load_canonical(entity, version)
        if canonical:
            return canonical
        # 2. extinct taxa: no fallback to raw source references, ever
        if extinct:
            return []
        # 3. extant taxa: explicit policy may allow observational morphology
        if self.allow_observational_as_canonical:
            out = []
            for c in self.source.best(entity, n=3):
                c.role = AssetRole.CANONICAL_RECONSTRUCTION
                c.compute_score()
                out.append(c)
            return out
        return []

    def _load_canonical(self, entity: str, version: str) -> list[AssetCandidate]:
        if self.store is None:
            return []
        try:
            uri = self.store.canonical_uri(entity, version)
            if not uri:
                return []
            return [
                AssetCandidate(
                    provider="canonical",
                    provider_id=f"{entity}:{version}",
                    entity_id=entity,
                    original_uri=uri,
                    preview_uri=uri,
                    license="project-internal",
                    role=AssetRole.CANONICAL_RECONSTRUCTION,
                    epistemic_status=EpistemicStatus.GENERATED_RECONSTRUCTION,
                    reconstruction_relevance=1.0,
                    provenance_quality=1.0,
                )
            ]
        except Exception:
            return []
