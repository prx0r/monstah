"""GBIF occurrence + species API (present-day biodiversity)."""

from __future__ import annotations

from typing import Any

from .base import HttpApi


class GbifClient(HttpApi):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__("https://api.gbif.org/v1", **kwargs)

    def species(self, key: int) -> dict:
        return self.get(f"species/{key}")

    def search_species(self, q: str, *, limit: int = 20, rank: str | None = None) -> list[dict]:
        params: dict[str, Any] = {"q": q, "limit": limit}
        if rank:
            params["rank"] = rank
        return self.get("species/search", params)["results"]

    def occurrences(
        self,
        *,
        taxon_key: int | None = None,
        scientific_name: str | None = None,
        country: str | None = None,
        depth_gt: float | None = None,
        depth_lt: float | None = None,
        limit: int = 20,
        media_type: str | None = None,
    ) -> list[dict]:
        params: dict[str, Any] = {"limit": limit}
        if taxon_key is not None:
            params["taxonKey"] = taxon_key
        if scientific_name:
            params["scientificName"] = scientific_name
        if country:
            params["country"] = country
        if depth_gt is not None:
            params["depth"] = f"{depth_gt},{depth_lt or '*'}"
        if media_type:
            params["mediaType"] = media_type
        return self.get("occurrence/search", params)["results"]

    def multimedia(self, key: int) -> list[dict]:
        return self.get(f"occurrence/{key}/media", {})["results"]

    def spatial_search(self, *, lat: float, lng: float, radius_km: float, taxon_key: int | None = None) -> list[dict]:
        params: dict[str, Any] = {"lat": lat, "lng": lng, "radius": radius_km, "limit": 50}
        if taxon_key is not None:
            params["taxonKey"] = taxon_key
        return self.get("occurrence/search", params)["results"]
