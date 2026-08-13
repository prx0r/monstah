"""OBIS marine occurrence client (100M+ marine records)."""

from __future__ import annotations

from typing import Any

from .base import HttpApi


class ObisClient(HttpApi):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__("https://api.obis.org/v3", **kwargs)

    def occurrence(
        self,
        *,
        taxonid: int | None = None,
        scientificname: str | None = None,
        geometry: str | None = None,
        depth: str | None = None,
        limit: int = 50,
    ) -> dict:
        params: dict[str, Any] = {"limit": limit}
        if taxonid is not None:
            params["taxonid"] = taxonid
        if scientificname:
            params["scientificname"] = scientificname
        if geometry:
            params["geometry"] = geometry
        if depth:
            params["depth"] = depth
        return self.get("occurrence", params)

    def occurrences(self, **kwargs: Any) -> list[dict]:
        return self.occurrence(**kwargs).get("results", [])

    def taxon(self, aphiaid: int) -> dict:
        return self.get(f"taxon/{aphiaid}")

    def search_taxon(self, q: str) -> dict:
        return self.get("taxon", {"scientificname": q, "limit": 10})

    def statistics(self, *, geometry: str | None = None, depth: str | None = None) -> dict:
        params: dict[str, Any] = {}
        if geometry:
            params["geometry"] = geometry
        if depth:
            params["depth"] = depth
        return self.get("stats", params)
