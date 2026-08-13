# Progress

Status: **evidence-constrained world engine working end-to-end — 5 live channels, the
MVP vertical slice (`monstah produce`) running, 59 offline tests, full audit + handover docs.**

## Handover (read first)
- `docs/ONBOARDING.md` — new-agent entry point.
- `docs/AUDIT.md` — LIVE vs LEGACY, wiring gaps, name collisions, security.
- `docs/INDEX.md` — master index + CLI quick reference.

## What is built and verified working
- **Engine core**: type firewall (`core/truth`), substrate entities (`core/models`),
  identity crosswalk (`core/identity`).
- **Evidence chain**: Source→Claim→Assertion→Reconstruction persisted with real
  immutable IDs (`evidence/`), built per taxon during ingest.
- **Ingest**: PBDB, Macrostrat, GBIF, OBIS, GloBI, OpenTree, OpenAlex, Open5e all live
  (EOL degraded — needs key).
- **Simulation**: d20 engine, replayable Monte Carlo `(master_seed, run_index)`,
  SimulationModel classes (honest GAME_PROXY label).
- **Discovery/narrative**: scenario discovery, strict historical overlap, novelty
  history, significance, story compiler.
- **Reconstruction**: WorldSnapshot + stable digest, version lifecycle
  (DRAFT→REVIEWED→APPROVED; LTX only gets APPROVED).
- **Assets**: reference packs (portfolio selection), visual specs with certainty tiers,
  image backends, visual QA (P0/P1/P2), canonical asset registry.
- **Media**: LTX ShotSpec (canonicality from mode+basis), ShotSpec v2, ControlPlanner +
  control-frame compositor, deterministic ScientificRenderer (SVG), renderers
  (LTX25 contract + OfflineRenderer), 4-layer QA, EpisodeAssembler, image providers
  (GBIF/iNat/Wikimedia/BHL), R2 storage.
- **Production**: `produce_episode` one-command vertical, resumable `ProductionRun`,
  `EpisodeManifest` (fully backward-traceable), StoreManager persistence
  (DuckDB always + optional Postgres + R2).
- **Channels (root pkg)**: prehistoric, ancient-oceans, deep-blue, living-planet,
  tree-of-life — each a folder with `DATAFLOW.md`.
- **CLI**: `produce`, `resume`, `channel`, `simulate`, `snapshot`, `matchup`, `ingest`,
  `run`, `scenarios`.

## The MVP vertical slice (the main path)
`monstah produce prehistoric --world hell-creek --out out/produce` runs:
ingest → world snapshot → scenario manifest → battle → story → shots → render →
4-layer QA → assemble → publish, resumable via `RUN.json`, emitting
`episode-manifest.json` + `assembly.json`. Offline by default (deterministic renderer
+ graphics); live LTX/ffmpeg/Postgres are optional and key/DSN-gated.

## Integrity hardening (peer-review G–N, done)
Monotonic firewall (EVIDENCE→RECONSTRUCTION→SIMULATION only), persisted evidence chain
with real IDs, canonical-vs-source asset separation, ShotBasis independent of
ScenarioMode, immutable event IDs + pre/post state, renderer profiles (out of domain),
CI (offline pytest + compileall), real DuckDB persistence. See `docs/REVIEW_NOTES.md`.

## Legacy / not wired (see `docs/AUDIT.md`)
`simulations/ecs_battle.py` (alternative engine, not wired) · `ingest/eol.py` (403,
needs key) · `media/storage.py::AssetStore` (unused) · `domains/paleo/loader.py`
(legacy `ingest` path) · `story/episode.py::EpisodeSpec` (executable, next-gen, not yet
the pipeline output). Two `SimulationRun` and two `EpisodeSpec` symbols exist across
modules — see AUDIT.

## MVP ladder (docs/MVP.md)
- 01 WorldSnapshot + digest — done
- 02–11 versioning, reference packs, visual specs, backends, QA, canonical assets,
  persistence, ScenarioManifest — done
- 12–20 sim models, story beats, episode spec, scientific renderer, ShotSpec v2,
  control, renderers — done
- 21–32 QA layers, uncertainty constraints, narration, assembler, EpisodeManifest,
  ProductionRun, `produce` — done
- Remaining: wire the executable EpisodeSpec (`story/episode.py`) into the pipeline,
  then produce the first real Hell Creek film (needs live LTX/ffmpeg + approved assets).

## Tests (59, offline, fast)
`test_truth` · `test_montecarlo` · `test_historical` · `test_channels` · `test_media` ·
`test_assets` · `test_evidence` · `test_world` · `test_mvp` · `test_mvp2` · `test_mvp3`.

## Trending-data niche analysis
See `docs/CHANNELS.md`. Blue ocean: Prehistoric (9.4M avg) + Ancient Oceans (10.5M avg,
lowest supply). Matchups = Shorts discovery. Weak: Evolution, generic wildlife.
