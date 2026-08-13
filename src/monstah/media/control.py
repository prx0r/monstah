"""ControlPlanner + deterministic control-frame compositor (MVP Phase 18-19).

Rule: the more epistemically constrained the shot, the less freedom LTX gets.
ControlPlanner maps a shot's basis to a control mode. The compositor builds
first/last-frame plates + a depth approximation from pre/post state and the
canonical assets — these are CONSTRAINTS for LTX, not final art.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..media.ltx import ShotBasis
from ..media.shot_spec2 import ShotControl, ShotSpecV2


@dataclass
class ControlFramePlate:
    view: str  # first | last
    entity_id: str
    reconstruction_version: str
    canonical_asset: str  # uri of the canonical reconstruction to composite
    state: dict[str, Any] = field(default_factory=dict)
    svg: str = ""


class ControlPlanner:
    """Choose the least-generative route that satisfies a shot."""

    def mode_for(self, shot: ShotSpecV2) -> str:
        if shot.control.preferred == "DETERMINISTIC":
            return "DETERMINISTIC"
        if shot.basis.type == ShotBasis.SIMULATION_EVENT:
            return "FIRST_LAST"
        if shot.basis.event_ids:
            return "FIRST_LAST"
        if shot.basis.type == ShotBasis.RECONSTRUCTION:
            return "I2V"
        if shot.subjects:
            return "I2V"
        return "T2V"


class ControlFrameCompositor:
    """Build first/last control plates from pre/post state + canonical assets."""

    def first_last_plates(
        self,
        shot: ShotSpecV2,
        canonical: dict[str, str],  # (entity, view) -> canonical asset uri
    ) -> list[ControlFramePlate]:
        plates: list[ControlFramePlate] = []
        if not shot.subjects:
            return plates
        for subj in shot.subjects:
            asset = canonical.get((subj.entity_id, "lateral"), "")
            pre = shot.basis.event_ids and _pre_state(shot) or {}
            post = shot.basis.event_ids and _post_state(shot) or {}
            plates.append(
                ControlFramePlate(view="first", entity_id=subj.entity_id,
                                  reconstruction_version=subj.reconstruction_version,
                                  canonical_asset=asset, state=pre)
            )
            plates.append(
                ControlFramePlate(view="last", entity_id=subj.entity_id,
                                  reconstruction_version=subj.reconstruction_version,
                                  canonical_asset=asset, state=post)
            )
        return plates


def _pre_state(shot: ShotSpecV2) -> dict:
    return {"event_ids": shot.basis.event_ids, "phase": "pre"}


def _post_state(shot: ShotSpecV2) -> dict:
    return {"event_ids": shot.basis.event_ids, "phase": "post"}
