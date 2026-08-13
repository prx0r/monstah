"""Channel abstraction: a theme = evidence adapter + policies over the core engine.

Every channel runs the SAME chain:

    ENTITY -> ENVIRONMENT -> RELATION -> SCENARIO -> SIMULATION -> EVENT -> STORY -> SHOT

The channel is a bundle of policies over one engine:

    EvidenceAdapter      : which sources populate entities/environments
    ReconstructionPolicy : how evidence -> simulation model (explicit promotion)
    DiscoveryPolicy      : how the database writes the editorial calendar
    TruthPolicy          : whether a scenario is valid historically vs lab
    SimulationPolicy     : how a taxon becomes a combatant (game proxy)
    NarrativePolicy      : what the episode is allowed to claim
    MediaPolicy          : how a canonical event becomes a shot

The type firewall (core.truth) keeps game-proxy combat stats from ever leaking
into scientific reconstruction state.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ..core.models import Entity, Environment, Reference
from ..core.truth import Layer, TaxonFacts, TypedValue
from ..discovery import Candidate, OverlapResult, ScenarioDiscovery, Taxon, check_historical_overlap
from ..pipeline import PipelineOutput, run_candidate
from ..simulations import Combatant


# --- manifest ---------------------------------------------------------------
@dataclass
class ChannelManifest:
    """Metadata + the reusable assets a channel has already built up."""

    name: str
    title: str
    description: str = ""
    entities: dict[str, Entity] = field(default_factory=dict)
    environments: dict[str, Environment] = field(default_factory=dict)
    versions: dict[str, str] = field(default_factory=dict)  # entity -> reconstruction version
    asset_uris: dict[str, str] = field(default_factory=dict)  # entity -> R2 asset uri


# --- evidence ---------------------------------------------------------------
class EvidenceAdapter(ABC):
    """How a theme turns external sources into taxa/environments."""

    @abstractmethod
    def load_taxa(self, limit: int = 50) -> list[Taxon]:
        """Populate taxa from this channel's evidence sources (real data)."""

    def environments(self) -> list[Environment]:
        return []

    def environment_for_candidate(self, candidate: Candidate, taxa_by_ref: dict[str, Taxon]) -> Environment | None:
        """Bind a real environment to a candidate (no domain leakage)."""
        return None


# --- policies ---------------------------------------------------------------
class ReconstructionPolicy(ABC):
    """How evidence becomes a simulation model, through explicit promotion."""

    @abstractmethod
    def build(self, taxon: Taxon) -> TaxonFacts:
        """Return reconstruction/simulation params, labeled, never implicit."""


class SimulationPolicy(ABC):
    """How a taxon becomes a combatant. Returns None for non-combat channels."""

    def combatant_for(self, taxon: Taxon) -> Combatant | None:
        return None

    def resolve(self, a: Taxon, b: Taxon) -> tuple[Combatant, Combatant] | None:
        ca = self.combatant_for(a)
        cb = self.combatant_for(b)
        if ca is None or cb is None:
            return None
        return (ca, cb)


class TruthPolicy(ABC):
    """Whether a scenario is valid under the channel's truth rules."""

    def validate(self, candidate: Candidate, a: Taxon, b: Taxon) -> OverlapResult:
        if candidate.mode == "historical":
            return check_historical_overlap(
                a_range=(a.min_ma, a.max_ma),
                b_range=(b.min_ma, b.max_ma),
                a_env=set(a.env),
                b_env=set(b.env),
                a_region=a.region,
                b_region=b.region,
            )
        # lab mode: suspend only co-occurrence; report that explicitly
        return check_historical_overlap(
            a_range=(a.min_ma, a.max_ma),
            b_range=(b.min_ma, b.max_ma),
            a_env=set(a.env),
            b_env=set(b.env),
            a_region="global",
            b_region="global",
        )

    def allows(self, mode: str, overlap: OverlapResult) -> bool:
        """A channel's modes must respect its truth layer."""
        if mode == "historical":
            return overlap.valid_historical
        return True  # lab is explicitly counterfactual


