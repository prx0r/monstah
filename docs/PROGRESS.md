# Progress

Status: **evidence-constrained world engine working end-to-end, 5 live channels,
25 tests, organized docs.** All work since the LTX production pack import.

## What is built (all verified working)

### Engine core
- **Type firewall** (`core/truth.py`) — EvidenceTrait / ReconstructionParameter /
  SimulationParameter / GameProxyParameter / NarrativeProjection; values layer-tagged.
- **Shared substrate** (`core/models.py`) — ENTITY / ENVIRONMENT / RELATION /
  SCENARIO / SIMULATION / EVENT / STORY / SHOT / ASSET.
- **Identifier crosswalk** (`core/identity.py`) — pbdb/gbif/ott/eol/worms/wikidata.
- **Evidence chain** (`evidence/`) — Source / Claim / Assertion / Reconstruction;
  `builder` turns ingested facts into versioned reconstructions; game-proxy held apart.

### Data ingest (`ingest/`)
PBDB, Macrostrat, GBIF, OBIS, GloBI, OpenTree, OpenAlex, Open5e — **all verified live,
no auth** (EOL now needs a key). Open5e = 3,207-statchlock game-proxy corpus.

### Simulation
- **d20 battle engine** (`simulations/d20.py`) — attack-vs-AC, damage dice, crits;
  `run_duel_events` emits the real canonical event log.
- **Replayable Monte Carlo** (`simulations/montecarlo.py`) — `(master_seed, run_index)`,
  selected runs replay exactly.
- **esper ECS** alternative system (`simulations/ecs_battle.py`).

### Discovery / narrative
- Scenario discovery + **strict historical overlap** (temporal+geo+env, real regions).
- **ContentHistory/novelty** — no placeholder; repetition penalized.
- Significance detector + story compiler with provenance-bearing narrative claims.

### Media
- **LTX ShotSpec** (`media/ltx.py`) — pydantic models matching the vendored schema;
  `canonicality` comes from the truth layer, never invented by the renderer.
- **Canonical asset system** (`media/asset.py`, `media/providers.py`) — provider-agnostic
  image discovery (GBIF, iNaturalist, Wikimedia; BHL key-gated), license policy
  (ALLOW/REVIEW/REJECT), evidence-fit ranking, versioned reconstruction assets.
- **R2 storage** (`media/storage.py`) — `R2Store` + `AssetStore` (source/entities/environments).

### Stores
- **DuckDB analytical** (`data/duck.py`) — occurrences, sim results.
- **Postgres canonical** (`data/postgres.py`) — maps `sql/postgres.sql` (incl. asset tables).

### Channels (live, 5)
`prehistoric` (battle) · `ancient-oceans` (battle) · `deep-blue` (OBIS battle) ·
`living-planet` (GloBI non-combat) · `tree-of-life` (OpenTree non-combat).

### Offline full-stack simulation
`monstah simulate <channel>` runs ingest→evidence→discovery→validity→battle→Monte Carlo→
significance→story→shots→LTX bundle, writes episode JSON, **no LTX/network**.

## Key fixes applied (peer review, commit 61d9ce1)
Historical mode wired; geographic validity no longer bypassed; Open5e stats kept out of
the evidence layer; Deep Blue genuinely OBIS-driven; MC runs replayable; real event log
(no fabricated events); non-combat channel path; PALEO/domain leakage removed. See
`REVIEW_NOTES.md`.

## Trending-data niche analysis (YouTube GB/CA/IN, n≈117k)
- **Blue ocean:** Prehistoric/Dinosaurs (9.4M avg, low supply) and Ancient Oceans
  (10.5M avg, lowest supply) → top breakout lanes.
- Matchups (1.26M avg) = Shorts discovery engine. Space (3.9M) = strong later.
- Weak: Evolution (208k), generic wildlife (633k). See `CHANNELS.md`.

## Integrity hardening (second peer review — G–N, done)
- **G — monotonic firewall:** promotions are strictly directed
  `EVIDENCE→RECONSTRUCTION→SIMULATION`; `TaxonFacts.add` rejects layer relabeling.
- **H — evidence chain persists:** `Source→Claim→Assertion→Reconstruction` share the
  SAME immutable IDs and are written to a **durable DuckDB store** (not just in-memory);
  `NarrativeClaim` resolves to real persisted Assertion IDs + Source refs.
