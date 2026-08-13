# Monstah Docs

A machine-readable world reconstruction + simulation engine → YouTube channel identities.
Core: **one engine, many APIs → reusable assets → historically-accurate graph-derived
battles → LTX footage.** Truth is evidence-constrained; the content layer never decides
what is true.

## Map

| Doc | What it is |
|---|---|
| [`thesis.md`](thesis.md) | The original Evidence World Engine thesis (canonical guide, 2378 lines) |
| [`DATA.md`](DATA.md) | Data availability per API, mass-import strategy, graph schema |
| [`CHANNELS.md`](CHANNELS.md) | **10-channel spec** with trending-data justification + strength scores |
| [`LTX_USAGE.md`](LTX_USAGE.md) | How we use LTX (I2V-first, ShotSpec as execution plan, Retake, Reframe) |
| [`ASSETS.md`](ASSETS.md) | Canonical image/asset system: providers, license policy, versioned reconstructions |
| [`REVIEW_NOTES.md`](REVIEW_NOTES.md) | Peer-review findings + the truth-preservation fixes applied |
| `../media/ltx/` | Vendored LTX-2.3 production pack (prompting, control hierarchy, ComfyUI, hardware) |

## Architecture in one line

```
EVIDENCE → WORLD MODEL → RECONSTRUCTION → SCENARIO → SIMULATION(d20) → EVENTS
        → STORY → SHOT(ShotSpec) → LTX → EPISODE
```

Channel = EvidenceAdapter + ReconstructionPolicy + DiscoveryPolicy + TruthPolicy +
SimulationPolicy + NarrativePolicy + MediaPolicy, all over one engine.

## The two truth rules
1. **Firewall:** EvidenceTrait ≠ ReconstructionParameter ≠ SimulationParameter ≠
   GameProxyParameter ≠ NarrativeProjection (`core/truth`). Open5e stats are labeled
   game-proxy, never evidence.
2. **Historical Mode is strict:** temporal + geographic + environment overlap, from real
   data. Lab Mode suspends only co-occurrence and is labeled COUNTERFACTUAL.

## Channels (live)
```
monstah channel prehistoric   # Titans of Deep Time   (battle)
monstah channel ancient-oceans# Ancient Oceans        (battle)
monstah channel deep-blue     # Deep Blue             (battle, OBIS-driven)
monstah channel living-planet # Food Web Wars         (non-combat graph)
monstah channel tree-of-life  # Tree of Life          (non-combat phylogeny)

monstah simulate <channel> --offline   # full stack, no LTX/network
```