class NarrativePolicy(ABC):
    def label(self, mode: str, overlap: OverlapResult) -> str:
        return "COUNTERFACTUAL LAB SIMULATION" if mode != "historical" else "HISTORICAL RECONSTRUCTION"


class MediaPolicy(ABC):
    def environment(self, candidate: Candidate, envs: dict[str, Environment]) -> str:
        if candidate.environment and candidate.environment.key in envs:
            return candidate.environment.key
        return ""


class DiscoveryPolicy(ABC):
    def discover(self, taxa: list[Taxon], top_n: int = 10) -> list[Candidate]:
        return ScenarioDiscovery(taxa).generate(top_n)


# --- channel ----------------------------------------------------------------
class Channel:
    """A theme running the shared engine with a bundle of policies."""

    def __init__(
        self,
        manifest: ChannelManifest,
        adapter: EvidenceAdapter,
        *,
        reconstruction: ReconstructionPolicy | None = None,
        simulation: SimulationPolicy | None = None,
        truth: TruthPolicy | None = None,
        narrative: NarrativePolicy | None = None,
        media: MediaPolicy | None = None,
        discovery: DiscoveryPolicy | None = None,
        mode: str = "historical",
        n_runs: int = 1000,
    ) -> None:
        self.manifest = manifest
        self.adapter = adapter
        self.reconstruction = reconstruction or _IdentityReconstruction()
        self.simulation = simulation or _CombatSimulation()
        self.truth = truth or TruthPolicy()
        self.narrative = narrative or NarrativePolicy()
        self.media = media or MediaPolicy()
        self.discovery = discovery or DiscoveryPolicy()
        self.mode = mode
        self.n_runs = n_runs
        self._envs = {e.id: e for e in adapter.environments()}

    # -- evidence step: build the graph -------------------------------
    def ingest(self, limit: int = 50) -> list[Taxon]:
        taxa = self.adapter.load_taxa(limit=limit)
        for t in taxa:
            self.manifest.entities.setdefault(
                t.ref.key,
                Entity(refs=[t.ref], kind="taxon", name=t.name, traits=t.facts.scientific_flat()),
            )
            self.reconstruction.build(t)
        return taxa

    # -- discovery step: let the database write the calendar -----------
    def discover(self, taxa: list[Taxon], top_n: int = 10) -> list[Candidate]:
        return self.discovery.discover(taxa, top_n)

    # -- truth step: strict validity by mode ----------------------------
    def validate(self, candidate: Candidate, taxa_by_ref: dict[str, Taxon]) -> OverlapResult:
        a = taxa_by_ref[candidate.entities[0].key]
        b = taxa_by_ref[candidate.entities[1].key]
        return self.truth.validate(candidate, a, b)

    # -- simulation step: fight them with the shared engine ------------
    def produce(self, candidate: Candidate, taxa_by_ref: dict[str, Taxon]) -> PipelineOutput:
        overlap = self.validate(candidate, taxa_by_ref)
        if not self.truth.allows(candidate.mode, overlap):
            raise ValueError(
                f"scenario invalid under {candidate.mode} mode: {overlap.summary()}"
            )
        a = taxa_by_ref[candidate.entities[0].key]
        b = taxa_by_ref[candidate.entities[1].key]
        pair = self.simulation.resolve(a, b)
        if pair is None:
            # NON-COMBAT path: a graph/data story, no battle engine
            return self.produce_graph(candidate, taxa_by_ref, overlap)
        attacker, defender = pair
        # bind a real environment (removes PALEO/domain leakage)
        env = self.adapter.environment_for_candidate(candidate, taxa_by_ref)
        return run_candidate(
            candidate,
            taxa_by_ref,
            n_runs=self.n_runs,
            attacker=attacker,
            defender=defender,
            overlap=overlap,
            environment=env,
        )

    def produce_graph(
        self,
        candidate: Candidate,
        taxa_by_ref: dict[str, Taxon],
        overlap: OverlapResult | None = None,
    ) -> PipelineOutput:
        """Non-combat editorial path: a story from the graph, no simulation.

        Channels override this when their content is data/graph/timeline
        stories rather than battles (thesis §50).
        """
        from ..narrative import EpisodeSpec

        a = taxa_by_ref[candidate.entities[0].key]
        b = taxa_by_ref[candidate.entities[1].key]
        overlap = overlap or self.validate(candidate, taxa_by_ref)
        story = EpisodeSpec(
            title=f"{a.name} — {b.name}: {candidate.template}",
            scenario_id=candidate.template,
            channel=self.theme,
            hook=f"What is the relationship between {a.name} and {b.name}?",
            evidence=overlap.summary(),
            conclusion="Graph/data story; no battle simulation run.",
        )
        # media step still binds a real environment
        env = self.adapter.environment_for_candidate(candidate, taxa_by_ref)
        from ..media.shots import compile_shots

        shots = compile_shots(
            entity_versions=[
                {"entity": a.name, "version": "R1", "asset_uri": ""},
                {"entity": b.name, "version": "R1", "asset_uri": ""},
            ],
            environment=env.id if env else "",
            event_log=[{"t": 0, "actor": a.name, "action": "INTERACT"}],
        )
        return PipelineOutput(
            candidate=candidate,
            overlap=overlap,
            mc=type("MC", (), {"outcomes": {}, "selected": {}, "dominant_outcome": ""}),
            significance=type("SIG", (), {"score": 0.0, "signals": []}),
            story=story,
            shots=shots,
        )

    # -- render step: story + shots -> LTX, then store ----------------
    def render(self, output: PipelineOutput) -> PipelineOutput:
        output.story = _apply_mode_label(output.story, self.narrative.label(self.mode, output.overlap))
        output.bundle = self._ltx_bundle(output)
        return output

    def _ltx_bundle(self, output: PipelineOutput):
        """Convert compiled shots into render-ready LTX ShotSpecs."""
        from ..media import Project, RendererManifest, ShotBundle, to_ltx_shots

        ltx_shots = to_ltx_shots(output.shots, project=Project.MONSTAH, mode=output.candidate.mode)
        manifest = RendererManifest(
            renderer_family="ltx",
            renderer_version="2.3",
            backend="comfyui",
            model_variant="ltx-2-3-fast",
        )
        return ShotBundle(project=self.theme, manifest=manifest, shots=ltx_shots)

    def publish(self, output: PipelineOutput, store=None) -> str:
        """Persist the render bundle + story to R2 as canonical output."""
        import json

        from ..media.storage import R2Store

        store = store or R2Store(prefix=f"canonical/channels/{self.theme}")
        payload = {
            "story": output.story.render(),
            "overlap": output.overlap.__dict__,
            "shots": output.bundle.to_dict() if hasattr(output.bundle, "to_dict") else output.bundle,
        }
        key = f"{'_'.join(e.key for e in output.candidate.entities)}/{output.candidate.template}.json"
        return store.put_bytes(key, json.dumps(payload, indent=2).encode(), content_type="application/json")

    @property
    def theme(self) -> str:
        return self.manifest.name


class _IdentityReconstruction(ReconstructionPolicy):
    def build(self, taxon: Taxon) -> TaxonFacts:
        return taxon.facts


class _CombatSimulation(SimulationPolicy):
    def combatant_for(self, taxon: Taxon) -> Combatant | None:
        gp = taxon.game_proxy
        if not gp:
            return None
        return Combatant(
            {
                "name": taxon.name,
                "ref": taxon.ref,
                "armor_class": int(gp.get("armor_class", 12)),
                "hit_points": int(gp.get("hit_points", 50)),
                "attack_bonus": int(gp.get("attack_bonus", 5)),
                "damage_dice": gp.get("damage_dice", "2d6+3"),
                "speed": float(gp.get("speed", 8.0)),
                "perception": float(gp.get("perception", 60.0)),
                "diet": taxon.diet,
            }
        )


def _apply_mode_label(story, label: str):
    from dataclasses import replace

    if not hasattr(story, "conclusion"):
        return story
    return replace(story, conclusion=f"[{label}]\n" + (story.conclusion or ""))
