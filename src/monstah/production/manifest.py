"""EpisodeManifest (MVP Phase 27).

Every final episode records the full backward-traceable chain:
WorldSnapshot digest, scenario digest, sources, assertions, reconstruction
versions, simulation model, run ids, event ids, canonical asset digests,
ShotSpec digests, renderer manifests, QA verdicts, narration bindings, and the
master video digest. Answerable: "why is this shown at frame 1840?"
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EpisodeManifest:
    episode_id: str
    world_snapshot_digest: str = ""
    scenario_digest: str = ""
    sources: list[str] = field(default_factory=list)
    assertions: list[str] = field(default_factory=list)
    reconstruction_versions: dict[str, str] = field(default_factory=dict)
    simulation_model: str = ""
    run_ids: list[str] = field(default_factory=list)
    event_ids: list[str] = field(default_factory=list)
    canonical_asset_digests: dict[str, str] = field(default_factory=dict)
    shot_spec_digests: dict[str, str] = field(default_factory=dict)
    renderer_manifests: list[dict[str, Any]] = field(default_factory=list)
    qa_verdicts: list[dict[str, Any]] = field(default_factory=list)
    narration_bindings: list[dict[str, Any]] = field(default_factory=list)
    master_video_digest: str = ""

    def digest(self) -> str:
        blob = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode()).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "episode_id": self.episode_id,
            "world_snapshot_digest": self.world_snapshot_digest,
            "scenario_digest": self.scenario_digest,
            "sources": sorted(self.sources),
            "assertions": sorted(self.assertions),
            "reconstruction_versions": dict(sorted(self.reconstruction_versions.items())),
            "simulation_model": self.simulation_model,
            "run_ids": self.run_ids,
            "event_ids": sorted(self.event_ids),
            "canonical_asset_digests": dict(sorted(self.canonical_asset_digests.items())),
            "shot_spec_digests": dict(sorted(self.shot_spec_digests.items())),
            "renderer_manifests": self.renderer_manifests,
            "qa_verdicts": self.qa_verdicts,
            "narration_bindings": self.narration_bindings,
            "master_video_digest": self.master_video_digest,
        }
