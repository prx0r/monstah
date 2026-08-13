Yes. Monstah is now at the same point RoboBladez is: **stop adding horizontal capability and force one evidence-backed world all the way through to a finished rendered film.**

`81290be` closed the dangerous epistemic holes: monotonic truth layers, real provenance IDs, canonical-vs-source asset separation, independent ShotBasis, immutable simulation-event IDs with state, renderer profiles, and CI are now actual mechanisms.  The repo already runs ingest → evidence → discovery → validity → simulation/graph → significance → story → shots → LTX bundle offline.

So the next target should be:

> **One command takes a scientifically grounded scenario from public APIs to a reviewed canonical reconstruction, renders a complete LTX-2.5 documentary sequence, automatically checks it against evidence/reconstruction constraints, repairs failures, and emits a final MP4 with full provenance.**

# Monstah MVP definition

I would make the first flagship vertical slice **Titans of Deep Time**, because it exercises nearly every hard problem:

```text
PBDB
+ Macrostrat
+ literature
+ fossil/reference imagery
→ canonical animal reconstructions
→ canonical environment reconstruction
→ historically valid scenario
→ simulation/data event
→ narrative
→ controlled LTX footage
→ evidence QA
→ final episode
```

Use one narrow world:

```text
HELL CREEK MVP
```

and only 2–3 taxa.

For example:

```text
Tyrannosaurus
Triceratops
Edmontosaurus
```

The exact taxa matter less than completing the chain.

The MVP command should eventually be something like:

```bash
monstah produce \
  --channel prehistoric \
  --world hell-creek \
  --scenario auto \
  --render \
  --profile final \
  --out out/hell-creek-mvp
```

and create:

```text
out/hell-creek-mvp/
├── evidence/
│   ├── sources.jsonl
│   ├── claims.jsonl
│   ├── assertions.jsonl
│   └── bibliography.json
│
├── reconstruction/
│   ├── taxa/
│   │   ├── tyrannosaurus-R1.json
│   │   └── triceratops-R1.json
│   ├── environment/
│   │   └── hell-creek-R1.json
│   └── reconstruction-manifest.json
│
├── assets/
│   ├── source/
│   ├── reference-packs/
│   ├── canonical/
│   └── asset-manifest.json
│
├── scenario/
│   ├── scenario.json
│   ├── validity.json
│   └── simulation.json
│
├── events/
│   └── canonical-events.jsonl
│
├── story/
│   ├── episode.json
│   ├── narrative-claims.json
│   └── beats.json
│
├── shots/
│   ├── shot-001.json
│   ├── shot-002.json
│   └── ...
│
├── controls/
│   ├── first-frames/
│   ├── last-frames/
│   ├── depth/
│   └── guides/
│
├── renders/
│   ├── drafts/
│   ├── finals/
│   └── retakes/
│
├── qa/
│   ├── epistemic.json
│   ├── visual.json
│   └── shot-verdicts.json
│
├── episode/
│   ├── master.mp4
│   ├── vertical.mp4
│   └── episode-manifest.json
│
└── RUN.json
```

If that exists and everything links backward, **Monstah MVP exists.**

---

# Phase 1 — define a first-class WorldSnapshot

Right now the pieces exist, but the episode needs one immutable statement of:

> **Which world did we reconstruct?**

Create:

```text
WorldSnapshot
```

containing:

```yaml
world_id: hell-creek
world_version: R1

temporal_extent:
  min_ma:
  max_ma:

spatial_extent:
  geometry_ref:
  paleocoordinates:

environment:
  reconstruction_id:
  assertion_ids:

entities:
  - entity_id:
    reconstruction_id:
    assertion_ids:

relations:
  - relation_id:
    assertion_ids:

uncertainty_summary:
```

This becomes the canonical input to discovery/media.

The important hierarchy:

```text
Sources
↓
Claims
↓
Assertions
↓
Reconstruction
↓
WorldSnapshot
```

Your evidence chain is now mechanically persisted rather than fabricated, so this is the natural next aggregation layer.

### Exit gate

Given the same persisted evidence versions:

```text
WorldSnapshot.digest
```

is identical.

Change one reconstruction version:

```text
digest changes.
```

---

# Phase 2 — real reconstruction versioning

Current `R1` is enough for the architecture test, but a production system needs meaningful evolution.

Define:

```text
ReconstructionVersion
```

with:

```text
entity
version
basis_assertions
derivation_method
assumptions
uncertainties
supersedes
status
```

