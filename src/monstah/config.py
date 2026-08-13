"""Configuration loader.

Reads from environment variables, falling back to a local `.env` file.
Secrets live in `.env` (gitignored); never in code or git history.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def load_dotenv(path: str | Path | None = None) -> None:
    """Minimal .env parser (KEY=VALUE, # comments). No external dep needed."""
    path = Path(path) if path else PROJECT_ROOT / ".env"
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_dotenv()


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


@dataclass
class R2Config:
    account_id: str = field(default_factory=lambda: _env("R2_ACCOUNT_ID"))
    access_key_id: str = field(default_factory=lambda: _env("R2_ACCESS_KEY_ID"))
    secret_access_key: str = field(default_factory=lambda: _env("R2_SECRET_ACCESS_KEY"))
    endpoint_url: str = field(
        default_factory=lambda: _env(
            "R2_ENDPOINT_URL",
            f"https://{_env('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
        )
    )
    bucket: str = field(default_factory=lambda: _env("R2_BUCKET", "blog-video-assets"))

    def enabled(self) -> bool:
        return bool(self.access_key_id and self.secret_access_key and self.account_id)


@dataclass
class Settings:
    r2: R2Config = field(default_factory=R2Config)
    pbdb_cache: str = field(default_factory=lambda: _env("PBDB_CACHE", "~/.cache/monstah"))


def get_settings() -> Settings:
    return Settings()
