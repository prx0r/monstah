# Dataflow — Prehistoric (Titans of Deep Time)

Extinct-world reconstruction. Battle channel, strict historical mode.

```
SOURCES
  PBDB          identity, age range, occurrences
  Macrostrat    paleoenvironment / rock units
  Open5e        statblocks -> GAME_PROXY combat stats (never evidence)
  OpenAlex      literature grounding
    ↓
ADAPTER  PrehistoricAdapter
  - load_taxa(): paleo seed corpus, evidence facts + labeled game-proxy
  - environment_for_candidate(): binds a real paleoenvironment by era
    ↓
POLICIES
  TruthPolicy:        HISTORICAL (strict temporal+geo+env; no bypass)
  SimulationPolicy:   d20 combat (open5e statblocks -> Combatant)
  DiscoveryPolicy:    pairwise overlap + novelty scoring
  NarrativePolicy:    reconstruct / matchup framing
  MediaPolicy:        shot graph from real simulation event log
    ↓
OUTPUT
  Monte Carlo outcome distribution (replayable, master_seed/run_index)
  -> story (provenance-bearing NarrativeClaims)
  -> LTX ShotSpecs (canonicality from mode+basis; I2V refs via CanonicalAssetResolver)
  -> R2 bundle + durable DuckDB evidence/sim/events/episodes
```

## Notes
- Extinct => `CanonicalAssetResolver` NEVER feeds raw source refs to LTX; only an
  approved canonical reconstruction is eligible.
- Game-proxy (AC/HP/attack/damage) stays in `facts.game_proxy`, never evidence.
- Historical validity uses real regions; unknown region = validity gap, not a pass.
