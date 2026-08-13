# Dataflow — Deep Blue

Modern ocean, OBIS-driven. Battle channel, historical mode.

```
SOURCES
  OBIS          marine occurrences (depth range derived from real records)
  Open5e        marine statblocks -> GAME_PROXY combat stats
  (GBIF, GloBI, TraitBank)  optional enrichment
    ↓
ADAPTER  DeepBlueAdapter
  - load_taxa(): real OBIS occurrences -> depth/region evidence
  - environment_for_candidate(): binds ocean env by observed max depth
    ↓
POLICIES
  TruthPolicy:        HISTORICAL (co-occurring marine taxa)
  SimulationPolicy:   d20 combat (marine statblocks)
  DiscoveryPolicy:    overlap + novelty
  MediaPolicy:        shot graph from real simulation events
    ↓
OUTPUT
  Monte Carlo outcomes -> story -> LTX ShotSpecs -> R2 + durable store
```

## Notes
- Depth range is EVIDENCE from OBIS (not hardcoded); Open5e only game-proxy.
- Extant world => explicit policy MAY allow observational photos as canonical
  morphology for I2V (rarely needed for extinct).
- Data/occurrence episodes can be graph stories without a battle (per thesis §50).
