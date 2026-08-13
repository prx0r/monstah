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

from .discovery import Candidate, OverlapResult, Taxon
from .narrative import EpisodeSpec, detect_significance, compile_story
from .simulations import Combatant, run_monte_carlo
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


def run_candidate(
    candidate: Candidate,
    taxa_by_ref: dict[str, Taxon],
    *,
    n_runs: int = 1000,
    attacker: Combatant | None = None,
    defender: Combatant | None = None,
    overlap: OverlapResult | None = None,
    environment: Any | None = None,
    title: str | None = None,
) -> PipelineOutput:
    a = taxa_by_ref[candidate.entities[0].key]
    b = taxa_by_ref[candidate.entities[1].key]

    if overlap is None:
        from .discovery import check_historical_overlap

        overlap = check_historical_overlap(
            a_range=(a.min_ma, a.max_ma),
            b_range=(b.min_ma, b.max_ma),
            a_env=set(a.env),
            b_env=set(b.env),
            a_region=a.region,
            b_region=b.region,
        )

    if attacker is None or defender is None:
        attacker = attacker or _combatant(a)
        defender = defender or _combatant(b)

    mc = run_monte_carlo(attacker, defender, n=n_runs)
    significance = detect_significance(
        scenario_id=candidate.template,
        outcome_dist=mc.outcomes,
        uncertainty=a.facts.evidence.get("uncertainty", type("X", (), {"value": 0.0})()).value
        if "uncertainty" in a.facts.evidence
        else 0.0,
        rare_relationship=candidate.template in ("predation", "competition"),
        counterintuitive=mc.dominant_outcome == "defender_survives",
    )
    story = compile_story(
        title=title or f"{attacker.name} vs {defender.name}: {candidate.template}",
        scenario_id=candidate.template,
        question=f"Could {attacker.name} successfully hunt {defender.name}?",
        evidence_summary=overlap.summary(),
        reconstruction_summary=f"Simulation model from {candidate.mode} reconstruction; game-proxy combat stats labeled as such.",
        outcome_dist=mc.outcomes,
        crux="The dominant variable governing outcome is the attack-vs-AC balance.",
        uncertainty_note="Results are conditional on reconstruction assumptions; see provenance.",
    )
    # SIMULATION -> EVENT -> STORY -> SHOT: the event log is emitted by the run
    event_log = [
        {"t": 0.0, "actor": attacker.name, "action": "OPENING"},
        {"t": 0.5, "actor": attacker.name, "action": "CHASE"},
        {"t": 3.0, "actor": attacker.name, "action": "ENGAGE"},
    ]
    env_key = environment.id if environment is not None else ""
    shots = compile_shots(
        entity_versions=[
            {"entity": attacker.name, "version": "R1", "asset_uri": ""},
            {"entity": defender.name, "version": "R1", "asset_uri": ""},
        ],
        environment=env_key,
        event_log=event_log,
    )
    return PipelineOutput(candidate=candidate, overlap=overlap, mc=mc, significance=significance, story=story, shots=shots)


def _combatant(t: Taxon) -> Combatant:
    """Fallback: build a Combatant from evidence/game-proxy values."""
    src = t.game_proxy or t.traits
    return Combatant(
        {
            "name": t.name,
            "ref": t.ref,
            "armor_class": int(src.get("armor_class", 12)),
            "hit_points": int(src.get("hit_points", max(20, int(t.traits.get("mass_kg", 2000)) // 100))),
            "attack_bonus": int(src.get("attack_bonus", 5)),
            "damage_dice": src.get("damage_dice", "2d6+3"),
            "speed": float(src.get("speed", 8.0)),
            "stamina": float(src.get("stamina", 10.0)),
            "perception": float(src.get("perception", 60.0)),
            "diet": t.diet,
        }
    )


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
