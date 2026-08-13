# Dataflow — Extinction

Mass-extinction / ecosystem-collapse timeline stories. Non-combat editorial policy
over the same PBDB seed as Prehistoric.

```
SOURCES  PBDB taxa + age ranges (same substrate as prehistoric)
  ↓
ADAPTER  ExtinctionAdapter — taxa straddling the event boundary
  ↓
POLICIES TruthPolicy: historical · SimulationPolicy: NONE (graph/timeline story)
  ↓
OUTPUT   BEFORE → EVENT → AFTER → SURVIVORS story (StoryBeats) → LTX ShotSpecs (GRAPH_DERIVED)
```

Choose an event: `extinction_channel(event="K-Pg extinction" | "Permian-Triassic" | "End-Devonian")`.
