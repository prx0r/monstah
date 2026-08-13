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

from monstah.core.models import Entity, Environment, Reference
from monstah.core.truth import Layer, TaxonFacts, TypedValue
from monstah.discovery import Candidate, OverlapResult, ScenarioDiscovery, Taxon, check_historical_overlap
from monstah.evidence.builder import build_evidence_pack, build_reconstruction, source_from
from monstah.evidence.models import Assertion, Claim, Reconstruction, Source
from monstah.narrative.novelty import NoveltyScorer
from monstah.pipeline import PipelineOutput, run_candidate
from monstah.simulations import Combatant


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
    sources: dict[str, Source] = field(default_factory=dict)
    claims: dict[str, list[Claim]] = field(default_factory=dict)
    assertions: dict[str, list[Assertion]] = field(default_factory=dict)
    reconstructions: dict[str, Reconstruction] = field(default_factory=dict)


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
    def __init__(self) -> None:
        self.novelty = NoveltyScorer()

    def discover(self, taxa: list[Taxon], top_n: int = 10) -> list[Candidate]:
        sd = ScenarioDiscovery(taxa, novelty=self.novelty)
        cands = sd.generate(top_n)
        return cands

    def commit(self, template: str, entities: list[Reference]) -> None:
        self.novelty.commit(template, entities)


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
        self._analytics = None  # lazily created DuckStore

    def _get_analytics(self):
        from monstah.data.duck import DuckStore

        if self._analytics is None:
            self._analytics = DuckStore()
        return self._analytics

    # -- evidence step: build the graph -------------------------------
    def ingest(self, limit: int = 50) -> list[Taxon]:
        taxa = self.adapter.load_taxa(limit=limit)
        for t in taxa:
            src = source_from(
                t.ref.namespace,
                t.ref.key,
                type="evidence_record",
                title=t.name,
            )
            self.manifest.sources[t.ref.key] = src
            # persist the full evidence chain: source → claim → assertion
            pack = build_evidence_pack(t.ref, t.facts, src)
            self.manifest.claims[t.ref.key] = pack.claims
            self.manifest.assertions[t.ref.key] = pack.assertions
            # versioned reconstruction referencing the SAME persisted assertion IDs
            rec = build_reconstruction(t.ref, t.facts, src, version="R1", assertions=pack.assertions)
            self.manifest.reconstructions[t.ref.key] = rec
            self.manifest.versions[t.ref.key] = rec.version
            # persist the evidence chain to the durable analytical store
            self._get_analytics().write_evidence_pack(t.ref.key, src, pack.claims, pack.assertions, rec)
            self.manifest.entities.setdefault(
                t.ref.key,
                Entity(
                    refs=[t.ref],
                    kind="taxon",
                    name=t.name,
                    traits=t.facts.scientific_flat(),
                    properties={"reconstruction": rec.version, "assertions": rec.assertions},
                ),
            )
            self.reconstruction.build(t)
        return taxa

    # -- discovery step: let the database write the calendar -----------
    def discover(self, taxa: list[Taxon], top_n: int = 10) -> list[Candidate]:
        return self.discovery.discover(taxa, top_n)

    # -- run a candidate through the whole chain -----------------------
    def run(self, candidate: Candidate, taxa_by_ref: dict[str, Taxon]):
        out = self.produce(candidate, taxa_by_ref)
        self.render(out)
        self.discovery.commit(candidate.template, candidate.entities)
        self._record(out)
        return out

    def _record(self, output: PipelineOutput) -> None:
        """Persist simulation results + canonical events into the durable store."""
        store = self._get_analytics()
        for template, prob in output.mc.outcomes.items():
            store.register_sim_results(
                [{"scenario": output.candidate.template, "outcome": template, "probability": prob}]
            )
        rep_idx = output.mc.selected.get("representative", 0) if output.mc else 0
        if getattr(output, "event_log", None):
            store.write_events(output.candidate.template, rep_idx, output.event_log)

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
            evidence=self.manifest.assertions,
            versions=self.manifest.versions,
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
        from monstah.narrative import EpisodeSpec

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
        # media step still binds a real environment; basis is GRAPH_DERIVED
        # (a graph relationship, NOT a simulated canonical event)
        from monstah.media.ltx import ShotBasis
        from monstah.media.shots import EntityVersion, ShotSpec

        env = self.adapter.environment_for_candidate(candidate, taxa_by_ref)
        v_a = self.manifest.versions.get(a.ref.key, "R1")
        v_b = self.manifest.versions.get(b.ref.key, "R1")
        shots = [
            ShotSpec(
                index=0,
                entities=[
                    EntityVersion(entity=a.name, version=v_a, asset_uri=""),
                    EntityVersion(entity=b.name, version=v_b, asset_uri=""),
                ],
                environment=env.id if env else "",
                event="",
                event_ids=[],
                basis=ShotBasis.GRAPH_DERIVED,
                start_state={},
                end_state={},
                constraints=["graph-derived reconstruction; no simulation event"],
            )
        ]
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
        """Convert compiled shots into render-ready LTX ShotSpecs.

        Renderer config comes from a profile (config), never hardcoded in the
        domain layer.
        """
        from monstah.config import get_settings
        from monstah.media import Project, RendererManifest, ShotBundle, to_ltx_shots

        ltx_shots = to_ltx_shots(output.shots, project=Project.MONSTAH, mode=output.candidate.mode)
        self._attach_references(ltx_shots, output)
        profile = get_settings().renderer
        manifest = RendererManifest(
            renderer_family=profile.family,
            renderer_version=profile.version,
            backend=profile.backend,
            model_variant=profile.model_variant,
            output={"resolution": profile.resolution, "fps": profile.fps, "generate_audio": profile.generate_audio},
        )
        return ShotBundle(project=self.theme, manifest=manifest, shots=ltx_shots)

    def _attach_references(self, ltx_shots, output: PipelineOutput) -> None:
        """Attach canonical reconstruction references to each shot (I2V input).

        Uses CanonicalAssetResolver: for extinct taxa it NEVER returns raw source
        references — only an approved canonical reconstruction is eligible. For
        extant taxa an explicit policy may allow observational morphology.
        """
        try:
            if getattr(self.adapter, "offline", False):
                return
            from monstah.media import AssetRole, CanonicalAssetResolver, ImageResolver

            canonical = CanonicalAssetResolver(
                source=ImageResolver(),
                allow_observational_as_canonical=not self._is_extinct_world(),
            )
            try:
                refs_by_entity: dict[str, list[dict]] = {}
                for ent in output.candidate.entities:
                    entity = self.manifest.entities.get(ent.key)
                    name = entity.name if entity else ent.key
                    version = self.manifest.versions.get(ent.key, "R1")
                    extinct = self._is_extinct(ent.key)
                    if name not in refs_by_entity:
                        refs_by_entity[name] = [
                            {"uri": c.original_uri, "license": c.license, "creator": c.creator}
                            for c in canonical.resolve(name, version, extinct=extinct)
                        ]
                for shot in ltx_shots:
                    key = shot.entity_versions[0].split(":")[0] if shot.entity_versions else ""
                    shot.references = refs_by_entity.get(key, [])
            finally:
                canonical.source.close()
        except Exception as e:
            # optional enrichment: fail open but never silently
            import logging

            logging.getLogger("monstah.media").warning("reference resolution failed: %s", e)

    def _is_extinct_world(self) -> bool:
        """Whether the theme reconstructs extinct worlds (never feed raw refs to LTX)."""
        return any(e.refs and e.refs[0].namespace == "paleo" for e in self.manifest.entities.values())

    def _is_extinct(self, entity_key: str) -> bool:
        return self._is_extinct_world()

    def publish(self, output: PipelineOutput, store=None) -> str:
        """Persist the render bundle + story to R2 AND the durable store."""
        import json

        from monstah.media.storage import R2Store

        store = store or R2Store(prefix=f"canonical/channels/{self.theme}")
        payload = {
            "story": output.story.render(),
            "overlap": output.overlap.__dict__,
            "shots": output.bundle.to_dict() if hasattr(output.bundle, "to_dict") else output.bundle,
        }
        key = f"{'_'.join(e.key for e in output.candidate.entities)}/{output.candidate.template}.json"
        r2_key = store.put_bytes(key, json.dumps(payload, indent=2).encode(), content_type="application/json")
        # durable analytical record
        self._get_analytics().write_episode(
            self.theme, output.candidate.template, output.story.title, payload
        )
        return r2_key

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
