"""ProductionRun state machine + resumability (MVP Phase 28-29).

Each step writes its digest + dependencies to a manifest, so a crashed render
does not re-ingest PBDB, and a failed QA does not rebuild the reconstruction.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class RunStage(str, Enum):
    INGESTED = "INGESTED"
    WORLD_BUILT = "WORLD_BUILT"
    RECONSTRUCTED = "RECONSTRUCTED"
    ASSETS_READY = "ASSETS_READY"
    SCENARIO_READY = "SCENARIO_READY"
    SIMULATED = "SIMULATED"
    STORY_READY = "STORY_READY"
    SHOTS_READY = "SHOTS_READY"
    RENDERING = "RENDERING"
    QA = "QA"
    ASSEMBLED = "ASSEMBLED"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"


_ORDER = [s.value for s in RunStage]
_FAILED = RunStage.FAILED.value


@dataclass
class ProductionRun:
    run_id: str
    channel: str
    out_dir: str = "out/run"
    stage: RunStage = RunStage.INGESTED
    digests: dict[str, str] = field(default_factory=dict)  # stage -> digest

    @classmethod
    def create(cls, channel: str, out_dir: str = "out/run") -> "ProductionRun":
        return cls(run_id=f"run-{uuid.uuid4().hex[:12]}", channel=channel, out_dir=out_dir)

    def mark(self, stage: RunStage, digest: str = "") -> "ProductionRun":
        if stage is RunStage.FAILED or _ORDER.index(stage.value) >= _ORDER.index(self.stage.value):
            self.stage = stage
            if digest:
                self.digests[stage.value] = digest
        return self

    def can_resume_from(self) -> RunStage:
        """Next stage to run (current one is done)."""
        if self.stage is RunStage.FAILED:
            return self.stage
        idx = _ORDER.index(self.stage.value)
        return RunStage(_ORDER[idx + 1]) if idx + 1 < len(_ORDER) else RunStage.PUBLISHED

    # -- persistence ------------------------------------------------------
    def state_file(self) -> Path:
        return Path(self.out_dir) / self.run_id / "RUN.json"

    def save(self) -> None:
        fp = self.state_file()
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(json.dumps({"run_id": self.run_id, "channel": self.channel,
                                  "stage": self.stage.value, "digests": self.digests}, indent=2))

    @classmethod
    def load(cls, path: str | Path) -> "ProductionRun":
        data = json.loads(Path(path).read_text())
        return cls(run_id=data["run_id"], channel=data["channel"], out_dir=str(Path(path).parent.parent),
                   stage=RunStage(data["stage"]), digests=data.get("digests", {}))
