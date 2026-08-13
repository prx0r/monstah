# Onboarding — for a new agent picking up Monstah

Read this first. Then `docs/INDEX.md` → `docs/AUDIT.md` → `docs/ARCHITECTURE.md`.

## What this is
A machine-readable world-reconstruction engine → YouTube channel identities. It
turns public evidence (PBDB, Macrostrat, OBIS, GBIF, GloBI, OpenTree, OpenAlex,
Open5e) into historically-accurate, graph-derived battles + reconstructions, then
renders them (LTX is a replaceable renderer downstream of canonical state).

**Core rule: the content layer never decides what is true.** Every value is
evidence-constrained and layer-tagged (`core/truth.py`).

## Quickstart (5 min)
```bash
python -m venv .venv && .venv/bin/pip install -e .
.venv/bin/python -m pytest tests/ -q        # 59 offline tests
.venv/bin/monstah produce prehistoric --out out/produce   # full vertical slice
.venv/bin/monstah channel deep-blue                       # a themed channel
.venv/bin/monstah matchup tyrannosaurus-rex triceratops   # Monte Carlo duel
```

## Architecture in one line
```
EVIDENCE → WORLD → RECONSTRUCTION → SCENARIO → SIMULATION(d20) → EVENTS
  → STORY → SHOT(ShotSpec) → RENDER → QA → ASSEMBLE → EPISODE
```
A **channel** = `EvidenceAdapter` + `TruthPolicy` + `SimulationPolicy` +
`NarrativePolicy` + `MediaPolicy` over one engine. `channels/<theme>/` is one
folder per theme (see each `DATAFLOW.md`).

## Where things live
```
src/monstah/          the engine
  core/               entities, truth firewall, identity crosswalk
  evidence/           Source/Claim/Assertion/Reconstruction + builder
  ingest/             API clients
  discovery/          scenario discovery + historical overlap
  simulations/        d20 engine, replayable Monte Carlo, SimulationModel
  reconstruction/     WorldSnapshot, version lifecycle
  assets/             reference packs, visual specs, image backends, QA, canonical
  scenarios/          ScenarioManifest
  story/              claim-aware beats, narration (executable EpisodeSpec = next-gen)
  narrative/          significance, story compiler, novelty
  media/              LTX ShotSpec, control, deterministic graphics, renderers, QA,
                      assembler, image providers, R2
  data/               DuckDB (always) + Postgres (optional)
  production/         produce_episode, ProductionRun, EpisodeManifest, StoreManager
channels/             theme packages (one folder each, with DATAFLOW.md)
docs/                 this doc + INDEX + AUDIT + ARCHITECTURE + ...
media/ltx/            vendored LTX production pack
sql/postgres.sql      PostGIS schema
tests/                offline tests (pytest)
```

## The truth rules
1. **Firewall:** EvidenceTrait ≠ ReconstructionParameter ≠ SimulationParameter ≠
   GameProxyParameter ≠ NarrativeProjection. Open5e stats are labeled `GAME_PROXY`,
   never evidence.
2. **Historical Mode is strict:** temporal + geographic + environment overlap from real
   data; no bypass. Lab Mode is labeled `COUNTERFACTUAL`.
3. **LTX only receives an APPROVED reconstruction** (`reconstruction/versioning.py`).
4. **Runs are replayable:** every Monte Carlo run = `(master_seed, run_index)`.
5. **Events are immutable:** `sim://scenario/run/i/event/j` + pre/post state.

## How to run the main path
`monstah produce <channel> --world <id> --out <dir>` runs the full vertical and writes
`RUN.json` (resumable) + `episode-manifest.json` + `assembly.json`. Offline by default
(`OfflineRenderer`, deterministic). Live video needs `LTX_API_KEY`; Postgres needs
`POSTGRES_DSN`; ffmpeg assembly needs `ffmpeg`.

## How to add a channel
1. `mkdir channels/<theme>/`
2. `channels/<theme>/channel.py`: an `EvidenceAdapter` + a `<theme>_channel()` builder
   (see `channels/prehistoric/channel.py`).
3. `channels/<theme>/__init__.py`: `from .channel import <theme>_channel`
4. `channels/<theme>/DATAFLOW.md`: the source→adapter→policy→output dataflow.
5. Register in `channels/__init__.py` `_CHANNELS`.
6. Offline support: every adapter takes `offline=True`.

## How to add a test
Tests live in `tests/`, must be **offline** (use `offline=True` adapters; no network),
fast, and deterministic. Run `.venv/bin/python -m pytest tests/`.

## Conventions
- Type everything with pydantic dataclasses; values are layer-tagged via `core/truth`.
- Never hardcode renderer version in domain code — use `RendererProfile` (config).
- License is asset identity; unknown license → REJECT (`media/asset.py`).
- Every module has a docstring explaining its epistemic contract.

## Known gaps / next steps
See `docs/AUDIT.md` "Wiring gaps" and `docs/MVP.md` commit ladder (01–20 done; 21–36
partly — QA/narration/assembler/produce done, next: wire executable EpisodeSpec into the
pipeline, then first real Hell Creek film).
