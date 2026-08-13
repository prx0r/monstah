# Dataflow — Tree of Life

Evolution / phylogeny. **Non-combat** graph-story channel.

```
SOURCES
  OpenTree      TNRS name resolution, MRCA, subtrees (synthesized phylogeny)
  (PBDB, Open5e traits)  optional
    ↓
ADAPTER  TreeOfLifeAdapter
  - load_taxa(): resolve names to OTT ids (evidence)
    ↓
POLICIES
  TruthPolicy:      HISTORICAL
  SimulationPolicy: NONE -> GRAPH_STORY (phylogenetic narrative)
  NarrativePolicy:  common-ancestor / lineage framing
  MediaPolicy:      graph-derived shots (basis = GRAPH_DERIVED)
    ↓
OUTPUT
  MRCA/lineage story -> LTX ShotSpecs (GRAPH_DERIVED) -> R2 + store
```

## Notes
- Content = "common ancestor of X and Y", lineage transitions.
- Graph shots are GRAPH_DERIVED, never fake canonical events.
- Weak trending niche (evolution 208k avg) — keep as support channel, not lead.
