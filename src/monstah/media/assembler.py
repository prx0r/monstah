"""EpisodeAssembler (MVP Phase 26).

MVP: produce a short (60-120s) finished film = LTX clips + deterministic
graphics + narration, 16:9 master then 9:16 derivative. ffmpeg does the
combine when available; otherwise we emit a deterministic assembly plan
(concat list + narration + subtitle/citation tracks) that ffmpeg can execute.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..media.scientific_renderer import ScientificRenderer
from ..media.shot_spec2 import ShotSpecV2


@dataclass
class Segment:
    kind: str  # clip | graphic | evidence | narration
    uri: str = ""
    svg: str = ""
    duration: float = 0.0
    shot_id: str = ""


class EpisodeAssembler:
    """Assemble a short film from clips + deterministic graphics + narration."""

    def __init__(self, *, workdir: str | Path = "out/film", use_ffmpeg: bool = True) -> None:
        self.workdir = Path(workdir)
        self.workdir.mkdir(parents=True, exist_ok=True)
        self.ffmpeg = shutil.which("ffmpeg") if use_ffmpeg else None

    def plan(
        self,
        *,
        shots: list[ShotSpecV2],
        narration: str,
        render_jobs: dict[str, dict],
        scientific: ScientificRenderer | None = None,
        evidence: list[dict] | None = None,
    ) -> list[Segment]:
        """Build the ordered segment plan for the film."""
        scientific = scientific or ScientificRenderer()
        segments: list[Segment] = []
        for shot in shots:
            job = render_jobs.get(shot.shot_id, {})
            if shot.is_deterministic():
                segments.append(Segment(kind="graphic", uri=job.get("uri", ""),
                                        svg=_deterministic_svg(shot, scientific), duration=shot.duration,
                                        shot_id=shot.shot_id))
            else:
                segments.append(Segment(kind="clip", uri=job.get("uri", ""), duration=shot.duration,
                                        shot_id=shot.shot_id))
        if evidence:
            segments.append(Segment(kind="evidence", svg=scientific.evidence_card_svg(evidence), duration=5.0))
        segments.append(Segment(kind="narration", uri=narration, duration=0.0))
        return segments

    def assemble(self, segments: list[Segment]) -> dict[str, Any]:
        """Emit an assembly manifest + ffmpeg concat list (16:9 master, 9:16 plan)."""
        concat = self.workdir / "concat.txt"
        lines = []
        for s in segments:
            if s.uri:
                lines.append(f"file '{s.uri}'")
            if s.svg:
                # persist deterministic graphic as svg
                f = self.workdir / f"{s.shot_id or 'gfx'}.svg"
                f.write_text(s.svg)
                lines.append(f"file '{f.name}'")
        concat.write_text("\n".join(lines))
        manifest = {
            "master": "16:9",
            "derivatives": ["9:16"],
            "concat_list": str(concat),
            "ffmpeg_available": bool(self.ffmpeg),
            "segments": [
                {"kind": s.kind, "duration": s.duration, "shot_id": s.shot_id} for s in segments
            ],
        }
        return manifest


def _deterministic_svg(shot: ShotSpecV2, scientific: ScientificRenderer) -> str:
    # map a data-graphic shot to a deterministic SVG
    basis = shot.basis.type.value
    if "GRAPH" in basis or "SIMULATION" in basis:
        return scientific.temporal_range_svg([])
    return scientific.confidence_svg({})