Statuses:

```text
DRAFT
REVIEWED
APPROVED
SUPERSEDED
```

Do this for both:

```text
TaxonReconstruction
EnvironmentReconstruction
```

The key rule:

> **LTX may only receive an APPROVED reconstruction.**

Not a raw evidence bundle.

Not a draft.

Not merely “R1”.

---

# Phase 3 — build actual ReferencePacks

You already have:

```text
GBIF
iNaturalist
Wikimedia
BHL
```

plus licensing and role preservation, and the canonical/source resolver split now prevents extinct raw references from becoming LTX truth.

Now make the pack selector structurally useful.

Create:

```text
ReferencePack
```

For extinct taxa:

```text
MORPHOLOGY
├ lateral skeleton
├ dorsal/top if available
├ skull/detail
├ primary specimen
├ anatomical plate
├ historical reconstruction
└ literature figures
```

For environment:

```text
ENVIRONMENT
├ geology
├ flora
├ depositional context
├ climate
├ landscape analogues
└ historical reconstructions
```

Don't use simple top-N scoring.

Use constrained portfolio selection:

```text
maximize evidence/reuse score
subject to required roles + viewpoint diversity
```

### Exit gate

For T. rex, asking twice returns the same immutable pack and doesn't simply return five aesthetically similar images.

---

# Phase 4 — canonical reconstruction image pipeline

This is probably the biggest missing piece between the current asset infrastructure and LTX.

For extinct taxa:

```text
SOURCE REFERENCES
↓
ReferencePack
↓
VisualReconstructionSpec
↓
image generator
↓
candidate reconstruction images
↓
scientific visual QA
↓
human approval
↓
CanonicalVisualReconstruction
```

Create:

```text
VisualReconstructionSpec
```

Example:

```yaml
entity_id:
reconstruction_id:

morphology:
  skull:
  torso:
  limbs:
  tail:
  integument:

dimensions:
  body_length:
  hip_height:

appearance:
  constrained:
  uncertain:
  speculative:

required_views:
  - lateral
  - three_quarter
  - front
  - dorsal

reference_pack_id:
forbidden:
```

Do **not** store the generation prompt as truth.

Same principle as RoboBladez:

```text
machine-readable reconstruction spec
→ provider-specific prompt
```

---

# Phase 5 — real image-generation backend

Create a provider-neutral contract:

```python
class ReconstructionImageBackend:
    def generate(
        self,
        spec: VisualReconstructionSpec,
        references: ReferencePack,
        view: ViewSpec,
    ) -> list[ImageCandidate]:
        ...
```

Then:

```text
OpenAIImageBackend
OtherImageBackend
```

can be swapped.

You only need one working backend for MVP.

The system should generate maybe:

```text
4 candidates × 3 views
```

not hundreds.

---

# Phase 6 — scientific visual QA

This is the important difference from RoboBladez.

RoboBladez asks:

> does it match canon?

Monstah asks:

> does it match the evidence-constrained reconstruction?

Build:

```text
ReconstructionVisualQA
```

Checks:

```text
body-plan match
limb count
relative proportions
skull shape
major integument requirements
forbidden speculative structures
environment compatibility
reference consistency
```

And importantly classify failure by epistemic importance:

```text
P0_FACTUAL
P1_RECONSTRUCTION
P2_VISUAL
```

Example:

```text
extra horn
→ P0/P1

wrong skin color where color is unconstrained
→ possibly acceptable variation
```

Don't falsely imply every visible property is scientifically established.

---

# Phase 7 — make uncertainty visually explicit

This could become a real Monstah differentiator.

Every reconstruction property should eventually be one of:

```text
CONSTRAINED
INFERRED
OPEN
SPECULATIVE
```

Then a generated reconstruction manifest could say:

```text
skull geometry       CONSTRAINED
body dimensions      RECONSTRUCTED
integument pattern   OPEN
coloration            SPECULATIVE
```

The public media doesn't need labels over every frame, but the underlying system knows what it is allowed to claim.

That enables lines like:

> “The skeleton is well constrained. The coloration is not.”

without hand authoring caveats.

---

# Phase 8 — environment reconstruction images

Do the same for worlds.

Create:

```text
EnvironmentVisualSpec
```

from:

```text
Macrostrat
PBDB fauna/flora
geology
paleoclimate where available
published reconstructions
```

Then generate:

