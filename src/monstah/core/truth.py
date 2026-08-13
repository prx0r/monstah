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
        """Directed, auditable promotion. Strictly monotonic:

            EVIDENCE → RECONSTRUCTION → SIMULATION

        never upward, never across layers. Any other move is a firewall violation.
        """
        if target == self.layer:
            return self
        if target not in _ALLOWED_PROMOTIONS.get(self.layer, set()):
            raise ValueError(
                f"blocked promotion {self.layer.value} -> {target.value}: "
                "epistemic layers only advance EVIDENCE→RECONSTRUCTION→SIMULATION, "
                "and never cross into game-proxy/narrative except via a labeled projection"
            )
        return TypedValue(
            layer=target,
            value=self.value,
            unit=self.unit,
            status=Status.MODELLED.value,
            source=self.source,
            confidence=self.confidence,
        )


# Directed monotonic promotion edges. Simulation is the terminal scientific layer.
_ALLOWED_PROMOTIONS: dict[Layer, set[Layer]] = {
    Layer.EVIDENCE: {Layer.RECONSTRUCTION},
    Layer.RECONSTRUCTION: {Layer.SIMULATION},
    Layer.SIMULATION: set(),
    Layer.GAME_PROXY: set(),
    Layer.NARRATIVE: set(),
}


@dataclass
class TaxonFacts:
    """A taxon's typed values, held apart by epistemic layer."""

    evidence: dict[str, TypedValue] = field(default_factory=dict)
    reconstruction: dict[str, TypedValue] = field(default_factory=dict)
    simulation: dict[str, TypedValue] = field(default_factory=dict)
    game_proxy: dict[str, TypedValue] = field(default_factory=dict)

    def add(self, layer: Layer, key: str, tv: TypedValue) -> None:
        if tv.layer is not layer:
            raise ValueError(
                f"cannot place {tv.layer.value} value into {layer.value} bucket; "
                "TypedValue.layer is immutable and must match its container"
            )
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
