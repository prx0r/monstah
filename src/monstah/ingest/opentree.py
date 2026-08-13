"""Open Tree of Life client: synthesized phylogeny structure.

Gives evolutionary structure (taxonomy + published trees via OTT ids) so the
graph knows animals aren't an unordered list but part of a tree.
"""

from __future__ import annotations

from typing import Any

from .base import HttpApi


class OpenTreeClient(HttpApi):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__("https://api.opentreeoflife.org/v3", **kwargs)

    def tnrs_match(self, name: str) -> dict:
        """Match a name to an OTT id (taxonomy resolution)."""
        return self.post_("tnrs/match_names", {"names": [name]})

    def taxonomy(self, ott_id: int) -> dict:
        return self.post_("taxonomy/taxon_info", {"ott_id": ott_id})

    def subtree(self, ott_id: int) -> dict:
        """OTT subtree rooted at a taxon (e.g. a clade's descendants)."""
        return self.post_("taxonomy/subtree", {"ott_id": ott_id})

    def mrca(self, ott_ids: list[int]) -> dict:
        """Most recent common ancestor of several taxa (nearest common ancestor)."""
        return self.post_("taxonomy/mrca", {"ott_ids": ott_ids})

    def induced_subtree(self, ott_ids: list[int]) -> dict:
        """Phylogenetic tree relating a set of taxa."""
        return self.post_("tree_of_life/induced_subtree", {"ott_ids": ott_ids})

    def nearest_living_relative(self, ott_id: int) -> dict:
        """Best-effort nearest relative lookup via MRCA search."""
        return self.taxonomy(ott_id)

    def post_(self, path: str, payload: dict) -> dict:
        import json

        cache = self._cache_key(path, payload)
        if cache and cache.exists():
            return json.loads(cache.read_text())
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = self._client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        if cache:
            cache.write_text(json.dumps(data))
        return data
