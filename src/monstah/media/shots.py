"""Shot compiler (§36) and LTX bindings (§37, LTX production pack).

Converts canonical events into LTX ShotSpecs. The video model never gets to
invent outcomes the simulation didn't produce — every shot carries the
epistemic `canonicality` from the truth layer and explicit constraints/QA so
LTX cannot silently add facts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..core.models import Shot
from .ltx import Canonicality, ControlMode, Project, ShotBasis, ShotSpec as LtxShotSpec


@dataclass
class EntityVersion:
    """A specific reconstruction version used for a shot."""

    entity: str
    version: str
    asset_uri: str = ""


@dataclass
class ShotSpec:
    """Pipeline-level shot: an ordered event bound to versions.

    `basis` says what the shot is grounded in (SIMULATION_EVENT, RECONSTRUCTION,
    GRAPH_DERIVED...). `event_ids` reference immutable canonical events.
    """

    index: int
    entities: list[EntityVersion] = field(default_factory=list)
    environment: str = ""
    event: str = ""
    event_ids: list[str] = field(default_factory=list)
    basis: ShotBasis = ShotBasis.RECONSTRUCTION
    start_state: dict = field(default_factory=dict)
    end_state: dict = field(default_factory=dict)
    camera: str = "low tracking"
    duration: float = 5.0
    constraints: list[str] = field(default_factory=list)

    def to_core(self) -> Shot:
        return Shot(
            index=self.index,
            asset_ref=self.environment,
            camera={"style": self.camera},
            action={
                "entities": [e.__dict__ for e in self.entities],
                "event": self.event,
                "event_ids": self.event_ids,
                "basis": self.basis.value,
                "constraints": self.constraints,
            },
            duration=self.duration,
        )

    def to_ltx(
        self,
        *,
        project: Project = Project.MONSTAH,
        mode: str = "historical",
        prompt: str = "",
        aspect_ratio: str = "16:9",
    ) -> LtxShotSpec:
        from .ltx import canonicality

        entity_versions = []
        for e in self.entities:
            if isinstance(e, dict):
                entity_versions.append(f"{e.get('entity')}:{e.get('version', '')}")
            else:
                entity_versions.append(f"{e.entity}:{e.version}")
        return LtxShotSpec(
            shot_id=f"{project.value}-{self.index:03d}",
            project=project,
            canonicality=canonicality(mode, self.basis),
            entity_versions=entity_versions,
            environment_version=self.environment or None,
            event_ids=self.event_ids,
            prompt=prompt or f"A {self.camera} shot of {self.basis.value.lower()} {self.event or ''}.",
            duration_s=self.duration,
            aspect_ratio=aspect_ratio,
            control_mode=ControlMode.I2V if entity_versions else ControlMode.T2V,
            camera={"style": self.camera, "pre_state": self.start_state, "post_state": self.end_state},
            constraints=self.constraints,
        )


def compile_shots(
    *,
    entity_versions: list[EntityVersion],
    environment: str,
    event_log: list[dict],
    camera: str = "low tracking",
    duration: float = 6.0,
) -> list[ShotSpec]:
    """Map an ordered canonical event log to a shot graph.

    Each distinct event becomes a shot carrying its immutable event id and real
    pre/post state. The shot inherits the entity/environment versions but is
    constrained by what the event actually records.
    """
    shots: list[ShotSpec] = []
    for i, ev in enumerate(event_log):
        constraint = f"rendered event '{ev.get('action', '')}' as logged; no unlogged outcomes"
        eid = ev.get("event_id", f"evt:{i}")
        shots.append(
            ShotSpec(
                index=i,
                entities=list(entity_versions),
                environment=environment,
                event=f"{ev.get('actor', '')}:{ev.get('action', '')}",
                event_ids=[eid],
                basis=ShotBasis.SIMULATION_EVENT if ev.get("action") != "GRAPH" else ShotBasis.GRAPH_DERIVED,
                start_state=ev.get("pre_state", {"t": ev.get("t", 0.0)}),
                end_state=ev.get("post_state", {"t": ev.get("t", 0.0) + duration}),
                camera=camera,
                duration=duration,
                constraints=[constraint],
            )
        )
    return shots


def canonicality_for_mode(mode: str) -> Canonicality:
    """Back-compat mode-only mapping (legacy; the pipeline uses canonicality(mode,basis))."""
    if mode in ("lab", "counterfactual"):
        return Canonicality.COUNTERFACTUAL
    if mode == "historical":
        return Canonicality.CANONICAL_EVENT
    return Canonicality.RECONSTRUCTION


def to_ltx_shots(
    shots: list[ShotSpec],
    *,
    project: Project = Project.MONSTAH,
    mode: str = "historical",
) -> list[LtxShotSpec]:
    """Convert compiled shots into render-ready LTX ShotSpecs."""
    return [s.to_ltx(project=project, mode=mode) for s in shots]
