"""Story compiler (§35) and provenance-aware narrative claims (§16, §38).

Turns a scenario + evidence pack + simulation summary into an EpisodeSpec using
the canonical house structure:

    HOOK -> EVIDENCE -> RECONSTRUCTION -> SIMULATION -> REPRESENTATIVE EVENT
    -> CRUX -> UNCERTAINTY -> CONCLUSION
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class NarrativeClaim:
    """A sentence in an episode that must resolve back to evidence (§38)."""

    text: str
    claim_id: str
    assertion_ids: list[str] = field(default_factory=list)
    source_ids: list[str] = field(default_factory=list)
    status: str = "INFERRED"

    @property
    def resolves(self) -> bool:
        return bool(self.assertion_ids and self.source_ids)


@dataclass
class EpisodeSpec:
    title: str
    scenario_id: str
    channel: str = ""
    hook: str = ""
    evidence: str = ""
    reconstruction: str = ""
    simulation: str = ""
    representative_event: str = ""
    crux: str = ""
    uncertainty: str = ""
    conclusion: str = ""
    narrative_claims: list[NarrativeClaim] = field(default_factory=list)

    def blocks(self) -> list[tuple[str, str]]:
        return [
            ("HOOK", self.hook),
            ("EVIDENCE", self.evidence),
            ("RECONSTRUCTION", self.reconstruction),
            ("SIMULATION", self.simulation),
            ("REPRESENTATIVE EVENT", self.representative_event),
            ("CRUX", self.crux),
            ("UNCERTAINTY", self.uncertainty),
            ("CONCLUSION", self.conclusion),
        ]

    def render(self) -> str:
        lines = [f"# {self.title}\n"]
        for label, body in self.blocks():
            if body:
                lines.append(f"## {label}\n{body}\n")
        return "\n".join(lines)


def compile_story(
    *,
    title: str,
    scenario_id: str,
    question: str,
    evidence_summary: str,
    reconstruction_summary: str,
    outcome_dist: dict[str, float],
    crux: str,
    uncertainty_note: str,
    channel: str = "",
) -> EpisodeSpec:
    """Assemble a narrative from pipeline outputs. Never asserts facts beyond
    what the simulation/evidence establishes."""

    dominant = max(outcome_dist, key=outcome_dist.get) if outcome_dist else ""
    dom_prob = outcome_dist.get(dominant, 0.0)
    sim_text = f"Across {sum(outcome_dist.values()):.0%} scaled runs, the dominant outcome was {dominant} ({dom_prob:.0%})."
    conclusion = (
        f"The simulation establishes that under the chosen reconstructions, {dominant} "
        f"is the modal outcome ({dom_prob:.0%}). It does not establish certainty; "
        f"the result is conditional on the reconstruction assumptions described above."
    )
    return EpisodeSpec(
        title=title,
        scenario_id=scenario_id,
        channel=channel,
        hook=question,
        evidence=evidence_summary,
        reconstruction=reconstruction_summary,
        simulation=sim_text,
        representative_event=f"A representative seeded run producing {dominant}.",
        crux=crux,
        uncertainty=uncertainty_note,
        conclusion=conclusion,
    )
