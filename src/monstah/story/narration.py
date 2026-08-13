"""Narration compiled from claims (MVP Phase 25).

Every factual clause knows its assertion ids / source refs / status, so script
generation automatically distinguishes KNOWN vs RECONSTRUCTED vs MODELLED vs
UNKNOWN — never hand-authored caveats.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class NarrativeClause:
    text: str
    assertion_ids: list[str] = field(default_factory=list)
    source_refs: list[str] = field(default_factory=list)
    status: str = "INFERRED"  # OBSERVED | LITERATURE_ESTIMATE | INFERRED | MODELLED | SPECULATIVE

    def qualify(self) -> str:
        """Wrap the clause in the epistemically-correct framing."""
        if self.status in ("OBSERVED", "DIRECT_MEASUREMENT"):
            prefix = "Fossils place these animals in"
            return f"{prefix} {self.text.lstrip('., ')}"
        if self.status in ("LITERATURE_ESTIMATE", "INFERRED", "RECONSTRUCTED"):
            return f"The reconstruction is likely: {self.text.lstrip('., ')}"
        if self.status in ("MODELLED", "GAME_PROXY"):
            return f"In our simulation: {self.text.lstrip('., ')}"
        if self.status == "SPECULATIVE":
            return f"Some workers speculate: {self.text.lstrip('., ')}"
        return f"We cannot currently establish: {self.text.lstrip('., ')}"


def compile_narration(clauses: list[NarrativeClause]) -> str:
    return "\n".join(c.qualify() for c in clauses)
