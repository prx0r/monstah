"""DuckDB analytical + canonical store (durable, file-backed by default).

The heavyweight layer: occurrences, evidence chain (source→claim→assertion→
reconstruction), simulation results, events, episodes. Persists to a real file
so nothing lives only in memory. Parquet export keeps the 5GB box light.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Iterable

import duckdb


class DuckStore:
    """Analytical + lightweight-canonical store over DuckDB."""

    def __init__(self, path: str | Path | None = None, *, parquet_dir: str | None = None, durable: bool = True) -> None:
        if path is None:
            if durable:
                data_dir = Path(tempfile.gettempdir()) / "monstah" / "db"
                data_dir.mkdir(parents=True, exist_ok=True)
                self._path = str(data_dir / "monstah.duckdb")
                self._tmpdir = None
            else:
                self._tmpdir = tempfile.TemporaryDirectory()
                self._path = str(Path(self._tmpdir.name) / "analytics.duckdb")
        else:
            self._path = str(path)
            self._tmpdir = None
        self._parquet_dir = Path(parquet_dir) if parquet_dir else None
        self._con = duckdb.connect(self._path)
        self._init_schema()

    def _init_schema(self) -> None:
        self._con.execute("CREATE TABLE IF NOT EXISTS sources (entity_id TEXT, namespace TEXT, external_id TEXT, type TEXT, title TEXT)")
        self._con.execute("CREATE TABLE IF NOT EXISTS claims (id TEXT PRIMARY KEY, entity_id TEXT, trait TEXT, statement TEXT, source_uri TEXT, status TEXT)")
        self._con.execute("CREATE TABLE IF NOT EXISTS assertions (id TEXT PRIMARY KEY, entity_id TEXT, trait TEXT, value TEXT, unit TEXT, status TEXT, source_uri TEXT, version TEXT)")
        self._con.execute("CREATE TABLE IF NOT EXISTS reconstructions (entity_id TEXT, version TEXT, assertion_ids TEXT, parameters TEXT)")
        self._con.execute("CREATE TABLE IF NOT EXISTS occurrences (entity_id TEXT, lat DOUBLE, lng DOUBLE, min_ma DOUBLE, max_ma DOUBLE)")
        self._con.execute("CREATE TABLE IF NOT EXISTS sim_results (scenario TEXT, outcome TEXT, probability DOUBLE)")
        self._con.execute("CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, scenario TEXT, run_index BIGINT, actor TEXT, action TEXT, detail TEXT, pre_state TEXT, post_state TEXT)")
        self._con.execute("CREATE TABLE IF NOT EXISTS episodes (channel TEXT, scenario TEXT, title TEXT, bundle TEXT, created_at TIMESTAMP DEFAULT now())")
        self._con.execute("CREATE TABLE IF NOT EXISTS world_snapshots (world_id TEXT, world_version TEXT, digest TEXT, payload TEXT, created_at TIMESTAMP DEFAULT now(), UNIQUE(world_id, world_version))")
        self._con.execute("CREATE TABLE IF NOT EXISTS scenarios (id TEXT PRIMARY KEY, name TEXT, template TEXT, mode TEXT, params TEXT)")

    # --- evidence chain persistence ------------------------------------
    def write_source(self, entity_id: str, src: Any) -> None:
        self._con.execute(
            "INSERT INTO sources (entity_id, namespace, external_id, type, title) VALUES (?,?,?,?,?)",
            [entity_id, src.namespace, src.external_id, src.type, src.title],
        )

    def write_claim(self, c: Any) -> None:
        self._con.execute(
            "INSERT INTO claims (id, entity_id, trait, statement, source_uri, status) VALUES (?,?,?,?,?,?)",
            [c.id, c.entity.uri, c.trait, c.statement, c.source.uri, c.status.value],
        )

    def write_assertion(self, a: Any) -> None:
        self._con.execute(
            "INSERT INTO assertions (id, entity_id, trait, value, unit, status, source_uri, version) VALUES (?,?,?,?,?,?,?,?)",
            [a.id, a.entity.uri, a.trait, str(a.value), a.uncertainty.unit, a.status.value,
             a.provenance.source.uri, a.version],
        )

    def write_reconstruction(self, entity_id: str, r: Any) -> None:
        import json

        self._con.execute(
            "INSERT INTO reconstructions (entity_id, version, assertion_ids, parameters) VALUES (?,?,?,?)",
            [entity_id, r.version, json.dumps(r.assertions), json.dumps(r.parameters)],
        )

    def write_evidence_pack(self, entity_id: str, src: Any, claims: Iterable[Any],
                            assertions: Iterable[Any], reconstruction: Any) -> None:
        self.write_source(entity_id, src)
        for c in claims:
            self.write_claim(c)
        for a in assertions:
            self.write_assertion(a)
        self.write_reconstruction(entity_id, reconstruction)

    # --- simulation / event persistence --------------------------------
    def register_occurrences(self, rows: Iterable[dict]) -> None:
        self._con.executemany(
            "INSERT INTO occurrences (entity_id, lat, lng, min_ma, max_ma) VALUES (?,?,?,?,?)",
            [(r.get("entity_id"), r.get("lat"), r.get("lng"), r.get("min_ma"), r.get("max_ma")) for r in rows],
        )

    def register_sim_results(self, rows: Iterable[dict]) -> None:
        self._con.executemany(
            "INSERT INTO sim_results (scenario, outcome, probability) VALUES (?,?,?)",
            [(r["scenario"], r["outcome"], r.get("probability")) for r in rows],
        )

    def write_events(self, scenario: str, run_index: int, events: Iterable[dict]) -> None:
        import json

        self._con.executemany(
            "INSERT OR REPLACE INTO events (id, scenario, run_index, actor, action, detail, pre_state, post_state) VALUES (?,?,?,?,?,?,?,?)",
            [
                (e["event_id"], scenario, run_index, e.get("actor"), e.get("action"), e.get("detail"),
                 json.dumps(e.get("pre_state", {})), json.dumps(e.get("post_state", {})))
                for e in events
            ],
        )

    def write_episode(self, channel: str, scenario: str, title: str, bundle: dict) -> None:
        import json

        self._con.execute(
            "INSERT INTO episodes (channel, scenario, title, bundle) VALUES (?,?,?,?)",
            [channel, scenario, title, json.dumps(bundle)],
        )

    def write_world_snapshot(self, snap) -> None:
        import json

        self._con.execute(
            "INSERT OR REPLACE INTO world_snapshots (world_id, world_version, digest, payload) VALUES (?,?,?,?)",
            [snap.world_id, snap.world_version, snap.digest(), json.dumps(snap.evidence_closure())],
        )

    def write_scenario(self, man) -> None:
        import json

        self._con.execute(
            "INSERT OR REPLACE INTO scenarios (id, name, template, mode, params) VALUES (?,?,?,?,?)",
            [man.scenario_id, man.scenario_id, "scenario", man.mode, json.dumps({"digest": man.digest()})],
        )

    # --- queries --------------------------------------------------------
    def query(self, sql: str) -> list[dict]:
        rows = self._con.execute(sql).fetchall()
        cols = [d[0] for d in self._con.description] if self._con.description else []
        return [dict(zip(cols, r)) for r in rows]

    def count(self, table: str) -> int:
        return int(self._con.execute(f"SELECT count(*) FROM {table}").fetchone()[0])

    def to_parquet(self, table: str) -> Path:
        if self._parquet_dir is None:
            raise ValueError("parquet_dir not configured")
        self._parquet_dir.mkdir(parents=True, exist_ok=True)
        out = self._parquet_dir / f"{table}.parquet"
        self._con.execute(f"COPY {table} TO '{out}' (FORMAT PARQUET)")
        return out

    def close(self) -> None:
        try:
            self._con.close()
        finally:
            if self._tmpdir:
                self._tmpdir.cleanup()

    def __enter__(self) -> "DuckStore":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()
