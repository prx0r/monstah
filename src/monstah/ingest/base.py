"""Shared HTTP ingest scaffolding.

All external services are wrapped behind a thin, typed client that maps raw
API responses into evidence models (Source records / References). Requests are
cached on disk by default so re-ingests stay polite to public APIs.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import httpx

DEFAULT_TIMEOUT = 30.0


class IngestError(RuntimeError):
    pass


class HttpApi:
    """Base client: retries, JSON decode, optional disk cache."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        cache_dir: str | None = None,
        user_agent: str = "monstah/0.1",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.user_agent = user_agent
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self._client = httpx.Client(
            timeout=timeout,
            headers={"User-Agent": user_agent, "Accept": "application/json"},
            follow_redirects=True,
        )

    def _cache_key(self, path: str, params: dict | None) -> Path | None:
        if not self.cache_dir:
            return None
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        blob = json.dumps({"p": path, "q": params or {}}, sort_keys=True)
        digest = hashlib.sha1(blob.encode()).hexdigest()[:16]
        safe = path.strip("/").replace("/", "_") or "root"
        return self.cache_dir / f"{safe}_{digest}.json"

    def get(self, path: str, params: dict | None = None, *, use_cache: bool = True) -> dict | list:
        cache = self._cache_key(path, params) if use_cache else None
        if cache and cache.exists():
            return json.loads(cache.read_text())
        url = f"{self.base_url}/{path.lstrip('/')}"
        for attempt in (1, 2, 3):
            try:
                resp = self._client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
                if cache:
                    cache.write_text(json.dumps(data))
                return data
            except httpx.HTTPStatusError as e:
                if e.response.status_code in (429, 500, 502, 503, 504) and attempt < 3:
                    import time

                    time.sleep(attempt * 2)
                    continue
                raise IngestError(f"GET {url} -> HTTP {e.response.status_code}: {e.response.text[:200]}") from e
            except httpx.HTTPError as e:
                if attempt < 3:
                    import time

                    time.sleep(attempt)
                    continue
                raise IngestError(f"GET {url} failed: {e}") from e
        raise IngestError("unreachable")  # pragma: no cover

    def close(self) -> None:
        self._client.close()
