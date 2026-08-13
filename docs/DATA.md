# Data Layer — availability, mass import, graph structures

## Data availability (verified live, no auth)

| API | Endpoints | Auth | Scale | Mass-import mode |
|---|---|---|---|---|
| **PBDB** | `taxa/single`, `occs/list`, `taxa/list`, `occs/diversity`, `occs/geosum` | none | large | yes — paginate `occs/list` by id; prefer `diversity`/`geosum` summaries for scale |
| **Macrostrat** | `/columns`, `/units/lookup`, `/defs/lithologies`, `/paleogeography` | none | ~10k cols / ~100k units | yes — full dataset fits in memory; bulk pull units/columns |
| **GBIF** | `/occurrence/search`, `/species/search` | none (key raises limits) | ~3.9B occ | yes — paginate 300/page, offset≤300k; bulk download API for full scale |
| **OBIS** | `/occurrence`, `/taxon`, `/statistics`, `/checklist` | none | 100M+ marine | yes — API paginate + GeoParquet/TSV bulk exports |
| **GloBI** | `/interaction`, `/datasets`, `/references` | none | large | **yes — download interactions.parquet/TSV → DuckDB** (recommended over per-call) |
| **OpenTree** | `/tnrs/match_names`, `/taxonomy/taxon_info`, `/tree_of_life/mrca`, `/subtree`, `/induced_subtree` | none | tree | yes — name-resolution for crosswalking |
| **OpenAlex** | `/works` (search/filter/group) | optional `mailto` | ~324M works | yes — cursor pagination; `mailto=` raises pool |
| **Open5e** | `/monsters/` | none | 3,207 statblocks | **yes — pull all statblocks once, cache locally** (game-proxy corpus) |
| **EOL TraitBank** | `/pages`, `/data` | **key now required** | — | blocked without key — route traits via OpenAlex/OpenTree |

## Mass import strategy (5GB/4-core)

- **Static corpora (pull once, cache):** Open5e all 3,207 statblocks; Macrostrat units/columns; GloBI bulk parquet/TSV.
- **Paginated APIs (bounded pulls):** PBDB (by taxon/interval, not global); GBIF/OBIS (per region/depth, not global); OpenAlex (per topic).
- **Analytical layer:** load big corpora into **DuckDB + Parquet** (GloBI edges, occurrences, sim outputs) — never into RAM. Postgres+PostGIS is the canonical truth store.
- **Crosswalk:** OpenTree TNRS is the name resolver that joins PBDB/GBIF/OBIS/GloBI/WoRMS names to one identity.

## Graph structure channels populate (shared schema)

```
ENTITY ──taxa/agents/planets──┐
  ├─ external_ids (crosswalk: pbdb|gbif|ott|eol|worms|wikidata|macrostrat|obis|open5e)
  ├─ occurrences (geom Point 4326, min/max_ma, depth_m, formation, collection)
  ├─ trait_assertions (layer-tagged: EVIDENCE|RECONSTRUCTION|SIMULATION|GAME_PROXY)
  └─ relation_assertions (eats | host of | parasite of | pollinates | ancestor of | ...)

ENVIRONMENT ──paleoenvironment | ocean | phylogeny──┐
  └─ time_intervals, environments (constraints JSONB)

TIME ── time_intervals (min_ma/max_ma)  ·  locations  ·  paleolocations

EVIDENCE ── sources ── claims ── assertions ── reconstructions (versioned, supersedes)

SCENARIOS ── scenario_templates ── scenarios ── simulation_runs ── events
STORY ── story_candidates ── stories ── narrative_claims
MEDIA ── assets ── shots ── episodes ── content_history ── performance_metrics
```

**Key rule:** `EvidenceTrait != ReconstructionParameter != SimulationParameter !=
GameProxyParameter != NarrativeProjection` — values are layer-tagged (see `core/truth`)
so combat/game numbers can never become scientific reconstruction state.
