# Dataflow — Living Planet (Food Web Wars)

Modern ecology. **Non-combat** graph-story channel.

```
SOURCES
  GloBI         directed interaction edges (eats/host/parasite/pollinates)
  (GBIF, OpenTree)  optional
    ↓
ADAPTER  LivingPlanetAdapter
  - load_taxa(): taxa with real GloBI interaction lookups
    ↓
POLICIES
  TruthPolicy:      HISTORICAL (co-occurring species)
  SimulationPolicy: NONE -> produces a GRAPH_STORY (no battle engine)
  NarrativePolicy:  food-web / ecosystem narrative
  MediaPolicy:      graph-derived shots (basis = GRAPH_DERIVED, NOT canonical event)
    ↓
OUTPUT
  GloBI interaction story -> LTX ShotSpecs (RECONSTRUCTION/GRAPH_DERIVED) -> R2 + store
```

## Notes
- Proves the channel abstraction is not battle-specific.
- Graph shots carry `basis=GRAPH_DERIVED` and `event_ids=[]`; they are NOT labeled
  as canonical simulation events (ScenarioMode != ShotBasis).
