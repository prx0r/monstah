# Peer Review Notes (commit 61d9ce1) + fixes applied

Source: peer-review pack `monstah-peer-review-61d9ce1.zip`. Core conclusion:
**keep the channel architecture** (channel = adapter + policies over the shared
engine). The flaw was that it proved shared plumbing more than truth-preserving
domain reuse. All findings below are fixed.

## P0 — fixed
- **Historical mode not wired.** `Channel.mode` was stored but never controlled
  discovery/execution. → Now `TruthPolicy.validate/allows` enforces mode; historical
  mode rejects invalid candidates; lab mode explicitly suspends co-occurrence only.
- **Geographic validity bypassed.** `run_candidate()` passed `spatial_shared=True`.
  → Removed the bypass; spatial overlap comes from real evidence regions; unknown
  region is a validity gap, not a pass.
- **Open5e/D&D stats contaminating evidence model.** AC/HP/attack/damage were written
  straight into `Taxon.traits`. → Type firewall (`core/truth.py`): game-proxy values
  live in a separate layer and can never be promoted into scientific state; every
  value is layer-tagged.
- **Deep Blue not OBIS-driven.** Hard-coded Open5e list, depth=3000, region=global.
  → `load_taxa` now queries real OBIS occurrences for depth/region; Open5e only as
  labeled game-proxy.
- **Selected Monte Carlo runs not reproducible.** Advanced generators reused; saved id
  used `SeedSequence.entropy`. → Every run is `(master_seed, run_index)` via
  `SeedSequence([master_seed, i])`; selected runs replay exactly.

## P1 — fixed
- `spatial_overlap()` wasn't spatial. → Now uses real regions; environment kept separate.
- Domain leakage: every shot compiled with `environment="PALEO"` incl. Deep Blue.
  → Adapters bind real environments (`environment_for_candidate`); no hardcoded domain.
- Channel abstraction battle-specific (`EvidenceAdapter.taxon_for_combat`). → Removed;
  `SimulationPolicy` is optional; added a **non-combat** graph/data path.

## P2 — fixed
- Event log to media was fabricated. → Shots now consume the **real canonical event log**
  emitted by the selected simulation run (`run_duel_events`), preserving
  SIMULATION → EVENT → STORY → SHOT.

## Recommended architecture (adopted)
```
CHANNEL
├── EvidenceAdapter
├── ReconstructionPolicy
├── DiscoveryPolicy
├── TruthPolicy
├── SimulationPolicy
├── NarrativePolicy
└── MediaPolicy
```
with the type firewall `EvidenceTrait != ReconstructionParameter !=
SimulationParameter != GameProxyParameter != NarrativeProjection`.

## Six-commit plan (done, landed as three commits)
A. truth policy + strict historical validity — **done**
B. separate evidence traits from sim proxy params — **done**
C. selected MC runs exactly replayable — **done**
D. remove PALEO/domain leakage, bind real environments — **done**
E. Deep Blue genuinely OBIS-driven — **done**
F. non-combat channel path + channel contract tests — **done**

Also added since: evidence builder (Source/Claim/Assertion/Reconstruction from ingest),
ContentHistory/novelty (no placeholder), DuckDB + Postgres stores, real event-driven
shot graph, offline full-stack `simulate` command, 5 live channels, 21 tests.
