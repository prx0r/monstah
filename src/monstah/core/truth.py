"""Truth layer firewall.

The critical rule: a value's epistemic layer is part of its type, so it can
never be silently promoted. The content layer must not decide what is true;
and Open5e / D&D combat numbers are game-proxy values, never scientific
reconstruction state.

    EvidenceTrait  (from a source)
    !=
    ReconstructionParameter  (inferred / modelled from evidence)
    !=
    SimulationParameter  (used to run the engine)
    !=
    GameProxyParameter  (Open5e statblock — content machine only)
    !=
    NarrativeProjection  (what the episode claims to the audience)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Layer(str, Enum):
    EVIDENCE = "evidence"
    RECONSTRUCTION = "reconstruction"
    SIMULATION = "simulation"
    GAME_PROXY = "game_proxy"
    NARRATIVE = "narrative"

    @property
    def is_scientific(self) -> bool:
        """Layers that may appear in scientific reconstruction state."""
        return self in (Layer.EVIDENCE, Layer.RECONSTRUCTION, Layer.SIMULATION)

    @property
    def is_game_proxy(self) -> bool:
        return self is Layer.GAME_PROXY


class Status(str, Enum):
    OBSERVED = "OBSERVED"
    DIRECT_MEASUREMENT = "DIRECT_MEASUREMENT"
    LITERATURE_ESTIMATE = "LITERATURE_ESTIMATE"
    INFERRED = "INFERRED"
    MODELLED = "MODELLED"
    GAME_PROXY = "GAME_PROXY"
    SPECULATIVE = "SPECULATIVE"


@dataclass
class TypedValue:
    """A value pinned to one epistemic layer. The firewall unit."""

    layer: Layer
    value: Any
    unit: str = ""
    status: str = Status.INFERRED.value
    source: str = ""  # provenance locator
    confidence: float = 0.0

    def promote(self, target: Layer) -> "TypedValue":
        """Explicit, auditable promotion across the firewall (never implicit)."""
        if target == self.layer:
            return self
        if not self.layer.is_scientific or not target.is_scientific:
            raise ValueError(
                f"blocked promotion {self.layer.value} -> {target.value}: "
                "scientific/evidence layers cannot cross into game-proxy/narrative "
                "except through an explicit, labeled projection"
            )
        return TypedValue(
            layer=target,
            value=self.value,
            unit=self.unit,
            status=Status.MODELLED.value,
            source=self.source,
            confidence=self.confidence,
        )


@dataclass
class TaxonFacts:
    """A taxon's typed values, held apart by epistemic layer."""

    evidence: dict[str, TypedValue] = field(default_factory=dict)
    reconstruction: dict[str, TypedValue] = field(default_factory=dict)
    simulation: dict[str, TypedValue] = field(default_factory=dict)
    game_proxy: dict[str, TypedValue] = field(default_factory=dict)

    def add(self, layer: Layer, key: str, tv: TypedValue) -> None:
        tv.layer = layer
        getattr(self, layer.value)[key] = tv

    def evidence_flat(self) -> dict[str, Any]:
        return {k: v.value for k, v in self.evidence.items()}

    def reconstruction_flat(self) -> dict[str, Any]:
        return {k: v.value for k, v in self.reconstruction.items()}

    def scientific_flat(self) -> dict[str, Any]:
        """Everything the scientific stack may rely on (never game proxy)."""
        out = {}
        for t in (self.evidence, self.reconstruction, self.simulation):
            out.update({k: v.value for k, v in t.items()})
        return out

    def game_proxy_flat(self) -> dict[str, Any]:
        return {k: v.value for k, v in self.game_proxy.items()}
