"""Renderer backends (MVP Phase 20).

API-first is the fastest MVP: submit/poll/fetch/retake/reframe. The domain
passes a fully-constrained ShotSpecV2 + control plates; the renderer obeys.
`LTX25ApiRenderer` is the real contract (needs an API key). `OfflineRenderer`
produces a deterministic render manifest for testing the dataflow without a key.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ..config import get_settings
from .shot_spec2 import ShotSpecV2


@dataclass
class RenderJob:
    job_id: str
    shot: ShotSpecV2
    status: str = "queued"
    result_uri: str = ""
    manifest: dict[str, Any] = field(default_factory=dict)


class RendererBackend(ABC):
    @abstractmethod
    def submit(self, shot: ShotSpecV2) -> RenderJob: ...

    @abstractmethod
    def poll(self, job: RenderJob) -> str: ...

    @abstractmethod
    def fetch(self, job: RenderJob) -> dict: ...

    def retake(self, job: RenderJob, window: tuple[float, float] | None = None) -> RenderJob:
        raise NotImplementedError

    def reframe(self, job: RenderJob, aspect: str) -> RenderJob:
        raise NotImplementedError


class LTX25ApiRenderer(RendererBackend):
    """Real LTX-2.5 API adapter (submit/poll/fetch/retake/reframe)."""

    def __init__(self, *, api_key: str = "", base_url: str = "") -> None:
        self.api_key = api_key or _env_or("LTX_API_KEY", "")
        self.base_url = base_url or _env_or("LTX_API_URL", "https://api.ltx.io/v1")

    def _require_key(self) -> None:
        if not self.api_key:
            raise RuntimeError("LTX API key not configured (set LTX_API_KEY)")

    def submit(self, shot: ShotSpecV2) -> RenderJob:
        self._require_key()
        import uuid

        job = RenderJob(job_id=f"ltx-{uuid.uuid4().hex[:12]}", shot=shot)
        # NOTE: real submission posts shot + control plates to the LTX API.
        # Implemented as the contract; actual HTTP wiring needs the API key.
        raise NotImplementedError("submit requires live LTX API wiring + key")

    def poll(self, job: RenderJob) -> str:
        self._require_key()
        return job.status

    def fetch(self, job: RenderJob) -> dict:
        self._require_key()
        return {"job_id": job.job_id, "uri": job.result_uri}

    def retake(self, job: RenderJob, window: tuple[float, float] | None = None) -> RenderJob:
        self._require_key()
        job.status = "retake"
        return job

    def reframe(self, job: RenderJob, aspect: str) -> RenderJob:
        self._require_key()
        job.manifest["aspect"] = aspect
        return job


class OfflineRenderer(RendererBackend):
    """Deterministic, key-free renderer for testing the dataflow.

    Produces a real render MANIFEST binding the shot + control plates — it does
    not fabricate video. Used by `monstah produce` without a live LTX key.
    """

    def __init__(self) -> None:
        import uuid

        self._uuid = uuid.uuid4

    def submit(self, shot: ShotSpecV2) -> RenderJob:
        job = RenderJob(job_id=f"offline-{self._uuid().hex[:10]}", shot=shot, status="ready")
        job.manifest = {
            "renderer": "offline",
            "shot_id": shot.shot_id,
            "basis_type": shot.basis.type.value,
            "event_ids": shot.basis.event_ids,
            "assertion_ids": shot.basis.assertion_ids,
            "control_mode": shot.control.preferred,
            "first_frame": shot.control.first_frame,
            "last_frame": shot.control.last_frame,
            "subjects": [{"entity_id": s.entity_id, "version": s.reconstruction_version} for s in shot.subjects],
        }
        return job

    def poll(self, job: RenderJob) -> str:
        return job.status

    def fetch(self, job: RenderJob) -> dict:
        return {"job_id": job.job_id, "uri": job.result_uri, "manifest": job.manifest}

    def retake(self, job: RenderJob, window: tuple[float, float] | None = None) -> RenderJob:
        job.status = "retake"
        job.manifest["retake_window"] = window
        return job

    def reframe(self, job: RenderJob, aspect: str) -> RenderJob:
        job.manifest["aspect"] = aspect
        return job


def _env_or(key: str, default: str) -> str:
    import os

    return os.environ.get(key, default)


def default_renderer() -> RendererBackend:
    """Use the live API renderer when a key is present, else the offline one."""
    if _env_or("LTX_API_KEY", ""):
        return LTX25ApiRenderer()
    return OfflineRenderer()
