"""StoreManager — routes canonical/analytical/binary persistence (MVP Phase 10).

- DuckDB : analytical + evidence + events + episodes (always available)
- Postgres: canonical (world_snapshots, scenarios, events, episodes) when configured
- R2      : binaries (images, JSON exports, bundles)

Postgres is optional: if a DSN is configured it is used; otherwise the manager
still persists everything to DuckDB + R2 (never blocks on an absent DB).
"""

from __future__ import annotations

from typing import Any

from ..config import get_settings


class StoreManager:
    def __init__(self, *, duck=None, postgres=None, r2=None) -> None:
        from ..data.duck import DuckStore
        from ..media.storage import R2Store

        self.duck = duck or DuckStore()
        self.r2 = r2 or R2Store(prefix="canonical/channels")
        self.postgres = postgres
        if postgres is None and _postgres_dsn():
            try:
                from ..data.postgres import PostgresStore

                self.postgres = PostgresStore(dsn=_postgres_dsn())
            except Exception:
                self.postgres = None

    # --- canonical -------------------------------------------------------
    def write_world_snapshot(self, snap) -> None:
        self.duck.write_world_snapshot(snap)
        if self.postgres:
            self.postgres.write_world_snapshot(snap)

    def write_scenario(self, man) -> None:
        self.duck.write_scenario(man)
        if self.postgres:
            self.postgres.write_scenario(man)

    def write_events(self, scenario: str, run_index: int, events: list[dict]) -> None:
        self.duck.write_events(scenario, run_index, events)
        if self.postgres:
            for e in events:
                self.postgres.write_canonical_event({"scenario": scenario, "run_index": run_index, **e})

    def write_episode(self, channel: str, scenario: str, title: str, bundle: dict) -> None:
        self.duck.write_episode(channel, scenario, title, bundle)
        if self.postgres:
            self.postgres.write_episode(
                {"id": f"{channel}:{scenario}:{title[:40]}", "channel": channel, "title": title,
                 "metadata": {"bundle": bundle}}
            )

    def close(self) -> None:
        self.duck.close()
        if self.postgres:
            self.postgres.close()


def _postgres_dsn() -> str:
    try:
        return get_settings().postgres_dsn
    except Exception:
        return ""