```text
HELL_CREEK_R1
├ wide
├ low ground
├ river/floodplain
├ vegetation plate
├ atmospheric reference
└ lighting reference
```

Approve it once.

Then every future Hell Creek episode reuses it.

This is where the **visual moat compounds**.

---

# Phase 9 — canonical asset registry

The repository already has asset tables/storage concepts.

Now formalize:

```text
CanonicalAsset
```

with:

```text
asset_id
entity/environment id
reconstruction_version
visual_version
view
role
status
file_sha256
reference_pack_id
generator_manifest
review history
supersedes
```

Critical lookup:

```python
canonical_assets.resolve(
    entity_id,
    reconstruction_version,
    view,
)
```

Never:

```python
find_some_image("Tyrannosaurus")
```

inside rendering.

---

# Phase 10 — persist canonical state properly

The current progress doc explicitly says Postgres/DuckStore are not yet fully wired into channel publish; R2 is currently doing that role.

Do this now, before generating lots of data.

Responsibilities:

### Postgres

Canonical:

```text
entities
sources
claims
assertions
reconstructions
world_snapshots
scenarios
canonical_events
assets
asset_versions
episodes
shots
```

### DuckDB/Parquet

Analytical:

```text
millions of occurrences
GloBI edges
simulation runs
channel analytics
candidate scoring
```

### R2

Binaries:

```text
images
videos
JSON exports
control frames
reference packs
```

No ambiguity.

---

# Phase 11 — create immutable ScenarioManifest

A scenario should pin:

```text
ScenarioManifest
├ world_snapshot_digest
├ participant reconstruction versions
├ environment reconstruction
├ relation basis
├ ScenarioMode
├ validity result
├ model version
└ assumptions
```

Then:

```text
scenario_digest
```

becomes the simulation/story root.

For historical:

```text
VALID
```

must be established before running a historical-content path.

For Lab:

```text
COUNTERFACTUAL
```

stays attached permanently.

You already successfully separated ScenarioMode from ShotBasis; preserve that architecture.

---

# Phase 12 — stop treating all “simulations” alike

For Monstah, simulation is going to branch into different model classes.

Define:

```text
SimulationModel
```

with:

```text
model_id
model_version
model_class
scientific_status
inputs
assumptions
outputs
```

Classes:

```text
GAME_PROXY
MECHANISTIC_MODEL
STATISTICAL_MODEL
GRAPH_MODEL
NO_SIMULATION
```

Your current Open5e/d20 model should remain honestly:

```text
GAME_PROXY
```

not gradually become “the prehistoric simulator.”

That leaves room later for:

```text
locomotion models
energetic models
biomechanical models
population/ecosystem models
```

without breaking epistemic semantics.

---

# Phase 13 — improve the first simulation vertical

For MVP, keep d20 if necessary.

But alter presentation from:

> “T. rex wins because AC…”

to:

> “Under this explicit game-proxy combat model…”

More importantly, output:

```text
SimulationRun
├ run_id
├ scenario_digest
├ model_id/version
├ seed
├ initial_state
├ events
├ final_state
└ outcome
```

You now have immutable event IDs and pre/post state reaching shots.

Build outward from that.

---

# Phase 14 — Event→Story should become claim-aware

Create:

```text
StoryBeat
```

containing:

```text
beat_id
shot_basis
basis_event_ids
basis_assertion_ids
basis_reconstruction_ids
narrative_claim_ids
importance
```

Different beat kinds:

```text
SOURCE_FACT
RECONSTRUCTION
GRAPH_RELATION
SIMULATION_RESULT
EDITORIAL_BRIDGE
UNCERTAINTY
```

Then your narrative can never blur:

```text
fossil evidence says X
```

with:

```text
simulation predicts Y
```

The new real Source→Claim→Assertion chain makes this possible now.

---

# Phase 15 — EpisodeSpec should become executable

Create an actual final:

```text
EpisodeSpec
```

```yaml
episode_id:
channel:
world_snapshot:
scenario:

thesis:
question:
hook:

beats:
  - ...

narrative_claims:
  - ...

required_assets:
  - ...

uncertainties:
  - ...

duration_target:
aspect_targets:
```

This becomes the only input to the media compiler.

Not ad hoc story strings.

---

# Phase 16 — build deterministic scientific graphics alongside LTX

This is important.

**Do not generate every visual with LTX.**

Monstah should have two renderers:

```text
GENERATIVE
LTX

DETERMINISTIC
ScientificRenderer
```

ScientificRenderer handles:

