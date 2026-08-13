"""Evidence world extension.

Synthetic worlds *generate* truth. Evidence worlds must *reconstruct* truth
from sources. Every factual property is an assertion carrying provenance,
status and uncertainty; nothing is assumed precise.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from ..core.models import Reference, new_id


class ClaimStatus(str, Enum):
    OBSERVED = "OBSERVED"
    LITERATURE_ESTIMATE = "LITERATURE_ESTIMATE"
    INFERRED = "INFERRED"
    MODELLED = "MODELLED"
    SPECULATIVE = "SPECULATIVE"


class Source(BaseModel):
    """A retrievable provenance endpoint (API record, paper, dataset)."""

    id: str = Field(default_factory=new_id)
    namespace: str
    external_id: str
    type: str = "unknown"  # paper | api_record | dataset | ...
    locator: str = ""  # DOI, URL, etc.
    title: str = ""
    access_date: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class Provenance(BaseModel):
    """Where a claim came from, exactly."""

    source: Reference
    source_locator: str = ""  # page/row/figure within the source
    method: str = ""  # how the value was derived
    accessed: str = ""


class Uncertainty(BaseModel):
    """Value + honest shape of the error, not a fake point estimate."""

    kind: str = "point"
    value: Any = None
    distribution: str = ""
    median: float | None = None
    lower: float | None = None
    upper: float | None = None
    unit: str = ""
    notes: str = ""

    @property
    def summary(self) -> str:
        if self.kind == "distribution":
            return f"{self.median} [{self.lower}, {self.upper}] {self.unit}".strip()
        return f"{self.value} {self.unit}".strip()


class Claim(BaseModel):
    """A candidate statement extracted from a source, before verification."""

    id: str = Field(default_factory=new_id)
    entity: Reference
    trait: str
    statement: str
    source: Reference
    status: ClaimStatus = ClaimStatus.INFERRED
    confidence: float = 0.0
    raw: str = ""


class Assertion(BaseModel):
    """A verified, versioned factual property attached to an entity."""

    id: str = Field(default_factory=new_id)
    entity: Reference
    trait: str
    value: Any = None
    uncertainty: Uncertainty = Field(default_factory=Uncertainty)
    status: ClaimStatus = ClaimStatus.INFERRED
    confidence: float = 0.0
    provenance: Provenance = Field(default_factory=Provenance)
    version: str = ""

    @property
    def summary(self) -> str:
        return f"{self.entity.uri}.{self.trait} ~ {self.uncertainty.summary} [{self.status.value}]"


class RelationAssertion(BaseModel):
    """A verified edge claim (eats, hosts, overlaps...)."""

    id: str = Field(default_factory=new_id)
    relation: str
    subject: Reference
    object: Reference
    status: ClaimStatus = ClaimStatus.INFERRED
    confidence: float = 0.0
    provenance: Provenance = Field(default_factory=Provenance)


class Reconstruction(BaseModel):
    """A versioned model of an entity built from many assertions."""

    id: str = Field(default_factory=new_id)
    entity: Reference
    version: str = "R1"
    assertions: list[str] = Field(default_factory=list)
    parameters: dict[str, Any] = Field(default_factory=dict)
    assumptions: dict[str, Any] = Field(default_factory=dict)
    supersedes: str | None = None
    superseded_by: str | None = None

    def bump(self) -> "Reconstruction":
        """Create the next version, superseding this one."""
        import re

        n = int(re.search(r"(\d+)$", self.version).group(1)) + 1
        nxt = self.model_copy(
            deep=True,
            update={"version": f"R{n}", "supersedes": self.version, "superseded_by": None},
        )
        self.superseded_by = nxt.version
        return nxt
