# Monstah Docs — Index

A machine-readable world reconstruction + simulation engine → YouTube channel identities.
Core: **one engine, many data APIs → reusable assets → historically-accurate graph-derived
battles → LTX footage.** Truth is evidence-constrained; the content layer never decides
what is true.

**Start here:**
1. **[ONBOARDING.md](ONBOARDING.md)** — how a new agent picks up the project (quickstart,
   architecture, where things live, conventions).
2. **[AUDIT.md](AUDIT.md)** — what is LIVE vs LEGACY, wiring gaps, name collisions, security.
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** — the system design + truth rules + module map.
4. **[PROGRESS.md](PROGRESS.md)** — status of everything built.

## Full doc map

| Doc | What it is |
|---|---|
| **ONBOARDING.md** | New-agent entry point (read first) |
| **AUDIT.md** | Live vs legacy, wiring gaps, collisions, security |
| **ARCHITECTURE.md** | System design, truth rules, module map |
| **PROGRESS.md** | Status of everything built + fixes |
| **MVP.md** | The 32-phase evidence-to-media MVP plan + commit ladder (01–20 done) |
| **THESIS.md** | The original Evidence World Engine thesis (canonical guide) |
| **DATA.md** | Data availability per API, mass-import strategy, graph schema |
| **CHANNELS.md** | 10-channel spec with trending-data strength scores |
| **LTX_USAGE.md** | How we use LTX (I2V-first, ShotSpec as execution plan, Retake, Reframe) |
| **ASSETS.md** | Canonical image/asset system: providers, license policy, versioned reconstructions |
| **REVIEW_NOTES.md** | Peer-review findings + truth-preservation fixes |
| `../media/ltx/` | Vendored LTX-2.3 production pack (prompting, control hierarchy, ComfyUI, hardware) |
| `../channels/*/DATAFLOW.md` | Per-theme dataflow (sources → adapter → policies → output) |

## CLI quick reference
```
monstah produce <channel> [--world] [--out]   # one-command vertical slice (main path)
monstah resume <channel> <run-path>           # resume from RUN.json
monstah channel <channel>                     # run a theme end-to-end
monstah simulate <channel> --offline          # full offline stack, no LTX/network
monstah snapshot <channel>                    # immutable WorldSnapshot + digest
monstah matchup <a> <b>                       # Monte Carlo duel (Open5e statblocks)
monstah ingest <taxa...>                      # live PBDB/Macrostrat (legacy path)
monstah scenarios | run                       # legacy
```

## Verification
```
.venv/bin/python -m pytest tests/ -q   # 59 offline tests
.venv/bin/monstah produce prehistoric --out out/produce
```
