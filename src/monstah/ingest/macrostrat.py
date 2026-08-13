"""Macrostrat client: reconstruct the actual world at a place + time.

PBDB says *a fossil is here around this age*. Macrostrat tells us *what Earth
was like there*: rock units, lithology, depositional context, age.
"""

from __future__ import annotations

from typing import Any

from .base import HttpApi


class MacrostratClient(HttpApi):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__("https://macrostrat.org/api", **kwargs)

    def lithology(self, *, lat: float | None = None, lng: float | None = None) -> list[dict]:
        params: dict[str, Any] = {"format": "json"}
        if lat is not None and lng is not None:
            params["lat"] = lat
            params["lng"] = lng
        return self.get("defs/lithologies", params)["success"]["data"]

    def columns(self, *, lat: float | None = None, lng: float | None = None) -> list[dict]:
        params: dict[str, Any] = {"format": "json"}
        if lat is not None and lng is not None:
            params["lat"] = lat
            params["lng"] = lng
        return self.get("columns", params)["success"]["data"]

    def unit_strat(
        self,
        *,
        lat: float | None = None,
        lng: float | None = None,
        age: float | None = None,
        lithology: str | None = None,
    ) -> list[dict]:
        """Rock units at a point, optionally filtered by age (Ma) / lithology."""
        params: dict[str, Any] = {"format": "json"}
        if lat is not None:
            params["lat"] = lat
        if lng is not None:
            params["lng"] = lng
        if age is not None:
            params["age"] = age
        if lithology:
            params["lithology"] = lithology
        return self.get("units/lookup", params)["success"]["data"]

    def stratigraphy(self, unit_id: int) -> list[dict]:
        return self.get(f"units/{unit_id}", {"format": "json"})["success"]["data"]

    def environment_at(self, lat: float, lng: float, age_ma: float) -> list[dict]:
        """Context of the world at a PBDB occurrence point + age."""
        return self.unit_strat(lat=lat, lng=lng, age=age_ma)
