# Dataflow — Ancient Oceans

Marine prehistory. Battle channel, strict historical mode.

```
SOURCES
  PBDB          marine taxa, age range
  Macrostrat    paleogeography / marine paleoenvironment
  Open5e        statblocks -> GAME_PROXY combat stats
    ↓
ADAPTER  AncientOceansAdapter  (reuses prehistoric seed, marine filter)
  - load_taxa(): paleo marine taxa only
  - environment_for_candidate(): oceanic paleoenvironment by era
    ↓
POLICIES
  TruthPolicy:      HISTORICAL (strict; marine env required)
  SimulationPolicy: d20 combat
  DiscoveryPolicy:  overlap + novelty
    ↓
OUTPUT
  Monte Carlo outcomes -> story -> LTX ShotSpecs -> R2 + durable store
```

## Notes
- Reuses the same engine + statblocks as Prehistoric; only the adapter filter
  and environment differ (cheapest additional channel).
- Extinct => canonical-only references to LTX.