```text
maps
timelines
phylogenies
food webs
occurrence plots
fossil ranges
depth plots
confidence diagrams
evidence cards
```

Then the episode alternates:

```text
beautiful reconstruction footage
+
actual data graphics
```

That dramatically increases credibility and reduces generation cost.

For the Hell Creek episode:

```text
PBDB occurrence map
temporal range diagram
environment reconstruction
animal footage
simulation visualization
```

---

# Phase 17 — ShotSpec v2 for Monstah

Every shot should state why it exists.

```yaml
shot_id:

basis:
  type: RECONSTRUCTION
  assertion_ids: []
  reconstruction_ids: []
  event_ids: []

subjects:
  - entity_id:
    reconstruction_version:
    canonical_visual_assets:

environment:
  reconstruction_version:
  canonical_assets:

camera:
prompt:
duration:

control:
  preferred:
  first_frame:
  last_frame:
  guide:

constraints:
qa:
```

Your current ShotBasis distinction is exactly the foundation for this.

---

# Phase 18 — ControlPlanner

Same general principle as RoboBladez:

> the more epistemically constrained the shot, the less freedom LTX gets.

Rules:

```text
generic landscape reconstruction
→ I2V

animal hero shot
→ I2V canonical reconstruction

simple movement
→ I2V

specific state transition
→ FIRST_LAST

simulation-event visualization
→ FIRST_LAST / KEYFRAME / guide video

data graphic
→ deterministic renderer

editorial atmospheric bridge
→ T2V allowed
```

T2V should be relatively rare for core scientific content.

---

# Phase 19 — deterministic control-frame compositor

For Monstah, this can be simpler initially than a full 3D animation system.

Take:

```text
canonical animal asset
canonical environment
event/state information
camera template
```

and create:

```text
first-frame plate
last-frame plate
depth approximation
```

These aren't final art.

They're **constraints** for LTX.

For a simulation event:

```text
pre_state
→ control frame A

post_state
→ control frame B
```

The fact that event pre/post state is now threaded into shots means you have the data substrate for this.

---

# Phase 20 — real LTX-2.5 adapter

You already moved version/model selection into `RendererProfile`, defaulting to 2.5 instead of hardcoding it in domain code.

Now implement the real backend:

```text
LTX25ApiRenderer
```

first.

Interface:

```python
submit(shot)
poll(job)
fetch(job)
retake(...)
reframe(...)
```

API first is the fastest MVP.

ComfyUI later.

Don't block the project on local GPU infrastructure.

---

# Phase 21 — use draft/final economics

Pipeline:

```text
EpisodeSpec
↓
8 ShotSpecs
↓
DRAFT render
↓
QA
↓
accepted shots
↓
FINAL render
↓
QA
↓
localized RETAKE
```

Do not final-render every candidate.

This should be fully automatic.

---

# Phase 22 — split QA into four distinct layers

Monstah needs more QA than RoboBladez.

## 1. BindingQA

Deterministic:

```text
right reconstruction version?
right assertion IDs?
right environment?
right assets?
right renderer manifest?
```

## 2. VisualIdentityQA

```text
does generated animal match canonical image?
silhouette?
limbs?
skull?
major markings?
```

## 3. EventQA

For simulation/graph-driven shots:

```text
does rendered action match basis?
does event order remain correct?
```

## 4. EpistemicQA

The most Monstah-specific.

Ask:

```text
did render introduce unsupported factual content?
```

Examples:

```text
invented herd behavior
invented feathers
invented interaction
invented environment species
invented injury
```

Verdict:

```text
PASS
RETAKE
REGENERATE
NEEDS_REVIEW
```

---

# Phase 23 — QA needs tolerance based on uncertainty

This is important.

If a reconstruction marks:

```text
skin coloration = OPEN
```

the QA system should **not reject** alternate plausible coloration.

If:

```text
horn count = CONSTRAINED
```

wrong horn count is a hard failure.

So QA must consume:

```text
ReconstructionConstraintSet
```

not simply compare pixels.

This gives you a huge conceptual advantage over generic AI-video pipelines.

---

# Phase 24 — Retake loop

Use:

```text
shot
↓
render
↓
QA
```

If failure localized:

```text
2.1–3.6 sec
```

then:

```text
Retake
```

If whole shot identity wrong:

```text
regenerate from stronger controls
```

If reconstruction itself looks wrong:

```text
STOP
```

Do not “fix” canon in the renderer.

