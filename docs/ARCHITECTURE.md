# Architecture

## The core chain

```
EVIDENCE → WORLD MODEL → RECONSTRUCTION → SCENARIO → SIMULATION(d20)
  → EVENTS → STORY → SHOT(ShotSpec) → LTX → EPISODE
```

`EVENTS` are emitted by the selected simulation run (never fabricated). The
`ShotSpec` is an execution plan, not creative prose; LTX is a replaceable renderer
downstream of canonical state.

## Channel = a bundle of policies over one engine

```
CHANNEL
├── EvidenceAdapter      : which sources populate entities/environments
├── ReconstructionPolicy : evidence → simulation model (explicit promotion)
├── DiscoveryPolicy      : the database writes the editorial calendar
├── TruthPolicy          : strict historical vs counterfactual lab validity
├── SimulationPolicy     : taxon → combatant (game proxy), or None (non-combat)
├── NarrativePolicy      : what the episode is allowed to claim
└── MediaPolicy          : event → shot
```

Every theme runs the same chain; only the adapter + policies differ. Non-combat
channels (Living Planet, Tree of Life) take a graph/data path instead of the battle.

## The truth firewall (`core/truth.py`)

Values are pinned to one epistemic layer and can never be silently promoted:

```
EvidenceTrait ≠ ReconstructionParameter ≠ SimulationParameter
             ≠ GameProxyParameter ≠ NarrativeProjection
```

- `Taxon.traits` returns **scientific layers only** — game-proxy combat stats live in
  `facts.game_proxy` and are consumed only by the battle engine.
- Open5e/D&D statblocks are labeled `GAME_PROXY`, never reconstruction state.
- A `Reconstruction` is a versioned object of assertions (`R17` supersedes → `R18`).

## Two truth rules

1. **Historical Mode is strict.** A scenario is valid only if temporal + geographic +
   environment overlap all hold, from real evidence. No bypassing.
2. **Lab Mode suspends only co-occurrence** and is labeled `COUNTERFACTUAL`.

## Reproducible simulation

- Each Monte Carlo run = `(master_seed, run_index)` via `SeedSequence([master, i])`.
- Selected representative/surprising/median runs replay exactly.

## Data flow per channel

```
adapter.load_taxa()                 # evidence + labeled game-proxy facts
  → Channel.ingest()                # builds Source/Assertion/Reconstruction per taxon
  → DiscoveryPolicy.discover()      # scored scenario candidates (novelty-aware)
  → TruthPolicy.validate()          # strict historical validity
  → SimulationPolicy.resolve()      # combatants (or None → graph story)
  → run_monte_carlo()               # outcome distribution
  → significance → story            # narrative claims resolve to assertions
  → shots → LTX ShotSpec            # real event log; canonicality from truth layer
  → publish() → R2                  # canonical/channels/<theme>/...
```

## Module map

| Module | Responsibility |
|---|---|
| `core/models` | ENTITY / ENVIRONMENT / RELATION / SCENARIO / EVENT / STORY / SHOT / ASSET |
| `core/truth` | layer firewall + `TaxonFacts` |
| `core/identity` | identifier crosswalk (pbdb/gbif/ott/eol/worms/wikidata) |
| `evidence/` | Source/Claim/Assertion/Reconstruction + builder |
| `ingest/` | typed API clients (all work, EOL needs key) |
| `discovery/` | scenario discovery, historical overlap, novelty |
| `simulations/` | d20 engine, replayable Monte Carlo, esper ECS |
| `narrative/` | significance, story compiler, novelty history |
| `media/` | LTX ShotSpec, asset/image providers, R2 store |
| `data/` | DuckDB analytical + Postgres canonical stores |
| `channels/` | themes (prehistoric, ancient-oceans, deep-blue, living-planet, tree-of-life) |
| `domains/` | paleo seed corpus (100 taxa, 20 environments) |

## Storage split

- **PostgreSQL + PostGIS** = canonical truth (schema in `sql/postgres.sql`).
- **DuckDB + Parquet** = analytical joins / sim outputs (keeps 5GB box light).
- **R2** = canonical assets (sources, reconstructions, environments) + episode bundles.
