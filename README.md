# Monstah

**A machine-readable world reconstruction + simulation engine that turns evidence
into historically-accurate, graph-derived battles and media.**

Core idea — one engine, many data APIs → reusable assets → battles → footage:

```
EVIDENCE → WORLD MODEL → RECONSTRUCTION → SCENARIO → SIMULATION(d20)
  → EVENTS → STORY → SHOT(ShotSpec) → LTX → EPISODE
```

The content layer never decides what is true. Every factual value is
evidence-constrained and layer-tagged (see `docs/ARCHITECTURE.md`).

## Quickstart

```bash
python -m venv .venv && .venv/bin/pip install -e .
.venv/bin/monstah channel prehistoric            # online, real statblocks
.venv/bin/monstah simulate prehistoric --offline # full stack, no LTX/network
.venv/bin/monstah matchup tyrannosaurus-rex triceratops   # Monte Carlo duel
.venv/bin/monstah channel deep-blue              # OBIS-driven marine
.venv/bin/python -m pytest tests/                # offline, fast
```

## CLI

| Command | What it does |
|---|---|
| `channel <name>` | run a theme end-to-end (ingest→discover→battle→story→shots) |
| `simulate <name>` | full offline stack simulation, writes episode bundles |
| `matchup a b` | Monte Carlo duel from two Open5e statblocks |
| `scenarios` | scenario discovery over a corpus |

## Channels (live)

`prehistoric` · `ancient-oceans` · `deep-blue` · `living-planet` · `tree-of-life`

## Repository layout

```
src/monstah/
├── core/        entities, truth-layer firewall, identity crosswalk
├── evidence/    Source/Claim/Assertion/Reconstruction + builder
├── ingest/      API clients: PBDB, Macrostrat, GBIF, OBIS, GloBI, OpenTree, OpenAlex, Open5e, EOL
├── discovery/   scenario discovery, historical overlap, novelty
├── simulations/ d20 battle engine, Monte Carlo (replayable), esper ECS
├── narrative/   significance, story compiler, novelty
├── media/       LTX ShotSpec, canonical assets + image providers, R2 storage
├── data/        DuckDB analytical + Postgres canonical stores
├── channels/    themes = adapter + policies over the engine
└── domains/     paleo seed corpus
docs/            thesis, architecture, data, channels, media, progress
sql/             PostGIS schema
media/ltx/       vendored LTX production pack
```

## Docs
Start at [`docs/INDEX.md`](docs/INDEX.md). Highlights: `ARCHITECTURE.md`,
`PROGRESS.md`, `CHANNELS.md` (10-channel spec + strength), `DATA.md`,
`LTX_USAGE.md`, `ASSETS.md`, `REVIEW_NOTES.md`.

## Design constraints
- **Truth firewall:** EvidenceTrait ≠ ReconstructionParameter ≠ SimulationParameter ≠
  GameProxyParameter ≠ NarrativeProjection (`core/truth`). Open5e stats are labeled
  game-proxy, never evidence.
- **Historical Mode is strict:** temporal + geographic + environment overlap from real
  data; Lab Mode is labeled COUNTERFACTUAL.
- **Reproducible:** every Monte Carlo run = `(master_seed, run_index)`.
- **Hardware:** CPU-only, 5GB/4-core; vectorized Monte Carlo (10k runs < 1s), DuckDB+Parquet
  for the analytical layer, remote/streamed ingest.
