"""Evidence builder: turn ingested facts into Source / Claim / Assertion /
Reconstruction objects.

Every factual property becomes an assertion with provenance. The reconstruction
is a versioned object built from those assertions; game-proxy combat stats are
recorded as labeled simulation parameters, never as evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..core.models import Reference
from ..core.truth import Layer, TaxonFacts
from .models import (
    Assertion,
    Claim,
    ClaimStatus,
    Provenance,
    Reconstruction,
    Source,
    Uncertainty,
)


def source_from(
    namespace: str,
    external_id: str,
    *,
    type: str = "api_record",
    locator: str = "",
    title: str = "",
) -> Source:
    return Source(
        namespace=namespace,
        external_id=external_id,
        type=type,
        locator=locator,
        title=title,
    )


def claims_from_facts(
    entity: Reference,
    facts: TaxonFacts,
    source: Source,
) -> list[Claim]:
    """Extract raw candidate claims from evidence facts (source -> claim).

    Game-proxy values are excluded: they are simulation parameters, not claims
    about the entity.
    """
    out: list[Claim] = []
    for trait, tv in facts.evidence.items():
        out.append(
            Claim(
                entity=entity,
                trait=trait,
                statement=f"{entity.key} {trait} ≈ {tv.value}",
                source=Reference(namespace=source.namespace, key=source.external_id),
                status=ClaimStatus(tv.status) if tv.status in ClaimStatus._value2member_map_ else ClaimStatus.INFERRED,
                confidence=tv.confidence,
                raw=str(tv.value),
            )
        )
    return out


def assertions_from_facts(
    entity: Reference,
    facts: TaxonFacts,
    source: Source,
) -> list[Assertion]:
    """Adjudicate evidence facts into provenance-bearing assertions.

    Game-proxy values are intentionally excluded: they are simulation
    parameters, not evidence about the entity.
    """
    out: list[Assertion] = []
    for trait, tv in facts.evidence.items():
        out.append(
            Assertion(
                entity=entity,
                trait=trait,
                value=tv.value,
                uncertainty=Uncertainty(value=tv.value, unit=tv.unit),
                status=ClaimStatus(tv.status) if tv.status in ClaimStatus._value2member_map_ else ClaimStatus.INFERRED,
                confidence=tv.confidence,
                provenance=Provenance(
                    source=Reference(namespace=source.namespace, key=source.external_id),
                    method="evidence_fact",
                ),
                version="R1",
            )
        )
    return out


@dataclass
class EvidencePack:
    """The full persistable evidence chain for one entity: source → claim → assertion."""

    entity: Reference
    source: Source
    claims: list[Claim]
    assertions: list[Assertion]

    def assertion_by_id(self) -> dict[str, Assertion]:
        return {a.id: a for a in self.assertions}


def build_evidence_pack(
    entity: Reference,
    facts: TaxonFacts,
    source: Source,
) -> EvidencePack:
    """Build source → claims → assertions in one pass with immutable IDs."""
    claims = claims_from_facts(entity, facts, source)
    assertions = assertions_from_facts(entity, facts, source)
    return EvidencePack(entity=entity, source=source, claims=claims, assertions=assertions)


def build_reconstruction(
    entity: Reference,
    facts: TaxonFacts,
    source: Source,
    *,
    version: str = "R1",
    supersedes: str | None = None,
    assertions: list[Assertion] | None = None,
) -> Reconstruction:
    """Assemble a versioned Reconstruction from a taxon's evidence + labeled
    simulation parameters. Game-proxy values are recorded under an explicit
    `game_proxy` parameter key so they can never be mistaken for evidence.

    If `assertions` is provided it must be the persisted Assertion objects, so
    the Reconstruction references the SAME immutable IDs that were stored.
    """
    if assertions is None:
        assertions = assertions_from_facts(entity, facts, source)
    rec = Reconstruction(
        entity=entity,
        version=version,
        assertions=[a.id for a in assertions],
        parameters={
            "scientific": facts.scientific_flat(),
            "game_proxy": facts.game_proxy_flat(),
            "layers": {k: [x.value for x in v.values()] for k, v in facts.__dict__.items()},
        },
        assumptions={
            "game_proxy_is_simulation_proxy": True,
            "no_combat_stat_is_evidence": True,
        },
        supersedes=supersedes,
    )
    return rec