Return upstream to reconstruction review.

---

# Phase 25 — narration should compile from claims

Build narration only from:

```text
NarrativeClaim[]
```

Every factual clause should know:

```text
assertion_ids
source_refs
status
```

Then script generation can automatically distinguish:

```text
KNOWN:
"Fossils place these animals in..."

RECONSTRUCTED:
"The environment was likely..."

MODELLED:
"In our simulation..."

UNKNOWN:
"We cannot currently establish..."
```

This is one of the strongest possible Monstah features.

---

# Phase 26 — episode assembler

Use ffmpeg for MVP.

Combine:

```text
LTX clips
deterministic graphics
narration
subtitles
music
citations
```

Produce:

```text
master 16:9
```

then:

```text
9:16 derivative
```

Aim first for:

```text
60–120 seconds
```

not 20 minutes.

A 90-second scientifically grounded finished film proves much more than another ten APIs.

---

# Phase 27 — EpisodeManifest

Every final episode:

```text
EpisodeManifest
├ WorldSnapshot digest
├ scenario digest
├ Sources
├ Assertions
├ Reconstruction versions
├ SimulationModel version
├ run IDs
├ canonical event IDs
├ canonical visual asset digests
├ ShotSpec digests
├ renderer manifests
├ QA verdicts
├ narration claim bindings
└ master video digest
```

Now you can literally answer:

> Why is this dinosaur shown like this at frame 1840?

That's the Monstah moat.

---

# Phase 28 — one-command vertical harness

Create:

```python
produce_episode(...)
```

or:

```bash
monstah produce
```

which orchestrates:

```text
INGEST
↓
WORLD BUILD
↓
VALIDATE
↓
DISCOVER
↓
SELECT
↓
RECONSTRUCT
↓
RESOLVE/GENERATE ASSETS
↓
SIMULATE
↓
STORY
↓
SHOT COMPILE
↓
CONTROL GENERATION
↓
RENDER
↓
QA
↓
RETAKE
↓
ASSEMBLE
↓
PUBLISH
```

Each phase resumable by manifest.

If render crashes:

```text
do not re-ingest PBDB.
```

If QA fails:

```text
do not rebuild reconstruction.
```

This matters enormously for autonomous production.

---

# Phase 29 — add run-state / resumability

Create:

```text
ProductionRun
```

Statuses:

```text
INGESTED
WORLD_BUILT
RECONSTRUCTED
ASSETS_READY
SCENARIO_READY
SIMULATED
STORY_READY
SHOTS_READY
RENDERING
QA
ASSEMBLED
PUBLISHED
FAILED
```

Every step writes its digest and dependencies.

Then:

```bash
monstah resume <run-id>
```

This will save a lot of money when remote API/GPU work fails halfway through.

---

# Phase 30 — first actual MVP film

Do one episode only.

Suggested structure:

```text
0–5s       hook
5–15s      actual fossil/data basis
15–30s     reconstructed world
30–45s     introduce taxa
45–60s     scenario question
60–80s     model/simulation result
80–95s     uncertainty/crux
95–105s    conclusion
```

Use around:

```text
4 LTX clips
3 deterministic graphics
1–2 evidence/source visuals
```

This mixture is better than trying to make 100% AI footage.

---

# Phase 31 — only after that, turn it into an autonomous content machine

Then run:

```text
PBDB universe
↓
ScenarioDiscovery
↓
100 candidate stories
↓
significance/novelty
↓
rank
```

Select top 10.

But don't render all 10.

Generate:

```text
story plans
asset reuse analysis
cost estimates
```

Then render highest-value one.

This becomes:

```text
AUTO EDITORIAL CALENDAR
```

---

# Phase 32 — asset compounding

After each episode:

```text
new canonical assets
new source packs
new environments
new taxon reconstructions
new maps
```

remain reusable.

Episode 1 might require:

```text
T. rex
Triceratops
Hell Creek
```

Episode 2 adds:

```text
Edmontosaurus
```

but reuses everything else.

Production cost should decline as the corpus expands.

Track:

```text
asset_reuse_rate
new_asset_cost
render_cost
episode_cost
```

Those should become core operational metrics.

---

# Phase 33 — first mini-season

Only once the single episode works:

```text
5 Hell Creek episodes
```

all sharing:

```text
environment
taxa
maps
reconstruction assets
```

This proves the asset moat.

Then:

```text
Ancient Oceans
```

can become world #2.

