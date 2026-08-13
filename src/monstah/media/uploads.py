"""Uploads sync — pull received reference files from R2 into the print room.

The "print room" (`reference/`) is where received reference documents land
(mirroring the `.meta` librarian pattern: a tracked index of what was received,
where it came from, when). This pulls files from the R2 `uploads/` prefix into
`reference/` and verifies SHA when a `.sha256` file is present.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..config import R2Config
from .storage import R2Store


class UploadsSync:
    """Sync files from R2 `uploads/` into the local print room."""

    def __init__(self, *, room: str | Path = "reference", config: R2Config | None = None) -> None:
        self.room = Path(room)
        self.room.mkdir(parents=True, exist_ok=True)
        self.store = R2Store(config, prefix="uploads")

    def list_remote(self) -> list[str]:
        """Names of every file in the R2 uploads prefix (stripped of prefix)."""
        return [k.split("/", 1)[-1] for k in self.store.list("") if "/" in k]

    def pull(self, name: str, *, verify: bool = True) -> Path:
        """Download one file into the print room; verify SHA if a .sha256 exists."""
        dest = self.room / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        data = self.store.get_bytes(name)
        dest.write_bytes(data)
        if verify:
            self._verify(name, dest)
        return dest

    def sync(self, names: list[str] | None = None, *, verify: bool = True) -> dict[str, Any]:
        """Pull all (or the given) uploads into the print room. Returns a report."""
        report: dict[str, Any] = {"pulled": [], "verified": [], "failed": []}
        remote = self.list_remote() if names is None else names
        for name in remote:
            try:
                dest = self.pull(name, verify=verify)
                report["pulled"].append(str(dest))
                report["verified"].append(name)
            except Exception as e:
                report["failed"].append({"name": name, "error": str(e)[:120]})
        return report

    def _verify(self, name: str, dest: Path) -> None:
        import hashlib

        sha_file = self.room / f"{name}.sha256"
        if not sha_file.exists():
            # try to fetch the expected hash from R2 if present
            try:
                expected = self.store.get_bytes(f"{name}.sha256").decode().strip().split()[0]
            except Exception:
                return  # no sha available; nothing to verify
        else:
            expected = sha_file.read_text().strip().split()[0]
        actual = hashlib.sha256(dest.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"SHA mismatch for {name}: expected {expected}, got {actual}")
