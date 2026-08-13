"""Evidence builder: turn ingested facts into Source / Claim / Assertion /
Reconstruction objects.

Every factual property becomes an assertion with provenance. The reconstruction
is a versioned object built from those assertions; game-proxy combat stats are
recorded as labeled simulation parameters, never as evidence.
"""

from __future__ import annotations

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


def assertions_from_facts(
    entity: Reference,
    facts: TaxonFacts,
    source: Source,
) -> list[Assertion]:
    """Convert evidence-layer facts into provenance-bearing assertions.

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
                    method=tv.source,
                ),
                version="R1",
            )
        )
    return out


def build_reconstruction(
    entity: Reference,
    facts: TaxonFacts,
    source: Source,
    *,
    version: str = "R1",
    supersedes: str | None = None,
) -> Reconstruction:
    """Assemble a versioned Reconstruction from a taxon's evidence + labeled
    simulation parameters. Game-proxy values are recorded under an explicit
    `game_proxy` parameter key so they can never be mistaken for evidence."""
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