Do **not** jump to Alien Worlds yet despite it being on the current project next-list. The current PROGRESS doc still lists Alien Worlds and more channel work, but I would explicitly defer that until the production vertical is proven.

---

# What I would not build yet

Defer:

```text
Alien Worlds
Ancient Worlds
another 5 channels
mass UI
consumer website
huge global ingest
custom fine-tuning
complex ecosystem simulation
full 3D paleo engine
real-time generation
automatic publishing to 10 networks
```

All of them are downstream multipliers.

The current blocker is:

> **Can one evidence-backed world become a finished defensible film automatically?**

---

# Target code structure

You don't need to reorganize everything immediately, but this is the eventual responsibility map:

```text
src/monstah/
├── evidence/
│   ├── sources.py
│   ├── claims.py
│   ├── assertions.py
│   └── builder.py
│
├── reconstruction/
│   ├── taxon.py
│   ├── environment.py
│   ├── constraints.py
│   ├── world.py
│   └── versioning.py
│
├── assets/
│   ├── source_resolver.py
│   ├── reference_pack.py
│   ├── canonical.py
│   ├── visual_spec.py
│   ├── image_backend.py
│   └── qa.py
│
├── scenarios/
│   ├── discovery.py
│   ├── manifest.py
│   └── validity.py
│
├── simulations/
│   ├── model.py
│   ├── d20.py
│   ├── montecarlo.py
│   └── events.py
│
├── story/
│   ├── significance.py
│   ├── claims.py
│   ├── beats.py
│   └── episode.py
│
├── media/
│   ├── shot_spec.py
│   ├── control.py
│   ├── scientific_renderer.py
│   ├── renderer.py
│   ├── ltx25.py
│   ├── qa.py
│   └── assembler.py
│
├── production/
│   ├── run.py
│   ├── manifest.py
│   └── resume.py
│
└── cli.py
```

---

# Exact commit sequence

I would hand the dev agent this order:

```text
01 Add WorldSnapshot + stable digest
02 Add reconstruction lifecycle/versioning
03 Add ReferencePack requirements + diversity selection
04 Add VisualReconstructionSpec
05 Add provider-neutral reconstruction image backend
06 Wire one real image-generation provider
07 Add ReconstructionVisualQA
08 Add EnvironmentVisualSpec + canonical environment assets
09 Add immutable CanonicalAsset registry + content hashes
10 Wire Postgres canonical state + DuckDB analytics into production
11 Add ScenarioManifest + scenario digest
12 Add SimulationModel metadata/classes
13 Pin run/model/event identity through full pipeline
14 Add claim-aware StoryBeat
15 Add executable EpisodeSpec
16 Add deterministic ScientificRenderer
17 Add ShotSpec v2 with reconstruction/assertion/event bindings
18 Add ControlPlanner
19 Add first/last control-frame compositor
20 Implement real LTX25ApiRenderer
21 Add resumable render queue
22 Add BindingQA
23 Add VisualIdentityQA
24 Add EventQA
25 Add EpistemicQA
26 Add uncertainty-aware QA constraints
27 Add automatic Retake/regeneration loop
28 Compile narration from NarrativeClaims
29 Add ffmpeg EpisodeAssembler
30 Add EpisodeManifest
31 Add ProductionRun state machine + resume
32 Add `monstah produce --render`
33 Produce first Hell Creek MVP film
34 Run adversarial provenance/visual tests
35 Freeze MONSTAH-MVP-v1
36 Produce 5-episode Hell Creek mini-season
```

# The acceptance test

The MVP is done when this statement is true:

```text
A taxon enters Monstah as public evidence.

Every factual assertion retains its source.

A reconstruction is explicitly derived and versioned.

Images are collected as evidence, not mistaken for the reconstruction.

A canonical visual reconstruction is generated and approved.

A historical scenario can only proceed if its truth policy permits it.

Any simulation clearly declares what kind of model it is.

Important outputs become immutable events or graph-derived facts.

The story can state only claims supported by those objects.

Every shot states its epistemic basis.

LTX receives approved reconstruction assets and constrained control inputs.

Generated footage is checked against reconstruction and epistemic constraints.

Bad intervals are repaired.

A final episode is assembled.

Every factual sentence, visual subject, and modeled event can be traced backward.
```

Once that works for one Hell Creek film, **Monstah is no longer a world-engine prototype. It is an autonomous evidence-to-media production system.**

Then scale worlds, channels, simulations, and output volume—not architecture.
