"""Executable EpisodeSpec (MVP Phase 15).

This becomes the ONLY input to the media compiler — not ad hoc story strings.
It pins the world snapshot, scenario, thesis, claim-aware beats, narrative
claims, required assets, uncertainties, and format targets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .beats import StoryBeat


@dataclass
class EpisodeSpec:
    episode_id: str
    channel: str = ""
    world_snapshot: dict[str, Any] = field(default_factory=dict)
    scenario: dict[str, Any] = field(default_factory=dict)

    thesis: str = ""
    question: str = ""
    hook: str = ""

    beats: list[StoryBeat] = field(default_factory=list)
    narrative_claims: list[dict] = field(default_factory=list)
    required_assets: list[str] = field(default_factory=list)
    uncertainties: list[str] = field(default_factory=list)

    duration_target: float = 600.0
    aspect_targets: list[str] = field(default_factory=lambda: ["16:9", "9:16", "4:5"])

    def compile_script(self) -> str:
        """The deterministic script a narrator/assembler reads from beats."""
        lines = [f"# {self.hook}", ""]
        for b in self.beats:
            marker = f"[{b.kind.value}]" if b.grounded else f"[{b.kind.value}:UNGROUNDED]"
            lines.append(f"({marker}) {b.text}")
        if self.uncertainties:
            lines.append("\n## Uncertainties")
            lines.extend(f"- {u}" for u in self.uncertainties)
        return "\n".join(lines)
