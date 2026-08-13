"""GloBI (Global Biotic Interactions) client.

Normalizes species interaction data -> ecological *edges*. Query a taxon and get
what it eats, what eats it, hosts, parasites, competitors, and the underlying
source references. For heavy offline work GloBI publishes downloadable
integrated datasets (loadable into DuckDB / SQLite).
"""

from __future__ import annotations

from typing import Any

from .base import HttpApi

# GloBI Elton interactions provide citation-traceable edges.
INTERACTION_SOURCES = {
    "eats": "http://purl.obolibrary.org/obo/RO_0002470",
    "prey of": "http://purl.obolibrary.org/obo/RO_0002471",
    "host of": "http://purl.obolibrary.org/obo/RO_0002453",
    "parasite of": "http://purl.obolibrary.org/obo/RO_0002444",
    "visited": "http://purl.obolibrary.org/obo/RO_0002618",
    "pollinates": "http://purl.obolibrary.org/obo/RO_0002455",
}


class GlobiClient(HttpApi):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__("https://api.globalbioticinteractions.org", **kwargs)

    def interactions(
        self,
        taxon: str,
        *,
        interaction_type: str | None = None,
        fields: str = "source_taxon_name,target_taxon_name,interaction_type,reference_doi,reference_url",
        limit: int = 100,
    ) -> list[dict]:
        params: dict[str, Any] = {
            "sourceTaxon": taxon,
            "fields": fields,
            "limit": limit,
            "noContext": "true",
        }
        if interaction_type:
            params["interactionType"] = interaction_type
        data = self.get("interaction", params)
        cols = data.get("columns", [])
        rows = data.get("data", [])
        return [dict(zip(cols, row)) for row in rows]

    def eats(self, taxon: str, *, limit: int = 100) -> list[dict]:
        """What does `taxon` eat? (directed out-edges of eats)"""
        return self.interactions(taxon, interaction_type="eats", limit=limit)

    def prey_of(self, taxon: str, *, limit: int = 100) -> list[dict]:
        """Who eats `taxon`? (prey-of edges)"""
        return self.interactions(taxon, interaction_type="prey of", limit=limit)

    def _edges(self, rows: list[dict]) -> list[dict]:
        out = []
        for r in rows:
            out.append(
                {
                    "source": r.get("source_taxon_name"),
                    "target": r.get("target_taxon_name"),
                    "interaction": r.get("interaction_type"),
                    "reference_doi": r.get("reference_doi"),
                    "reference_url": r.get("reference_url"),
                }
            )
        return out
