"""ScientificRenderer — deterministic data graphics (MVP Phase 16).

Do NOT generate every visual with LTX. Monstah has two renderers: GENERATIVE
(LTX) and DETERMINISTIC (this). Deterministic graphics (timelines, range charts,
occurrence plots, confidence diagrams, evidence cards) increase credibility and
cut generation cost. All output is deterministic SVG.
"""

from __future__ import annotations

import html
from typing import Any


def _esc(s: Any) -> str:
    return html.escape(str(s))


class ScientificRenderer:
    """Deterministic SVG graphics for scientific beats."""

    def temporal_range_svg(self, ranges: list[dict], *, width: int = 900, height: int = 300) -> str:
        """Fossil range diagram: rows = taxa, horizontal = time (Ma)."""
        all_lo = min((r.get("min_ma") for r in ranges), default=0)
        all_hi = max((r.get("max_ma") for r in ranges), default=100)
        span = max(1e-9, all_hi - all_lo)
        pad = 30
        row_h = max(24, (height - pad) / max(1, len(ranges)))
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
        parts.append(f'<text x="{pad}" y="20" font-family="sans-serif" font-size="14">Temporal ranges (Ma)</text>')
        for i, r in enumerate(ranges):
            y = pad + i * row_h + 12
            x1 = pad + (r.get("max_ma", all_hi) - all_lo) / span * (width - 2 * pad)
            x2 = pad + (r.get("min_ma", all_lo) - all_lo) / span * (width - 2 * pad)
            parts.append(
                f'<rect x="{x1:.0f}" y="{y - 8}" width="{max(4, x2 - x1):.0f}" height="12" '
                f'rx="3" fill="#4a7ba6" stroke="#274b63"/>'
            )
            parts.append(
                f'<text x="{x2 + 6}" y="{y}" font-family="sans-serif" font-size="12">{_esc(r.get("name", ""))}</text>'
            )
        parts.append("</svg>")
        return "\n".join(parts)

    def confidence_svg(self, appearance: dict[str, str], *, width: int = 500, height: int = 300) -> str:
        """Certainty breakdown: CONSTRAINED/INFERRED/OPEN/SPECULATIVE per trait."""
        colors = {"CONSTRAINED": "#2e8b57", "INFERRED": "#4a7ba6", "RECONSTRUCTED": "#d2a106",
                  "OPEN": "#999", "SPECULATIVE": "#c0392b"}
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">']
        y = 20
        parts.append(f'<text x="10" y="{y}" font-family="sans-serif" font-size="14">Reconstruction certainty</text>')
        y += 22
        for trait, c in appearance.items():
            col = colors.get(c.upper(), "#777")
            parts.append(f'<rect x="10" y="{y}" width="14" height="14" fill="{col}"/>')
            parts.append(
                f'<text x="32" y="{y + 12}" font-family="sans-serif" font-size="12">'
                f'{_esc(trait)} — {_esc(c.upper())}</text>'
            )
            y += 22
        parts.append("</svg>")
        return "\n".join(parts)

    def occurrence_plot_svg(self, points: list[dict], *, width: int = 600, height: int = 400) -> str:
        """Simple occurrence scatter (lon/lat)."""
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">']
        parts.append(f'<rect width="{width}" height="{height}" fill="#f4f4f4"/>')
        for p in points:
            lng = p.get("lng", 0)
            lat = p.get("lat", 0)
            x = (lng + 180) / 360 * width
            y = (90 - lat) / 180 * height
            parts.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="4" fill="#c0392b" opacity="0.8"/>')
        parts.append("</svg>")
        return "\n".join(parts)

    def evidence_card_svg(self, claims: list[dict], *, width: int = 640, height: int = 200) -> str:
        """A provenance card: what we claim + the source behind it."""
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">']
        parts.append(f'<rect x="4" y="4" width="{width - 8}" height="{height - 8}" rx="8" fill="#fff" '
                     f'stroke="#ccc"/>')
        y = 28
        for c in claims[:5]:
            parts.append(
                f'<text x="16" y="{y}" font-family="sans-serif" font-size="12">'
                f'• {_esc(c.get("statement", ""))}  <tspan fill="#888">[{_esc(c.get("source", ""))}]</tspan></text>'
            )
            y += 24
        parts.append("</svg>")
        return "\n".join(parts)
