"""PostgreSQL + PostGIS canonical store (§45, §47).

Canonical world state lives in Postgres. This store wires the tables from
sql/postgres.sql (entities, taxa, external_ids, occurrences, sources,
trait_assertions, relation_assertions, reconstructions, scenarios,
simulation_runs, events, stories, shots, assets, episodes). Uses psycopg; if
unavailable, the store is inert but importable.
"""

from __future__ import annotations

from typing import Any, Iterable

try:
    import psycopg

    _HAS_PSYCOPG = True
except Exception:  # pragma: no cover
    _HAS_PSYCOPG = False


class PostgresStore:
    """Canonical store. Requires psycopg[binary] and a running Postgres."""

    def __init__(self, *, dsn: str | None = None, connect_args: dict[str, Any] | None = None) -> None:
        if not _HAS_PSYCOPG:
            raise RuntimeError("psycopg not installed: pip install 'psycopg[binary]'")
        self._conn = psycopg.connect(dsn or (connect_args or {}))

    def init_schema(self, schema_file: str = "sql/postgres.sql") -> None:
        from pathlib import Path

        sql = Path(schema_file).read_text()
        with self._conn.cursor() as cur:
            cur.execute(sql)
        self._conn.commit()

    # -- entities / crosswalk -------------------------------------------
    def upsert_entity(self, entity_id: str, kind: str, name: str, properties: dict) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO entities (id, kind, name, properties) VALUES (%s,%s,%s,%s)
                ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name, properties=EXCLUDED.properties
                """,
                (entity_id, kind, name, properties),
            )
        self._conn.commit()

    def set_external_id(self, entity_id: str, namespace: str, ext_id: str) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO external_ids (entity_id, namespace, ext_id) VALUES (%s,%s,%s)
                ON CONFLICT (entity_id, namespace) DO UPDATE SET ext_id=EXCLUDED.ext_id
                """,
                (entity_id, namespace, ext_id),
            )
        self._conn.commit()

    # -- assertions / reconstructions -----------------------------------
    def insert_trait_assertion(self, a: dict) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO trait_assertions
                  (id, entity_id, trait, value_json, status, confidence, unit,
                   value_median, value_lower, value_upper, source_id, version)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    a["id"], a["entity_id"], a["trait"], a.get("value_json"),
                    a.get("status"), a.get("confidence"), a.get("unit"),
                    a.get("median"), a.get("lower"), a.get("upper"),
                    a.get("source_id"), a.get("version"),
                ),
            )
        self._conn.commit()

    def insert_reconstruction(self, r: dict) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO reconstructions
                  (id, entity_id, version, parameters, assumptions, supersedes)
                VALUES (%s,%s,%s,%s,%s,%s)
                """,
                (r["id"], r["entity_id"], r["version"], r.get("parameters"),
                 r.get("assumptions"), r.get("supersedes")),
            )
        self._conn.commit()

    # -- simulation ------------------------------------------------------
    def insert_sim_run(self, r: dict) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO simulation_runs (id, scenario_id, seed, model_versions, result)
                VALUES (%s,%s,%s,%s,%s)
                """,
                (r["id"], r.get("scenario_id"), r.get("seed"), r.get("model_versions"), r.get("result")),
            )
        self._conn.commit()

    def insert_event(self, e: dict) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO events (id, run_id, kind, ts, description, payload)
                VALUES (%s,%s,%s,%s,%s,%s)
                """,
                (e["id"], e.get("run_id"), e.get("kind"), e.get("ts"), e.get("description"), e.get("payload")),
            )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()
