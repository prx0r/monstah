"""R2 / S3-compatible storage for canonical assets and simulation bundles.

The canonical asset library (visual assets, reconstruction bundles, sim runs)
lives in Cloudflare R2. This module wraps boto3 with the account config from
`.env` and exposes simple get/put/list helpers with a local convenience for
canonical media checked into the repo.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import BinaryIO

from ..config import R2Config, get_settings

try:
    import boto3
    from botocore.config import Config as BotoConfig
    from botocore.exceptions import ClientError

    _HAS_BOTO = True
except Exception:  # pragma: no cover
    _HAS_BOTO = False


class R2Store:
    """Thin S3-compatible store over Cloudflare R2."""

    def __init__(self, config: R2Config | None = None, *, prefix: str = "canonical") -> None:
        cfg = config or get_settings().r2
        if not cfg.enabled():
            raise RuntimeError("R2 credentials not configured (check .env)")
        if not _HAS_BOTO:
            raise RuntimeError("boto3 not installed")
        self.cfg = cfg
        self.prefix = prefix.rstrip("/")
        self._client = boto3.client(
            "s3",
            endpoint_url=cfg.endpoint_url,
            aws_access_key_id=cfg.access_key_id,
            aws_secret_access_key=cfg.secret_access_key,
            config=BotoConfig(signature_version="s3v4"),
            region_name="auto",
        )

    def _key(self, name: str) -> str:
        name = name.lstrip("/")
        if name.startswith(self.prefix + "/"):
            return name
        return f"{self.prefix}/{name}"

    def put_bytes(self, name: str, data: bytes, *, content_type: str = "application/octet-stream") -> str:
        key = self._key(name)
        self._client.put_object(
            Bucket=self.cfg.bucket, Key=key, Body=data, ContentType=content_type
        )
        return key

    def put_file(self, name: str, path: str | Path) -> str:
        with open(path, "rb") as f:
            return self.put_bytes(name, f.read())

    def get_bytes(self, name: str) -> bytes:
        key = self._key(name)
        obj = self._client.get_object(Bucket=self.cfg.bucket, Key=key)
        return obj["Body"].read()

    def get_file(self, name: str, dest: str | Path) -> Path:
        dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(self.get_bytes(name))
        return dest

    def list(self, prefix: str = "") -> list[str]:
        key_prefix = self._key(prefix)
        out: list[str] = []
        paginator = self._client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.cfg.bucket, Prefix=key_prefix):
            for obj in page.get("Contents", []):
                out.append(obj["Key"])
        return out

    def exists(self, name: str) -> bool:
        try:
            key = self._key(name)
            self._client.head_object(Bucket=self.cfg.bucket, Key=key)
            return True
        except ClientError:
            return False

    def delete(self, name: str) -> None:
        key = self._key(name)
        self._client.delete_object(Bucket=self.cfg.bucket, Key=key)


class AssetStore(R2Store):
    """R2 layout helper for the canonical asset library — NOT currently wired.

    LEGACY/UNUSED: not called by any active path (see docs/AUDIT.md). `R2Store`
    is the live store. Kept as the canonical layout for when asset ingestion runs.

        assets/source/<provider>/...         (downloaded licensed source images)
        assets/entities/<entity-id>/references/
        assets/entities/<entity-id>/reconstructions/
        assets/environments/<env-id>/
    """

    def __init__(self, config: R2Config | None = None) -> None:
        super().__init__(config, prefix="assets")

    def put_source_image(self, provider: str, provider_id: str, data: bytes) -> str:
        return self.put_bytes(f"source/{provider}/{provider_id}", data, content_type="image/jpeg")

    def put_reference(self, entity_id: str, file_name: str, data: bytes) -> str:
        return self.put_bytes(f"entities/{entity_id}/references/{file_name}", data, content_type="image/jpeg")

    def put_reconstruction(self, entity_id: str, version: str, data: bytes) -> str:
        return self.put_bytes(
            f"entities/{entity_id}/reconstructions/{entity_id}_{version}.png", data, content_type="image/png"
        )

    def put_environment(self, env_id: str, file_name: str, data: bytes) -> str:
        return self.put_bytes(f"environments/{env_id}/{file_name}", data, content_type="image/jpeg")
