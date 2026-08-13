"""Identifier crosswalk.

Same species appears under many namespaces (pbdb, gbif, ott, eol, worms,
wikidata). Names change; identifiers let us join the graph. Treat names as
labels, never as identity.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..core.models import Reference

# Canonical external namespaces used across the evidence domains.
PBDB = "pbdb"
GBIF = "gbif"
OTT = "ott"
EOL = "eol"
WORMS = "worms"
WIKIDATA = "wikidata"
OPENALEX = "openalex"
MACROSTRAT = "macrostrat"
OBIS = "obis"

NAMESPACES = (PBDB, GBIF, OTT, EOL, WORMS, WIKIDATA, OPENALEX, MACROSTRAT, OBIS)


class Crosswalk(BaseModel):
    """Maps a single logical entity to its IDs in every namespace."""

    entity: Reference | None = None
    ids: dict[str, str] = Field(default_factory=dict)
    names: list[str] = Field(default_factory=list)

    def get(self, namespace: str) -> str | None:
        return self.ids.get(namespace)

    def set(self, namespace: str, value: str) -> None:
        self.ids[namespace] = value

    @property
    def references(self) -> list[Reference]:
        return [Reference(namespace=k, key=v) for k, v in self.ids.items() if v]
