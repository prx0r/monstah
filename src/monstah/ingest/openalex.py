"""OpenAlex scholarly works client: papers behind every claim.

Returns scholarly-work/entity metadata with powerful filtering and grouping,
powering the ingest loop: taxon -> discover papers -> extract claims.
"""

from __future__ import annotations

from typing import Any

from .base import HttpApi


class OpenAlexClient(HttpApi):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__("https://api.openalex.org", **kwargs)

    def works(
        self,
        q: str | None = None,
        *,
        title_search: str | None = None,
        doi: str | None = None,
        filter_: str | None = None,
        per_page: int = 25,
        sort: str = "relevance_score:desc",
    ) -> list[dict]:
        params: dict[str, Any] = {"per-page": per_page, "sort": sort}
        if q:
            params["search"] = q
        if title_search:
            params["filter"] = f"title.search:{title_search}"
        elif filter_:
            params["filter"] = filter_
        if doi:
            params["filter"] = f"doi:{doi}"
        data = self.get("works", params)
        return data.get("results", [])

    def by_doi(self, doi: str) -> dict:
        return self.get(f"works/doi:{doi.lstrip('doi:')}")

    def author(self, author_id: str) -> dict:
        return self.get(f"authors/{author_id}")
