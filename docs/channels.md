# Channel Spec — 5 YouTube Identities

Product core: **distinct YouTube channel identities, each running historically-accurate,
graph-derived battles on reusable assets, through one shared engine.**

Every channel uses the same chain:

    ENTITY -> ENVIRONMENT -> RELATION -> SCENARIO -> SIMULATION(d20) -> EVENT -> STORY -> SHOT

The channel only decides **which APIs populate the graph** and **what the engine is allowed to claim**.

Data-availability verified (no-auth, live):
PBDB ✓  Macrostrat ✓  GBIF ✓  OBIS ✓  GloBI ✓  OpenTree ✓  OpenAlex ✓  Open5e ✓
EOL ✗ (now requires an API key — swap to OpenAlex/OpenTree for traits/literature).

"Graph-derived fights" = the scenario is not hand-picked; it's a query result:
temporal+spatial overlap, a real GloBI interaction edge, or a phylogenetic relationship.

---

## Channel 1 — TITANS OF DEEP TIME  (prehistoric)
**Identity:** Flagship. "Who actually coexisted, and who wins?" Historical-first, Lab clearly labeled.
**Premise:** Battles reconstructed from real fossil evidence, never invented coexistence.

| Layer | Source | Endpoint | What it gives |
|---|---|---|---|
| Identity + occurrences | PBDB | `taxa/single`, `occs/list` | who lived, where, when (Ma) |
| Paleoenvironment | Macrostrat | `units/lookup`, `columns` | rock unit, lithology, depositional context |
| Combat stats | Open5e | `monsters/` | statblocks: AC, HP, attack_bonus, damage_dice |
| Literature grounding | OpenAlex | `works?title.search=` | citable papers + DOI |

**Historical accuracy:** `HistoricalScenario.valid` requires temporal overlap AND spatial overlap AND environment compatibility (from PBDB + Macrostrat). If any fails → invalid (no pretending). A "Lab" flag suspends only co-occurrence, never capabilities.
**Graph-derived fights:** `ScenarioDiscovery` enumerates taxon × taxon × overlap → e.g. "Deinonychus vs Tenontosaurus" only if PBDB says they overlapped in Cloverly.
**Reusable assets:** per-taxon reconstruction + statblock + visual. Hell Creek env + T.rex + Triceratops assets compound across every future episode.
**Episodes:** "A Day in Hell Creek, 66 Ma" · "Could a T. rex catch a Gallimimus?" · "Deinonychus pack vs Tenontosaurus" · "Megalodon vs Livyatan (Lab)".

---

## Channel 2 — DEEP BLUE  (modern ocean)
**Identity:** Data-led ocean mysteries. "Query the real ocean, reconstruct the ecosystem."
**Premise:** Battles driven by actual marine occurrence + interaction data, not speculation.

| Layer | Source | Endpoint | What it gives |
|---|---|---|---|
| Marine occurrences | OBIS | `/occurrence` (depth, geometry) | what lives at depth X, region Y |
| Predation edges | GloBI | `/interaction?interactionType=eats` | who actually hunts whom |
| Combat stats | Open5e | `monsters/` (Sperm Whale, Giant Squid, Great White) | statblocks |
| Biodiversity | GBIF | `/occurrence/search` | modern range + media |

**Graph-derived fights:** build the local ecosystem graph for a depth/region query, then GloBI edges pick predator→prey candidates; OBIS confirms they co-occur at that depth.
**Episodes:** "What hunts the giant squid?" · "The deepest recorded predator in this basin" · "Sperm whale vs giant squid: the real matchup" · "Who eats great white sharks?"
**Reusable assets:** marine statblocks + ocean environments + predation-edge library.

---

## Channel 3 — ANCIENT OCEANS  (marine prehistory)
**Identity:** "The deadliest oceans in Earth history."
**Premise:** Same engine as Titans, but marine: PBDB marine occurrences + Macrostrat paleogeography.

