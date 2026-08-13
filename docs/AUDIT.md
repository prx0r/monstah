# Audit — live vs legacy, wiring, and gaps

Date: session end. 59 tests pass offline. Full audit of every module.

## Verdict
The MVP vertical slice is **live and working end-to-end**:
`monstah produce prehistoric` runs ingest → world → scenario → simulate → story →
shots → render → QA → assemble → publish, resumable by manifest. Everything below
is real (no stubs); a few modules are legacy/unwired and are flagged explicitly.

---

## LIVE — wired into the running pipeline

| Concern | Module(s) | Role |
|---|---|---|
| **Produce harness** | `production/produce.py`, `run.py`, `manifest.py`, `persistence.py` | one-command vertical + resumable ProductionRun + EpisodeManifest + StoreManager |
| **Channels (root pkg)** | `channels/` (`base.py`, `prehistoric/`, `ancient_oceans/`, `deep_blue/`, `living_planet/`, `tree_of_life/`) | theme = adapter + policies; each has `DATAFLOW.md` |
| **Engine core** | `core/truth.py`, `core/models.py`, `core/identity.py` | layer firewall, substrate entities, crosswalk |
| **Evidence chain** | `evidence/models.py`, `evidence/builder.py` | Source→Claim→Assertion→Reconstruction, persisted |
| **Ingest** | `ingest/` (pbdb, macrostrat, gbif, obis, globi, opentree, openalex, open5e) | API clients (all live except EOL) |
| **Discovery** | `discovery/scenario_generator.py`, `historical_overlap.py` | scenario discovery + strict historical validity |
| **Simulation** | `simulations/d20.py`, `montecarlo.py`, `model.py` | d20 engine, replayable MC, SimulationModel classes |
| **Narrative** | `narrative/significance.py`, `story.py`, `novelty.py` | significance, story compiler, novelty history |
| **Reconstruction** | `reconstruction/world.py`, `versioning.py`, `taxon.py` | WorldSnapshot + digest, version lifecycle |
| **Assets** | `assets/reference_pack.py`, `visual_spec.py`, `image_backend.py`, `qa.py`, `canonical.py` | reference packs, specs, backends, visual QA, canonical registry |
| **Scenarios** | `scenarios/manifest.py` | immutable ScenarioManifest + digest |
| **Story (new)** | `story/beats.py`, `narration.py` | claim-aware beats, narration-from-claims |
| **Media** | `media/ltx.py`, `shots.py`, `shot_spec2.py`, `control.py`, `scientific_renderer.py`, `renderer.py`, `qa.py`, `assembler.py`, `providers.py`, `asset.py`, `storage.py` | LTX ShotSpec, control, deterministic graphics, renderers, QA, assembler, image providers, R2 |
| **Data** | `data/duck.py`, `data/postgres.py` | DuckDB (always) + Postgres (optional) |
| **CLI** | `cli.py` | produce, resume, channel, simulate, snapshot, matchup, ingest, run, scenarios |
| **Domains seed** | `domains/paleo/seed.py` | 100-taxon / 20-environment corpus (used by channels) |

---

## LEGACY / NOT WIRED — real code, but not on the active path

| Module | Status | Note |
|---|---|---|
| `simulations/ecs_battle.py` | **alternative, not wired** | esper ECS battle engine; superseded by d20 for the pipeline. Kept as an alternative; not used by `produce`. |
| `ingest/eol.py` | **degraded** | EOL now requires an API key (403 without it); exported but unusable. Traits route via OpenAlex/OpenTree instead. |
| `media/storage.py::AssetStore` | **unused** | R2 layout helper (source/entities/environments); not called anywhere. R2Store is the live one. |
| `domains/paleo/loader.py::PaleoLoader` | **legacy path** | live PBDB/Macrostrat loader used only by `monstah ingest` CLI; has a hacky diet heuristic. Channels use `seed.py` instead. |
| `story/episode.py::EpisodeSpec` | **not yet wired** | the executable EpisodeSpec (MVP Phase 15). The pipeline still emits `narrative/story.EpisodeSpec`; the executable one is the future "only input to the media compiler." |
| `core/models.py` substrate | **partly superseded** | `core.models.SimulationRun`/`History` overlap with `simulations/model.SimulationRun` + `production`. Kept as generic substrate. |

## Name collisions to be aware of
- **`SimulationRun`** exists in both `core/models.py` and `simulations/model.py` (the latter is the live MVP one).
- **`EpisodeSpec`** exists in both `narrative/story.py` (live, emitted by pipeline) and `story/episode.py` (executable, next-gen, not wired).

## Wiring gaps (known, by design)
- **Postgres** canonical store is optional (needs `POSTGRES_DSN`); DuckDB + R2 are the default persistence.
- **LTX-2.5 API** renderer is a contract + `OfflineRenderer` (deterministic); live video needs an `LTX_API_KEY` + wiring.
- **Film assembly is honest:** `EpisodeAssembler` only runs ffmpeg on *real* media inputs and sets `produced=True` + writes `master.mp4` only when it can. The offline MVP produces **no film** — the run honestly stays at `QA`/`RENDERING` (draft render plan) and never falsely claims `ASSEMBLED`/`PUBLISHED`. `resume` short-circuits terminal runs; mid-run resumption that avoids re-running completed stages needs persisted intermediate outputs (documented gap).
- **Vision QA** (VisualIdentityQA) is a deterministic skeleton; a real vision model can plug in.
- **Executable EpisodeSpec** (`story/episode.py`) is not yet the pipeline's output.

## CLI commands
`produce` (main MVP path) · `resume` · `channel` · `simulate` · `snapshot` · `matchup` ·
`ingest` · `run` (legacy manual path) · `scenarios`

## Security
`.env` (gitignored) holds R2 credentials. No secrets are committed. CI runs offline
pytest + compileall (`.github/workflows/ci.yml`).

## Test inventory (59, all offline)
`test_truth` · `test_montecarlo` · `test_historical` · `test_channels` · `test_media` ·
`test_assets` · `test_evidence` · `test_world` · `test_mvp` · `test_mvp2` · `test_mvp3`
