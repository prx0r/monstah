"""DuckDB + Parquet analytical store (§45, §47).

The heavyweight analytical layer: occurrence joins, simulation outputs, Monte
Carlo analytics. Kept out of RAM by registering Parquet-backed relations. Fits
the 5GB/4-core box: DuckDB runs analytical joins far cheaper than Postgres for
giant occurrence/interaction data.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Iterable

import duckdb


class DuckStore:
    """Thin analytical store over DuckDB, optionally backed by Parquet."""

    def __init__(self, path: str | Path | None = None, *, parquet_dir: str | None = None) -> None:
        if path is None:
            self._tmpdir = tempfile.TemporaryDirectory()
            self._path = str(Path(self._tmpdir.name) / "analytics.duckdb")
        else:
            self._path = str(path)
        self._parquet_dir = Path(parquet_dir) if parquet_dir else None
        self._con = duckdb.connect(self._path)

    # -- tables ---------------------------------------------------------
    def register_occurrences(self, rows: Iterable[dict]) -> None:
        """Register occurrence records (entity_id, lat, lng, min_ma, max_ma...)."""
        import polars as pl

        df = pl.DataFrame(rows)
        self._con.register("occurrences", df)
        self._con.execute(
            "CREATE TABLE IF NOT EXISTS occurrences AS SELECT * FROM occurrences"
        )

    def register_sim_results(self, rows: Iterable[dict]) -> None:
        import polars as pl

        df = pl.DataFrame(rows)
        self._con.register("sim_results", df)
        self._con.execute("CREATE TABLE IF NOT EXISTS sim_results AS SELECT * FROM sim_results")

    # -- queries --------------------------------------------------------
    def query(self, sql: str) -> list[dict]:
        return self._con.execute(sql).fetchall()

    def query_df(self, sql: str):
        import polars as pl

        return pl.DataFrame(self._con.execute(sql).fetch_df())

    def cooccurring(
        self,
        taxon: str,
        *,
        min_ma: float | None = None,
        max_ma: float | None = None,
        radius_km: float | None = None,
    ) -> list[dict]:
        """Analytical join: taxa occurring near the same place/time as `taxon`."""
        rows = self.query_df(
            """
            SELECT b.entity_id, count(*) AS overlap
            FROM occurrences a
            JOIN occurrences b ON a.entity_id = b.entity_id AND a.entity_id <> b.entity_id
            WHERE a.entity_id = ? AND b.entity_id <> ?
            GROUP BY b.entity_id ORDER BY overlap DESC LIMIT 50
            """,
        )
        return rows

    def outcome_summary(self, scenario: str) -> list[dict]:
        rows = self.query_df(
            "SELECT outcome, count(*) AS n FROM sim_results WHERE scenario = ? GROUP BY outcome ORDER BY n DESC",
        )
        return rows

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
            if hasattr(self, "_tmpdir"):
                self._tmpdir.cleanup()

    def __enter__(self) -> "DuckStore":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()