| Layer | Source | Endpoint | What it gives |
|---|---|---|---|
| Marine taxa/occurrences | PBDB | `occs/list` (env=marine) | marine fauna + age |
| Paleogeography/coastlines | Macrostrat | `paleogeography`, `units/lookup` | seaways, basins, paleoenvironment |
| Combat stats | Open5e | `monsters/` (Mosasaurus, Megalodon) | statblocks |
| Literature | OpenAlex | `works` | grounding |

**Graph-derived fights:** Western Interior Seaway fauna via PBDB; mosasaur predator structure via overlap.
**Episodes:** "A day in the Western Interior Seaway" · "What actually hunted ammonites?" · "When ichthyosaurs ruled" · "The Devonian reef killers".
**Reusable assets:** seaway environment + marine reptile statblocks.

---

## Channel 4 — FOOD WEB WARS / LIVING PLANET  (modern ecology)
**Identity:** "Reconstruct the actual food web, then break it."
**Premise:** Directed ecological edges (eats/host/parasite/pollinator) drive the graph — not a 1v1 arena.

| Layer | Source | Endpoint | What it gives |
|---|---|---|---|
| Interaction edges | GloBI | `/interaction` + bulk parquet/TSV dump | directed trophic/parasite/mutualist edges |
| Taxonomy resolution | OpenTree | `/taxonomy/taxon_info`, `/tree_of_life` | normalize messy names into one tree |
| Occurrence/range | GBIF | `/occurrence/search` | where the web actually exists |
| Combat stats | Open5e | `monsters/` | statblocks |

**Graph-derived fights:** pick a hub species, expand its GloBI neighborhood → predator/prey/competitor candidates; keystone-loss and cascade scenarios.
**Episodes:** "Who actually eats great white sharks?" · "The Yellowstone food web" · "What happens when wolves disappear?" · "The hidden parasite network of a forest".
**Reusable assets:** interaction-edge library (bulk-loadable into DuckDB) + food-web graph renderings.

---

## Channel 5 — TREE OF LIFE  (evolution)
**Identity:** "Every step between X and Y."
**Premise:** Battles/queries are *phylogenetic*: common ancestor, nearest living relative, trait transitions.

| Layer | Source | Endpoint | What it gives |
|---|---|---|---|
| Phylogeny | OpenTree | `/tnrs/match_names`, `/tree_of_life/mrca`, `/induced_subtree`, `/subtree` | common ancestors, clades, lineage tree |
| Traits/capabilities | Open5e | `monsters/` | body-plan capability vectors |
| Fossil timeline | PBDB | `occs/list`, `taxa/list` | when transitions happened |
| Literature | OpenAlex | `works` | grounding |

**Graph-derived fights:** "common ancestor(T), nearest living relative of an extinct taxon", "marine→terrestrial→marine transition" — the *lineage* is the matchup.
**Episodes:** "How whales returned to the sea" · "The animal that lost its legs" · "Nearest living relative of T. rex" · "Why mammals got huge after the dinosaurs".
**Reusable assets:** phylogeny subtree snapshots + lineage-transition records.

---

## Build order & hardware note (no GPU / 5GB / 4 cores)
1. **Titans of Deep Time** (flagship — already scaffolded as `prehistoric` channel)
2. **Deep Blue** (already scaffolded as `deep-blue` channel)
3. **Ancient Oceans** (reuse prehistoric adapter, marine filter — cheapest)
4. **Food Web Wars** (needs GloBI bulk parquet → DuckDB; new adapter)
5. **Tree of Life** (needs OpenTree mrca/subtree adapter)

All CPU-only; vectorized Monte Carlo (~10k runs < 1s); DuckDB+Parquet for the bulk GloBI/occurrence joins; R2 for canonical assets.

---

## Shared substrate (reuse compounds)
- d20 battle engine (Open5e statblocks) — every channel
- ScenarioDiscovery + historical-overlap validator — channels 1,2,3
- GloBI interaction-edge library — channels 2,4
- OpenTree name-resolution + phylogeny — channels 4,5
- Story compiler + shot graph + R2 asset store — every channel

The moat is the **compounding asset library**: once a taxon/environment/interaction is built and versioned, every future episode in every channel reuses it.
