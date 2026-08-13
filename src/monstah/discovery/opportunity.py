"""Trend/Opportunity Engine (markteresearch.md §"biggest strategic change").

Sits ABOVE the world engine: combines real demand signals (Google Trends, and
eventually TikTok Search Insights / YouTube supply) with our own production
economics (asset reuse, evidence availability, novelty) to answer

    WHAT SHOULD WE MAKE TODAY?

Monstah stays the production backend; this decides what to produce.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TopicSignal:
    """Demand signal for one topic."""

    topic: str
    current: float = 0.0  # recent search interest (0-100 proxy)
    baseline: float = 0.0  # earlier baseline
    velocity: float = 0.0  # (current/baseline - 1)

    @property
    def demand_proxy(self) -> float:
        return min(1.0, self.current / 100.0)

    @property
    def rising(self) -> bool:
        return self.velocity > 0.2 and self.current > 5


@dataclass
class Opportunity:
    topic: str
    score: float = 0.0
    factors: dict[str, float] = field(default_factory=dict)
    signal: TopicSignal | None = None

    def __str__(self) -> str:
        return f"[{self.score:0.3f}] {self.topic}"


class OpportunityScorer:
    """Score a topic's opportunity = demand × (1+velocity) × (1/supply) ×
    asset-reuse × evidence × evergreen × novelty."""

    def __init__(self, *, supply: dict[str, float] | None = None,
                 asset_reuse: dict[str, float] | None = None,
                 evidence: dict[str, float] | None = None,
                 evergreen: dict[str, float] | None = None,
                 novelty: dict[str, float] | None = None) -> None:
        self.supply = supply or {}
        self.asset_reuse = asset_reuse or {}
        self.evidence = evidence or {}
        self.evergreen = evergreen or {}
        self.novelty = novelty or {}

    def score(self, signal: TopicSignal) -> Opportunity:
        s = signal
        supply = self.supply.get(s.topic, 0.5)  # 0 = no competition, 1 = saturated
        reuse = self.asset_reuse.get(s.topic, 0.5)
        evidence = self.evidence.get(s.topic, 0.5)
        evergreen = self.evergreen.get(s.topic, 0.5)
        novelty = self.novelty.get(s.topic, 0.5)

        demand_term = s.demand_proxy * (1.0 + max(0.0, s.velocity))
        supply_term = 1.0 / (1.0 + 5.0 * supply)  # penalize saturation
        factors = {
            "demand": demand_term,
            "velocity": max(0.0, s.velocity),
            "supply_penalty": supply_term,
            "asset_reuse": reuse,
            "evidence": evidence,
            "evergreen": evergreen,
            "novelty": novelty,
        }
        score = demand_term * supply_term * reuse * evidence * evergreen * novelty
        return Opportunity(topic=s.topic, score=score, factors=factors, signal=s)


class LocalTrendingAdapter:
    """Demand/supply signal from real YouTube trending data (Kaggle CSVs).

    Always works offline. `demand` = avg views of videos matching a niche,
    `supply` = number of matching videos, `velocity` = 0 (no time series).
    """

    def __init__(self, csvs: list[str] | None = None) -> None:
        import os

        self.csvs = csvs or [
            os.environ.get("TRENDING_GB", "/tmp/opencode/GBvideos.csv"),
            os.environ.get("TRENDING_CA", "/tmp/opencode/CAvideos.csv"),
            os.environ.get("TRENDING_IN", "/tmp/opencode/INvideos.csv"),
        ]

    def signals(self, topics: list[str], **kw) -> list[TopicSignal]:
        import polars as pl

        frames = []
        for c in self.csvs:
            if os.path.exists(c):
                try:
                    frames.append(pl.read_csv(c, null_values=["", "None"]).select(["title", "views"]))
                except Exception:
                    pass
        if not frames:
            return [TopicSignal(topic=t) for t in topics]
        df = pl.concat(frames).with_columns(pl.col("views").cast(pl.Int64))
        df = df.with_columns(pl.col("title").str.to_lowercase().alias("t"))
        out: list[TopicSignal] = []
        for topic in topics:
            pat = "|".join(w.strip() for w in topic.split() if w.strip())
            sub = df.filter(pl.col("t").str.contains(pat)) if pat else df.head(0)
            if sub.height == 0:
                out.append(TopicSignal(topic=topic))
                continue
            demand = float(sub["views"].mean())
            supply = float(sub.height)
            out.append(
                TopicSignal(
                    topic=topic,
                    current=demand,
                    baseline=demand,
                    velocity=0.0,  # no time series in a snapshot
                )
            )
            # stash supply for the scorer via a side table
            self._supply = getattr(self, "_supply", {})
            self._supply[topic] = supply
        return out

    @property
    def supply(self) -> dict[str, float]:
        return getattr(self, "_supply", {})


def signals_for(
    topics: list[str],
    *,
    use_google: bool = True,
    days: int = 30,
    window: int = 7,
    csvs: list[str] | None = None,
) -> tuple[list[TopicSignal], dict[str, float], bool]:
    """Try live Google Trends; fall back to local YouTube-trending data.

    Returns (signals, supply_map, used_google).
    """
    if use_google:
        try:
            a = GoogleTrendsAdapter()
            sigs = a.signals(topics, days=days, window=window)
            if any(s.current > 0 for s in sigs):
                return sigs, {s.topic: 0.4 for s in sigs}, True
        except Exception:
            pass
    a = LocalTrendingAdapter(csvs=csvs)
    sigs = a.signals(topics, days=days, window=window)
    return sigs, a.supply, False


class GoogleTrendsAdapter:
    """Pulls real Google Trends interest for a list of topics (pytrends)."""

    def __init__(self) -> None:
        try:
            from pytrends.request import TrendReq

            self._pt = TrendReq(hl="en-US", tz=0)
        except Exception as e:  # pragma: no cover
            raise RuntimeError(f"pytrends unavailable: {e}")

    def signals(self, topics: list[str], *, days: int = 30, window: int = 7) -> list[TopicSignal]:
        """Interest-over-time for topics; current = last `window` days, baseline = prior.
        Google caps ~5 topics per request, so chunk.
        """
        out: list[TopicSignal] = []
        for i in range(0, len(topics), 5):
            chunk = topics[i : i + 5]
            out.extend(self._signals_chunk(chunk, days=days, window=window))
        return out

    def _signals_chunk(self, topics: list[str], *, days: int, window: int) -> list[TopicSignal]:
        try:
            self._pt.build_payload(topics, timeframe=f"today {days}-d")
            df = self._pt.interest_over_time()
        except Exception as e:  # pragma: no cover
            raise RuntimeError(f"Google Trends failed: {e}")
        out: list[TopicSignal] = []
        if df.empty:
            return out
        for t in topics:
            if t not in df.columns:
                out.append(TopicSignal(topic=t))
                continue
            series = df[t].dropna()
            if series.empty:
                out.append(TopicSignal(topic=t))
                continue
            current = float(series.iloc[-window:].mean())
            baseline = float(series.iloc[:-window].mean()) if len(series) > window else float(series.mean())
            baseline = baseline or 1.0
            velocity = current / baseline - 1.0
            out.append(TopicSignal(topic=t, current=current, baseline=baseline, velocity=velocity))
        return out
