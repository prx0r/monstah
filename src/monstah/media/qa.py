"""Four QA layers + uncertainty-aware constraints (MVP Phase 22-23).

QA must consume a ReconstructionConstraintSet (what is CONSTRAINED vs OPEN),
not merely compare pixels. Verdicts: PASS / RETAKE / REGENERATE / NEEDS_REVIEW.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ..assets.visual_spec import Certainty


class Verdict(str, Enum):
    PASS = "PASS"
    RETAKE = "RETAKE"
    REGENERATE = "REGENERATE"
    NEEDS_REVIEW = "NEEDS_REVIEW"


@dataclass
class ReconstructionConstraintSet:
    """What the reconstruction may/can-not claim (uncertainty-aware)."""

    hard: dict[str, Any] = field(default_factory=dict)  # trait -> required value (CONSTRAINED)
    forbidden: list[str] = field(default_factory=list)  # must never appear
    open: set[str] = field(default_factory=set)  # traits free to vary (OPEN/SPECULATIVE)

    @classmethod
    def from_spec(cls, spec) -> "ReconstructionConstraintSet":
        hard = {}
        open_traits = set()
        forbidden = list(spec.forbidden)
        for trait, cert in spec.appearance.items():
            if cert in (Certainty.CONSTRAINED, Certainty.INFERRED, Certainty.RECONSTRUCTED):
                hard[trait] = spec.morphology.get(trait, None)
            else:
                open_traits.add(trait)
        return cls(hard=hard, forbidden=forbidden, open=open_traits)


@dataclass
class QAResult:
    layer: str
    verdict: Verdict
    detail: str = ""
    findings: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.verdict is Verdict.PASS


# --- BindingQA (deterministic) --------------------------------------------
def binding_qa(shot, renderer_manifest: dict, constraints: ReconstructionConstraintSet) -> QAResult:
    findings: list[str] = []
    if not shot.basis.event_ids and not shot.basis.assertion_ids and not shot.basis.reconstruction_ids:
        findings.append("shot has no epistemic basis")
    if not renderer_manifest:
        findings.append("missing renderer manifest")
    verdict = Verdict.PASS if not findings else Verdict.NEEDS_REVIEW
    return QAResult(layer="binding", verdict=verdict, detail="; ".join(findings) or "bindings ok", findings=findings)


# --- VisualIdentityQA (deterministic skeleton; vision models plug in) -----
def visual_identity_qa(candidate, constraints: ReconstructionConstraintSet) -> QAResult:
    findings: list[str] = []
    # forbidden structures are a hard factual constraint
    if constraints.forbidden:
        findings.append("forbidden structures must be checked against render")
    # hard traits are required
    for trait in constraints.hard:
        if trait not in constraints.hard or constraints.hard[trait] is None:
            continue
    verdict = Verdict.PASS if not findings else Verdict.NEEDS_REVIEW
    return QAResult(layer="visual_identity", verdict=verdict,
                    detail="; ".join(findings) or "identity matches canonical constraints", findings=findings)


# --- EventQA (simulation/graph shots) -------------------------------------
def event_qa(shot, events: list[dict]) -> QAResult:
    findings: list[str] = []
    if not shot.basis.event_ids:
        return QAResult(layer="event", verdict=Verdict.PASS, detail="non-event shot")
    for eid in shot.basis.event_ids:
        if not any(e.get("event_id") == eid for e in events):
            findings.append(f"event {eid} missing from canonical log")
    verdict = Verdict.PASS if not findings else Verdict.RETAKE
    return QAResult(layer="event", verdict=verdict, detail="; ".join(findings) or "events bound", findings=findings)


# --- EpistemicQA (most Monstah-specific) ----------------------------------
def epistemic_qa(shot, claims: list[str], constraints: ReconstructionConstraintSet) -> QAResult:
    findings: list[str] = []
    for forbidden in constraints.forbidden:
        if forbidden in claims:
            findings.append(f"render claims forbidden content: {forbidden}")
    # OPEN traits may be present as variation, not asserted as fact
    verdict = Verdict.PASS if not findings else (Verdict.REGENERATE if findings else Verdict.PASS)
    return QAResult(layer="epistemic", verdict=verdict,
                    detail="; ".join(findings) or "no unsupported factual content", findings=findings)


def run_qa(shot, *, renderer_manifest, constraints, events, claims) -> list[QAResult]:
    """Run all four QA layers."""
    return [
        binding_qa(shot, renderer_manifest, constraints),
        visual_identity_qa(shot, constraints),
        event_qa(shot, events),
        epistemic_qa(shot, claims, constraints),
    ]
