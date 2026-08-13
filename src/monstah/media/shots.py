"""Shot compiler (§36) and asset architecture (§37).

Converts canonical events into media instructions. The video model never gets
to invent outcomes the simulation didn't produce — shots are constrained by
canonical event records and versioned entity/environment assets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..core.models import Shot


@dataclass
class EntityVersion:
    """A specific reconstruction version used for a shot."""

    entity: str
    version: str
    asset_uri: str = ""


@dataclass
class ShotSpec:
    index: int
    entities: list[EntityVersion] = field(default_factory=list)
    environment: str = ""
    event: str = ""
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
                "constraints": self.constraints,
            },
            duration=self.duration,
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

    Each distinct event becomes a shot; the shot inherits the entity/environment
    versions but is constrained by what the event actually records.
    """
    shots: list[ShotSpec] = []
    for i, ev in enumerate(event_log):
        constraint = f"rendered event '{ev.get('action', '')}' ({ev.get('detail', '')}) as logged; no unlogged outcomes"
        shots.append(
            ShotSpec(
                index=i,
                entities=list(entity_versions),
                environment=environment,
                event=f"{ev.get('actor', '')}:{ev.get('action', '')}",
                start_state={"t": ev.get("t", 0.0)},
                end_state={"t": ev.get("t", 0.0) + duration},
                camera=camera,
                duration=duration,
                constraints=[constraint],
            )
        )
    return shots