- **I — canonical vs source assets:** `CanonicalAssetResolver` never feeds raw source
  refs to LTX for extinct taxa; extant only via an explicit policy.
- **J — provider/license semantics:** unknown license → REJECT (never REVIEW); BHL reads
  real rights (no manufactured PD); Wikimedia uses raw file URL + classification;
  iNaturalist actually selects open-data original; resolver preserves provider roles.
- **K — mode ≠ basis:** `ShotBasis` (SIMULATION_EVENT/RECONSTRUCTION/GRAPH_DERIVED/...)
  independent of `ScenarioMode`; graph shots are GRAPH_DERIVED, not fake canonical events.
- **L — real event identity + state:** events carry immutable
  `sim://scenario/run/i/event/j` ids + pre/post state; persisted + threaded into shots.
- **M — renderer profile:** version/model from a `RendererProfile` in config (LTX-2.5),
  not hardcoded; `RendererManifest` has no stale defaults.
- **N — CI:** `.github/workflows/ci.yml` (offline pytest + compileall).
- **Persistence wired:** DuckStore is durable (file-backed); ingest writes the evidence
  chain, `run` writes sim results + canonical events, `publish` writes episodes to R2
  AND the durable store.

## Tests (31, offline, fast)
`test_truth` · `test_montecarlo` · `test_historical` · `test_channels` ·
`test_media` · `test_assets` · `test_evidence`. All offline; channel tests use
offline adapters + a durable-store persistence check. Run with
`.venv/bin/python -m pytest tests/`.

## Docs
`docs/INDEX.md` is the map. See README at repo root for quickstart + CLI.

## Docs
`docs/INDEX.md` is the map. `docs/MVP.md` is the 32-phase MVP guide (imported from R2
`mdev`) — the next target: force one evidence-backed world through to a finished film.
`docs/MVP.md` commit sequence 01–36 lists the exact build order.

## MVP guide progress (docs/MVP.md)
- **Commit 01 — WorldSnapshot + stable digest: DONE.** `reconstruction/world.py`.
- **Commits 02–11: DONE.**
  - 02 reconstruction versioning/lifecycle (`reconstruction/versioning.py`, `taxon.py`,
    `environment.py`): DRAFT→REVIEWED→APPROVED; **LTX only gets APPROVED**; registry auto-supersedes.
  - 03 ReferencePack constrained portfolio selection (`assets/reference_pack.py`): role+view
    diversity, not top-N.
  - 04+08 VisualReconstructionSpec + EnvironmentVisualSpec (`assets/visual_spec.py`) with
    certainty tiers (CONSTRAINED/INFERRED/OPEN/SPECULATIVE).
  - 05-06 provider-neutral `ReconstructionImageBackend` + offline `LocalSpecBackend`.
  - 07 ReconstructionVisualQA (`assets/qa.py`): P0/P1/P2 classification.
  - 09 immutable CanonicalAsset registry + content hashes (`assets/canonical.py`).
  - 10 StoreManager persistence (DuckDB always + optional Postgres + R2) wired into publish.
  - 11 immutable ScenarioManifest + digest (`scenarios/manifest.py`).
- **Commits 12–20: DONE.**
  - 12-13 SimulationModel classes (`simulations/model.py`): GAME_PROXY/MECHANISTIC/
    STATISTICAL/GRAPH/NO_SIM; full SimulationRun with run/scenario/model/seed/events/outcome.
  - 14 claim-aware StoryBeat (`story/beats.py`): beats can never blur evidence vs prediction.
  - 15 executable EpisodeSpec (`story/episode.py`): the only input to the media compiler.
  - 16 deterministic ScientificRenderer (`media/scientific_renderer.py`): SVG timelines,
    range charts, occurrence plots, confidence diagrams, evidence cards.
  - 17 ShotSpec v2 (`media/shot_spec2.py`): basis binds assertions/reconstructions/events.
  - 18 ControlPlanner + 19 control-frame compositor (`media/control.py`): first/last plates.
  - 20 renderers (`media/renderer.py`): LTX25ApiRenderer contract + OfflineRenderer.
- Next: 21+ (QA layers, Retake loop, narration compilation, EpisodeAssembler,
  `monstah produce`).

## Tests (53, offline, fast)
`test_truth` · `test_montecarlo` · `test_historical` · `test_channels` · `test_media` ·
`test_assets` · `test_evidence` · `test_world` · `test_mvp`.
