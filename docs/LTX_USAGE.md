# How We Use LTX (2.5 / 2.3)

Status: LTX is a **replaceable renderer downstream of canonical project state.** It
must never decide scientific truth. The value of a stronger model is *controllability*,
not prettier clips — every control improvement lets us turn precise machine-readable
truth into convincing footage without giving the model authority over that truth.

> The more LTX obeys control signals, the less intelligence it needs to exercise —
> and the more valuable our upstream world/canon/data layer becomes. Renderers are
> commoditized; our evidence/asset/simulation layer is not.

## Our default is I2V, not T2V

```
CANONICAL ASSET ──► I2V ──► motion
```
not
```
text ──► hope it redraws the right subject
```

- Monstah: `TREX_RECON_R17.png + ShotSpec + env reference ─► LTX`
- RoboBladez: `BORIS_TALISMAN_R08.png + arena state + ShotSpec ─► LTX`

Canonical reconstruction assets then **compound** instead of being recreated each video.

## Prompt adherence == ShotSpec execution

Our prompts are execution plans, not creative prose. The better LTX follows
compositional/temporal instructions, the more valuable our **event → ShotSpec compiler** is.

## First-frame → last-frame control (main rendering primitive)

Simulation gives exact states; we hand LTX the canonical BEFORE + AFTER and let it
fill the cinematic transition. Less room to invent. Same for biologically-plausible
pose transitions in Monstah.

## Multi-keyframe conditioning

Constrain `A→B→C→D` from simulation states (frame 0 circling → frame 48 attack →
frame 82 contact → frame 120 separation). LTX only cinematizes interstitial motion.

## Motion/control conditioning (ideal architecture)

```
deterministic simulator ─► cheap guide render ─► depth/motion/edges ─► LTX ─► cinematic
```
Simulator owns: trajectory, contact, timing, orientation, relative position.
LTX owns: materials, lighting, camera, effects, atmosphere, audio, appearance.
**This cleanly divides truth from presentation.**

## Fine-detail preservation (disproportionately valuable for Monstah)

Feathers, scales, fins, limb proportions, teeth, soft-tissue geometry, skin pattern can
all be tied to a reconstruction. Better detail retention = less drift from scientific
reference. That is different from "the video looks sharper."

## Long-shot coherence = cheaper production

If one 8s controlled clip holds identity+environment+camera, we stop doing
`4 × 2s clips + continuity fixing`. Fewer assets, fewer mismatches, simpler editing,
less narration to mask cuts.

## Native AV generation

Let water/wind/footsteps/ambience arise from the same temporal generation (aligned to
motion). Keep narration and music downstream. Foley sync is useful.

## Retake (first-class)

- `S27: 0–2.8s ✅, 2.8–4.1s ❌ (leg deforms), 4.1–8s ✅` → repair only the bad span.
- Add automatic vision QA: render → compare vs ShotSpec → localize temporal error →
  Retake → verify. This turns generative video into a production system.

## Reframe (multi-channel)

Render one `MASTER 16:9`, then derive:
```
YouTube 16:9 · Shorts 9:16 · TikTok 9:16 · Instagram 4:5
```
Essential for the Monstah multi-channel strategy.

## Per-project killer features

**RoboBladez** (has exact ground truth; renderer must OBEY):
motion consistency, keyframe adherence, subject permanence, exact state-transition
rendering, synchronized impacts/audio, Retake.

**Monstah** (main danger = AI silently changing the reconstruction):
I2V reconstruction fidelity, fine-detail preservation, subject persistence,
controlled natural movement, environment stability, longer documentary shots, Retake.

## The event→shot→render loop that works

### RoboBladez
```
BORIS AI ─► reincarnation ─► deterministic fight ─► canonical trajectory
  ─► guide animation ─► LTX-2.5 ─► cinematic battle ─► auto QA ─► Retake ─► episode
```

### Monstah
```
SOURCE GRAPH ─► reconstruction ─► scenario ─► simulation/data event
  ─► canonical visual references ─► LTX-2.5 ─► documentary footage
  ─► scientific QA ─► Retake ─► episode
```
