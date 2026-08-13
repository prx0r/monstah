"""End-to-end pipeline runner (§33, §48).

For a scenario candidate: verify historical overlap, build participant
capability models, run Monte Carlo, detect significance, compile a story,
compile a shot graph, and persist the bundle. Optionally stores the canonical
bundle to R2.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from .discovery import Candidate, OverlapResult, Taxon, check_historical_overlap
from .narrative import EpisodeSpec, detect_significance, compile_story
from .simulations import Participant, run_monte_carlo
from .media.shots import compile_shots
from .media.storage import R2Store


@dataclass
class PipelineOutput:
    candidate: Candidate
    overlap: OverlapResult
    mc: Any
    significance: Any
    story: EpisodeSpec
    shots: list
    bundle: dict = field(default_factory=dict)

    def save(self, path: str) -> str:
        import os

        os.makedirs(path, exist_ok=True)
        out = {
            "candidate": {
                "template": self.candidate.template,
                "entities": [e.key for e in self.candidate.entities],
                "mode": self.candidate.mode,
                "score": self.candidate.score,
            },
            "overlap": self.overlap.summary(),
            "valid_historical": self.overlap.valid_historical,
            "outcomes": self.mc.outcomes,
            "selected_runs": self.mc.selected,
            "significance": {
                "score": self.significance.score,
                "signals": self.significance.signals,
                "factors": self.significance.factors,
            },
            "story": self.story.render(),
            "shots": [s.__dict__ for s in self.shots],
        }
        fp = f"{path}/{'_'.join(e.key for e in self.candidate.entities)}_{self.candidate.template}.json"
        with open(fp, "w") as f:
            json.dump(out, f, indent=2)
        return fp


def _participant(t: Taxon) -> Participant:
    return Participant(
        ref=t.ref,
        name=t.name,
        diet=t.diet,
        mass_kg=t.traits.get("mass_kg", 2000.0),
        speed=t.traits.get("speed", 8.0),
        bite_force=t.traits.get("bite_force", 800.0),
        stamina=t.traits.get("stamina", 10.0),
        defence=t.traits.get("defence", 0.3),
    )


def run_candidate(
    candidate: Candidate,
    taxa_by_ref: dict[str, Taxon],
    *,
    n_runs: int = 1000,
    envs: dict | None = None,
    title: str | None = None,
) -> PipelineOutput:
    a_ref, b_ref = candidate.entities[0], candidate.entities[1]
    a, b = taxa_by_ref[a_ref.key], taxa_by_ref[b_ref.key]

    overlap = check_historical_overlap(
        a_range=(a.min_ma, a.max_ma),
        b_range=(b.min_ma, b.max_ma),
        a_env=set(a.env),
        b_env=set(b.env),
        a_region="",
        b_region="",
        spatial_shared=True,
    )

    # decide actor roles by diet
    pred, prey = (a, b) if a.diet == "carnivore" else (b, a)
    mc = run_monte_carlo(
        _participant(pred),
        _participant(prey),
        n=n_runs,
        scenario_id=candidate.template,
    )
    significance = detect_significance(
        scenario_id=candidate.template,
        outcome_dist=mc.outcomes,
        uncertainty=a.traits.get("uncertainty", 0.0),
        rare_relationship=candidate.template in ("predation", "competition"),
        counterintuitive=mc.dominant_outcome == "prey_escape",
    )
    story = compile_story(
        title=title or f"{pred.name} vs {prey.name}: {candidate.template}",
        scenario_id=candidate.template,
        question=f"Could {pred.name} successfully hunt {prey.name}?",
        evidence_summary=overlap.summary(),
        reconstruction_summary=f"Body models from reconstruction parameters (mass {a.traits.get('mass_kg')} kg).",
        outcome_dist=mc.outcomes,
        crux="The dominant variable governing outcome is the assumed speed/stamina balance.",
        uncertainty_note="Results are conditional on reconstruction assumptions; see provenance.",
    )
    # a simple event log for shots
    event_log = [{"t": 0, "actor": pred.name, "action": "CHASE"}, {"t": 3, "actor": prey.name, "action": "RETREAT"}]
    shots = compile_shots(
        entity_versions=[
            {"entity": pred.name, "version": "R1", "asset_uri": ""},
            {"entity": prey.name, "version": "R1", "asset_uri": ""},
        ],
        environment="PALEO",
        event_log=event_log,
    )
    return PipelineOutput(candidate=candidate, overlap=overlap, mc=mc, significance=significance, story=story, shots=shots)


def save_to_r2(output: PipelineOutput, store: R2Store | None = None) -> str:
    import io

    store = store or R2Store(prefix="canonical/simulations")

    def _ref(r) -> str:
        return f"{r.namespace}:{r.key}"

    bundle = {
        "candidate": {
            "template": output.candidate.template,
            "entities": [_ref(e) for e in output.candidate.entities],
            "mode": output.candidate.mode,
            "score": output.candidate.score,
            "factors": output.candidate.factors,
        },
        "overlap": output.overlap.__dict__,
        "outcomes": output.mc.outcomes,
        "selected_runs": output.mc.selected,
        "significance": {"score": output.significance.score, "signals": output.significance.signals},
        "story": output.story.render(),
    }
    key = f"{'_'.join(_ref(e) for e in output.candidate.entities)}/{output.candidate.template}.json"
    return store.put_bytes(key, json.dumps(bundle, indent=2).encode(), content_type="application/json")
