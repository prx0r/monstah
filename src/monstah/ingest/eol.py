"""EOL TraitBank client: structured organism traits for the capability layer."""

from __future__ import annotations

from typing import Any

from .base import HttpApi


class EolClient(HttpApi):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__("https://api.eol.org", **kwargs)

    def search(self, q: str, *, limit: int = 10) -> list[dict]:
        return self.get("search/1.0.json", {"q": q, "page": 1, "per_page": limit}).get("results", [])

    def taxon_page(self, eol_page_id: int) -> dict:
        return self.get(f"pages/1.0/{eol_page_id}.json", {"images": 0})

    def traits(self, eol_page_id: int) -> list[dict]:
        """TraitBank data for a page: body mass/length, habitat, diet, locomotion..."""
        page = self.get(f"pages/1.0/{eol_page_id}.json", {"images": 0})
        return page.get("data_objects", []) if isinstance(page, dict) else []

    def data_search(self, q: str = "mass", *, eol_page_id: int | None = None) -> list[dict]:
        params: dict[str, Any] = {"q": q, "per_page": 50}
        if eol_page_id:
            params["id"] = eol_page_id
        return self.get("data/1.0/search.json", params).get("results", [])
