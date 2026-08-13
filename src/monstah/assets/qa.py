"""ReconstructionVisualQA (MVP Phase 6, 7).

Monstah QA asks: does the image match the evidence-constrained reconstruction?
Failures are classified by epistemic importance (P0_FACTUAL / P1_RECONSTRUCTION /
P2_VISUAL). It does NOT falsely imply every visible property is established.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .image_backend import ImageCandidate
from .visual_spec import VisualReconstructionSpec, Certainty


class QASeverity(str, Enum):
    P0_FACTUAL = "P0_FACTUAL"
    P1_RECONSTRUCTION = "P1_RECONSTRUCTION"
    P2_VISUAL = "P2_VISUAL"


@dataclass
class QAFinding:
    check: str
    severity: QASeverity
    detail: str = ""

    @property
    def blocks_approval(self) -> bool:
        return self.severity in (QASeverity.P0_FACTUAL, QASeverity.P1_RECONSTRUCTION)


@dataclass
class ReconstructionVisualQA:
    spec: VisualReconstructionSpec
    findings: list[QAFinding] = field(default_factory=list)

    def assess(self, candidate: ImageCandidate) -> "ReconstructionVisualQA":
        """Run deterministic checks against the spec. (Vision models plug in here.)"""
        # P0: forbidden structures must not appear (a hard factual constraint)
        if candidate.generator_manifest.get("spec", {}).get("forbidden"):
            self.findings.append(
                QAFinding("forbidden_structure", QASeverity.P0_FACTUAL,
                          "spec declares forbidden structures that must not render")
            )
        # P1: required morphology keys must be declared
        morph = candidate.generator_manifest.get("spec", {}).get("morphology", {})
        for part in ("skull", "torso", "limbs", "tail"):
            if part in self.spec.morphology and part not in morph:
                self.findings.append(
                    QAFinding("morphology_missing", QASeverity.P1_RECONSTRUCTION,
                              f"reconstruction declares {part} but candidate manifest omits it")
                )
        # P2: OPEN/SPECULATIVE traits must be flagged, not asserted
        for trait, certainty in self.spec.appearance.items():
            if certainty in (Certainty.OPEN, Certainty.SPECULATIVE):
                self.findings.append(
                    QAFinding("unconstrained_visual", QASeverity.P2_VISUAL,
                              f"trait {trait} is {certainty.value}; not assertable")
                )
        return self

    @property
    def passes(self) -> bool:
        return not any(f.blocks_approval for f in self.findings)

    def report(self) -> dict[str, Any]:
        return {
            "passes": self.passes,
            "findings": [
                {"check": f.check, "severity": f.severity.value, "detail": f.detail} for f in self.findings
            ],
        }
