# THESIS — The Evidence World Engine

The project is not “a dinosaur channel” or “a deep-sea channel.”

It is a **machine-readable world reconstruction and simulation engine** that takes structured evidence about entities, environments, traits, relationships and uncertainty, generates plausible scenarios, simulates them, detects interesting events, and turns those events into media.

The core chain is:

```text
EVIDENCE
↓
WORLD MODEL
↓
RECONSTRUCTION
↓
SCENARIO
↓
SIMULATION
↓
EVENTS
↓
STORY
↓
SHOT GRAPH
↓
LTX / MEDIA
↓
CHANNEL
```

The central constraint is:

> **The content layer never determines what is true. It only determines which supported or simulated truths are interesting enough to show.**

That makes this fundamentally different from ordinary AI content generation.

Normal AI content:

```text
prompt
→ plausible prose
→ plausible video
```

This system:

```text
sources
→ claims
→ normalized entities
→ reconstructed world state
→ simulation
→ canonical event record
→ narrative projection
→ media
```

The resulting media may be cinematic, speculative or counterfactual, but the system always knows **which layer it is operating in**.

---

# 1. The two-world thesis

The same engine can support two very different classes of universe.

## Synthetic worlds

RoboBladez:

```text
we define rules
↓
simulation creates truth
↓
truth becomes canon
```

## Evidence worlds

Prehistory, deep ocean, ecology, evolution:

```text
external evidence
↓
uncertain reconstruction
↓
simulation explores consequences
↓
content communicates result + uncertainty
```

The reusable substrate is:

```text
ENTITY
MODEL
ENVIRONMENT
RELATION
SCENARIO
SIMULATION
EVENT
STORY
SHOT
ASSET
```

The evidence-world extension adds:

```text
SOURCE
CLAIM
ASSERTION
PROVENANCE
UNCERTAINTY
RECONSTRUCTION
```

So the common platform becomes:

```text
                    WORLD ENGINE

          ┌──────────────┴──────────────┐
          │                             │
     SYNTHETIC                     EVIDENCE
     RoboBladez                  Life / Earth
          │                             │
          └──────────────┬──────────────┘
                         │
                    SIMULATION
                         │
                       EVENTS
                         │
                      ANALYSIS
                         │
                       STORY
                         │
                       SHOTS
                         │
                       MEDIA
```

---

# 2. The factual-world core

The factual system should not be organized by channel.

Do not build:

```text
/dinosaurs
/deepsea
/insects
/extinction
```

Build a normalized **Life + Earth Graph**.

```text
                         LIFE GRAPH
                             │
           ┌─────────────────┼────────────────┐
           │                 │                │
       extinct taxa      extant taxa      lineages
           │                 │                │
        fossils         occurrences       phylogeny
           │                 │                │
           └─────────────┬───┴────────────────┘
                         │
                    ECOLOGY GRAPH
                         │
          predator / prey / host / parasite
          competitor / pollinator / symbiont
                         │
                     EARTH GRAPH
                         │
             geology / climate / depth
             geography / paleoenvironment
```

Channels then become **different query-and-story policies over the same graph**.

That is a critical architectural choice.

---

# 3. External data sources

The first-party factual substrate we discussed is unusually strong.

## Paleobiology Database

Use PBDB for:

```text
fossil taxa
occurrences
collections
geological ages
formations
references
locations
taxonomic relations
```

Core role:

> **Where and when did extinct organisms occur?**

This drives historical-overlap queries.

Example:

```text
SELECT taxa
WHERE
    age overlaps 70–68 Ma
AND region overlaps western North America
AND environment compatible
```

Then scenario generation can ask:

> Which animals actually could have encountered each other?

---

# 4. Macrostrat

PBDB gives you the fossil.

Macrostrat helps reconstruct the world around it.

Use it for:

```text
rock unit
stratigraphic context
lithology
geological age
map polygons
formations
depositional setting
```

Combined:

```text
PBDB occurrence
+
Macrostrat geology
=
paleoenvironment context
```

Instead of:

> “T. rex on generic jungle floor”

you can reconstruct:

```text
Hell Creek
specific age interval
fluvial/floodplain context
co-occurring taxa
relevant formation
```

---

# 5. GBIF

Use for modern terrestrial and general biodiversity.

```text
species
taxonomy
occurrences
geography
observation dates
multimedia metadata
```

This gives a common graph for living and extinct organisms.

Example:

```text
entity:Tyrannosaurus_rex
status: extinct

entity:Carcharodon_carcharias
status: extant
```

Different occurrence providers; same canonical entity layer.

---

# 6. OBIS

This is the core of the future **Deep Blue** channel.

Use it for:

```text
marine occurrences
depth
coordinates
taxa
datasets
regions
observation distributions
```

This lets you query:

```text
all known cephalopod records
deeper than 3000 m
in North Pacific
```

or:

```text
species observed below 6000 m
```

or:

```text
rare predators recorded around trench X
```

The data itself generates episode candidates.

---

# 7. GloBI

This may be the most generative source in the whole stack.

Instead of just species:

```text
A
B
C
```

you get:

```text
A eats B
A parasitizes C
B hosts D
C competes with E
```

So the graph becomes ecological.

That gives immediate scenario grammar:

```text
predator → prey
host → parasite
pollinator → plant
competitor ↔ competitor
scavenger → carcass
symbiont ↔ host
```

This is what lets you build ecosystem stories rather than animal encyclopedia videos.

---

# 8. EOL TraitBank

Use traits to convert taxonomy into capability models.

Potential traits:

```text
body length
body mass
diet
habitat
locomotion
life history
depth preference
reproductive strategy
ecological role
```

Where evidence exists.

TraitBank is useful because:

```text
taxon identity
+
traits
=
proto simulation model
```

---

# 9. Open Tree of Life

Use the phylogenetic tree for evolutionary structure.

It answers relationships like:

```text
common ancestor(A,B)
nearest relatives
clade membership
lineage structure
```

This enables an entire evolutionary-content layer:

```text
trait transitions
lineage expansion
marine transitions
flight origins
size changes
extinction survivors
```

---

# 10. Literature layer

The structured databases will not contain enough physiological or behavioral detail for good reconstruction.

So every taxon also connects to literature.

Use:

```text
OpenAlex
Crossref
Unpaywall
publisher metadata
open-access papers
```

The flow:

```text
entity
↓
paper discovery
↓
claim extraction
↓
claim verification
↓
structured assertion
```

Example paper statement:

> estimated body mass 6.5–9 tonnes

should become:

```json
{
  "entity": "taxon:T_REX",
  "trait": "adult_mass",
  "distribution": {
    "lower": 6500,
    "central": 7800,
    "upper": 9000,
    "unit": "kg"
  },
  "status": "LITERATURE_ESTIMATE"
}
```

Never silently turn it into:

```text
mass = 7800
```

---

# 11. Canonical entity model

The core entity should be provider-independent.

```text
Entity

id
canonical_name
entity_type
status
taxonomy
crosswalks
```

Crosswalk:

```text
Internal Entity ID
├── PBDB ID
├── GBIF key
├── OTT ID
├── EOL ID
├── WoRMS / Aphia ID
├── Wikidata ID
└── other identifiers
```

Do not use names as primary identifiers.

Names change.

---

# 12. Assertion architecture

Every uncertain factual property should be represented as an assertion.

```text
TraitAssertion

entity_id
trait_id
value
unit
distribution
status
confidence
method
source_id
source_locator
created_at
supersedes
```

Statuses:

```text
OBSERVED
DIRECT_MEASUREMENT
LITERATURE_ESTIMATE
INFERRED
MODELLED
SIMULATION_ASSUMPTION
SPECULATIVE
```

This distinction is essential.

Example:

```text
fossil femur length
= OBSERVED

body mass derived from scaling
= LITERATURE_ESTIMATE / INFERRED

maximum sprint speed
= MODELLED

social hunting strategy
= SPECULATIVE / contested
```

---

# 13. Claim layer

A source may support multiple claims.

```text
Source
↓
Claim
↓
Assertion
```

Example:

```text
Paper X
↓
Claim 771:
estimated maximum body mass...
↓
TraitAssertion:
adult_mass distribution
```

This lets the content system later display:

> Why do we believe this?

---

# 14. Reconstruction object

Never have one eternal `Tyrannosaurus`.

Have versioned scientific reconstructions.

```text
Reconstruction

id
entity_id
version
source_set
parameter_set
uncertainty
visual_model
simulation_model
status
created_at
supersedes
```

Example:

```text
T_REX_RECON_R17
```

might contain:

```text
mass
length
center of mass
turn radius
bite force distribution
acceleration model
stamina assumptions
visual body plan
integument assumptions
behavior priors
```

Then later:

```text
R18 supersedes R17
```

Old episodes remain reproducible because they used R17.

---

# 15. Truth layers

For every factual-world episode, maintain three explicit layers.

## Layer 1 — Evidence

What sources actually report.

## Layer 2 — Reconstruction

What we infer/model.

## Layer 3 — Simulation

What happened under a specific reconstruction + scenario + seed.

Example:

```text
EVIDENCE:
mass estimates 6.5–9 tonnes

RECONSTRUCTION:
sample mass = 7.7 tonnes

SIMULATION:
this run used 7.84 tonnes
```

That separation should survive all the way to public-facing citations.

---

# 16. Historical Mode

Historical Mode is strict.

A scenario requires:

```text
temporal overlap
+
geographic overlap
+
environment compatibility
```

Potential historical query:

```text
Taxon A first/last age
intersects
Taxon B first/last age

AND

occurrence polygons overlap

AND

paleoenvironment is compatible
```

If not:

```text
HistoricalScenario.valid = false
```

No pretending.

---

# 17. Lab Mode

Lab Mode is explicitly counterfactual.

Examples:

```text
Megalodon vs Mosasaurus
T. rex vs Giganotosaurus
Smilodon vs modern lion
```

Bodies and capabilities remain evidence-constrained.

Only co-occurrence constraint is suspended.

Output labels should say:

```text
COUNTERFACTUAL LAB SIMULATION
```

not historical reconstruction.

This preserves clickability without contaminating the epistemic layer.

---

# 18. Don't make the simulator fight-only

This was one of the major earlier design decisions.

Scenario families should include:

```text
PREDATION
ESCAPE
AMBUSH
CHASE
SCAVENGING
RESOURCE COMPETITION
TERRITORIAL COMPETITION
MIGRATION
GROUP DEFENCE
PACK HUNT
HABITAT SELECTION
ENVIRONMENTAL STRESS
CLIMATE SHIFT
ECOSYSTEM COLLAPSE
COLONIZATION
EXTINCTION PRESSURE
```

The richest content will probably not be “X vs Y.”

It will be:

> What would a day in this ecosystem actually look like?

---

# 19. Generic simulation model

Each reconstructed animal becomes a capability model.

```text
AnimalModel

morphology
locomotion
perception
energy
damage/injury abstraction
behavior
ecological needs
```

Parameter distributions:

```text
mass ~ distribution
speed ~ distribution
acceleration ~ distribution
turning radius ~ distribution
stamina ~ distribution
bite force ~ distribution
reaction time ~ distribution
perception radius ~ distribution
```

Behavior initially via utility AI.

Example actions:

```text
APPROACH
RETREAT
CIRCLE
CHASE
AMBUSH
ATTACK
DEFEND
FEED
REST
REPOSITION
SEEK_COVER
SEEK_WATER
```

No RL needed for MVP.

---

# 20. Monte Carlo architecture

A scenario should almost never be one run.

Run:

```text
100
1000
10000
```

depending cost.

Output distribution:

```json
{
  "scenario": "...",
  "runs": 10000,

  "outcomes": {
    "predator_success": 0.42,
    "prey_escape": 0.51,
    "disengagement": 0.07
  }
}
```

Then choose:

```text
representative run
close run
surprising run
median run
```

for content.

Never cherry-pick without recording why.

---

# 21. Scenario Discovery Engine

This is one of the strongest parts of the architecture.

The user should not need to constantly think of episode ideas.

Build:

```text
ScenarioDiscovery
```

It queries the graph and scores opportunities.

Prehistoric:

```text
taxon A
× taxon B
× temporal overlap
× geographic overlap
× ecological relationship
× scientific uncertainty
```

Then:

```text
content_score =
    novelty
  × recognizability
  × interaction_strength
  × scientific_interest
  × uncertainty_interest
  × visual_interest
```

Output:

```text
Candidate #1
Candidate #2
Candidate #3
...
```

---

# 22. Content novelty system

Track everything already published.

```text
ContentHistory

entities_used
relationships_used
environment_used
scenario_type
claims_used
visual_assets_used
publication_metrics
```

Then penalize repetition.

Example:

```text
T. rex vs Triceratops
```

may score low after three videos.

But:

```text
juvenile Tyrannosaurus survival strategy
```

might score high.

---

# 23. The channels

## Channel 1 — LOST WORLDS

Flagship scientific reconstruction channel.

Promise:

> Reconstruct actual ancient ecosystems as rigorously as possible.

Episode examples:

```text
A Day in Hell Creek, 66 Million Years Ago
What Lived Alongside Spinosaurus?
Inside a Jurassic Floodplain
The Last Ecosystem Before the Asteroid
The World of the Permian Supercontinent
```

Input:

```text
PBDB
Macrostrat
literature
phylogeny
```

Simulation focus:

```text
ecosystem
movement
predation
competition
environment
```

---

# 24. Channel 2 — PREHISTORIC MATCHUPS

The highly clickable simulation channel.

Two modes visibly separated:

```text
HISTORICAL
LAB
```

Ideas:

```text
Could Deinonychus Actually Kill Tenontosaurus?
Could a T. rex Catch a Gallimimus?
Megalodon vs Livyatan
Mosasaurus vs Megalodon — Lab Simulation
```

Episode structure:

```text
evidence
↓
body reconstructions
↓
mechanical comparison
↓
simulation
↓
Monte Carlo result
↓
representative run
↓
uncertainty
```

---

# 25. Channel 3 — ANCIENT OCEANS

Potentially enormous.

Topics:

```text
Cambrian seas
Devonian oceans
Jurassic marine reptiles
Cretaceous oceans
ancient sharks
ammonites
marine extinctions
```

Episodes:

```text
The Deadliest Ocean in Earth History
What Actually Hunted Ammonites?
A Day in the Western Interior Seaway
When Ichthyosaurs Ruled the Ocean
```

---

# 26. Channel 4 — DEEP BLUE

Modern ocean data channel.

Core sources:

```text
OBIS
GBIF
GloBI
TraitBank
WoRMS-style identifiers
OpenTree
literature
```

The unique format:

> Query the real ocean database, then reconstruct the ecosystem.

Ideas:

```text
What Lives 6,000 Metres Below the Pacific?
The Deepest Predator Recorded Here
Every Animal Known From This Trench
The Midnight-Zone Food Web
What Actually Hunts Giant Squid?
The Animals Found Around Whale Falls
Life Beneath Antarctic Ice
The Rarest Deep-Sea Animals in the Database
```

This could be extremely scalable.

---

# 27. Channel 5 — TREE OF LIFE

Evolution channel.

Core:

```text
OpenTree
traits
fossils
occurrences
papers
```

Episodes:

```text
How Whales Returned to the Sea
The Evolution of Flight
Every Major Step From Fish to Tetrapod
Why Mammals Became Huge After the Dinosaurs
How Snakes Lost Their Legs
The Rise of Cephalopod Intelligence
```

Underlying object:

```text
LineageTransition
```

with:

```text
ancestor
descendant/clade
trait change
time
evidence
```

---

# 28. Channel 6 — LIVING PLANET

Modern ecology, but graph-first.

Not:

> 10 facts about wolves.

Instead:

> Reconstruct the ecological network.

Episodes:

```text
The Yellowstone Food Web
What Happens When Wolves Disappear?
Who Actually Eats Great White Sharks?
Inside a Mangrove Food Web
The Hidden Parasite Network of a Forest
```

Core engine uses GloBI relationships heavily.

---

# 29. Channel 7 — EXTINCTION

Earth-history transitions.

Object:

```text
ExtinctionEvent
```

with:

```text
before ecosystem
event
environmental forcing
losses
survivors
after ecosystem
radiation
```

Episodes:

```text
The Day the Permian World Collapsed
Who Survived the K–Pg Extinction?
Why Sharks Survived When Marine Reptiles Didn't
The Recovery After Earth's Worst Extinction
```

---

# 30. Channel 8 — EVOLUTION EXPERIMENTS

More simulation-heavy.

Questions:

```text
What if oxygen doubled?
What if gravity were slightly higher?
Which body plans survive this environment?
What pressures favor gigantism?
What does isolation do over 1 million generations?
```

This moves beyond reconstruction into transparent model exploration.

Label clearly:

```text
EVOLUTIONARY MODEL
```

---

# 31. Channel 9 — ALIEN WORLDS

Later extension.

Use planetary data.

Entity:

```text
Planet
Star
Moon
```

Environment:

```text
gravity
temperature
irradiation
orbit
atmospheric assumptions
```

Then:

```text
known planetary data
+
explicit assumptions
+
world simulation
```

Episodes:

```text
What Would It Be Like on TRAPPIST-1e?
The Most Extreme Known Exoplanets
Could an Ocean World Stay Habitable?
```

Same engine.

---

# 32. Channel 10 — ANCIENT WORLDS

Later archaeology/history adapter.

Entities:

```text
city
person
polity
route
object
commodity
```

Relationships:

```text
traded_with
ruled
fought
travelled
produced
minted
```

Potential episodes:

```text
A Day in Alexandria in 200 BCE
How Roman Trade Actually Moved Across the Mediterranean
What Reached India From Rome?
```

This is downstream, not MVP.

---

# 33. Shared content pipeline

All channels use:

```text
WORLD QUERY
↓
SCENARIO CANDIDATE
↓
SOURCE/CLAIM PACK
↓
RECONSTRUCTION
↓
SIMULATION
↓
EVENT LOG
↓
SIGNIFICANCE DETECTOR
↓
STORY COMPILER
↓
SHOT GRAPH
↓
ASSET RESOLVER
↓
LTX
↓
QA
↓
ASSEMBLY
↓
PUBLISH
```

---

# 34. Significance detector

Not every simulation deserves content.

Detect:

```text
upset
close escape
unexpected behavior
high uncertainty
rare relationship
ecological cascade
extreme environment
counterintuitive result
large model disagreement
```

Potential score:

```text
story_score =
    surprise
  × scientific_value
  × confidence
  × visual_interest
  × audience_interest
```

But low-confidence scenarios can still be valuable if framed as uncertainty:

> Scientists disagree about this animal's speed. Here is what changes if each estimate is right.

That is excellent content.

---

# 35. Story compiler

Input:

```text
Scenario
EvidencePack
SimulationSummary
RepresentativeRun
UncertaintyReport
```

Output:

```text
EpisodeSpec
```

Example structure:

```text
HOOK

What is the question?

EVIDENCE

What do we actually know?

RECONSTRUCTION

What assumptions did we have to make?

SIMULATION

What happened across many runs?

REPRESENTATIVE EVENT

What did one run look like?

CRUX

What variable mattered most?

UNCERTAINTY

What could change this conclusion?

CONCLUSION

What the simulation establishes
and what it does not establish
```

That should become the house style.

---

# 36. Shot compiler

Convert canonical events into media instructions.

Example:

```json
{
  "shot_id": "S042",
  "entity_versions": [
    "TREX_R17",
    "EDMONTOSAURUS_R11"
  ],
  "environment": "HELL_CREEK_R04",
  "event": "CHASE_TURN_003",
  "start_state": {},
  "end_state": {},
  "camera": "low tracking",
  "duration": 6,
  "constraints": [
    "Tyrannosaurus remains behind prey",
    "prey turns toward river margin",
    "no contact occurs"
  ]
}
```

The video model doesn't get to invent:

> T. rex catches it.

if the simulation says it escaped.

---

# 37. Asset architecture

Every reconstruction should have visual assets.

```text
EntityAsset
EnvironmentAsset
BehaviorAsset
```

Versioned:

```text
TREX_VISUAL_R17
HELL_CREEK_VISUAL_R04
```

Possible assets:

```text
scientific reconstruction image
neutral turnaround
scale reference
texture reference
color assumptions
environment reference
movement reference
```

Then LTX gets consistent conditioning.

---

# 38. Provenance through media

Every factual sentence in an episode should map backwards.

```text
NarrativeClaim
↓
ReconstructionAssertion
↓
TraitAssertion
↓
Claim
↓
Source
```

This allows a website panel:

```text
WHY WE THINK THIS
```

for any statement.

Example:

> “This animal probably weighed about 7 tonnes.”

Click:

```text
3 supporting studies
1 competing estimate
reconstruction method
uncertainty range
```

That is a serious moat.

---

# 39. Corrections

If new research changes an assertion:

```text
TraitAssertion_R17
↓ superseded
TraitAssertion_R18
```

Find:

```text
affected reconstructions
affected simulations
affected episodes
```

Then flag:

```text
OUTDATED RECONSTRUCTION
```

Potentially regenerate.

This turns the content archive into a living scientific model.

---

# 40. MVP scope

The factual MVP should be **small but complete**.

## Dataset

Start with:

```text
100 iconic prehistoric taxa
```

spread across:

```text
Cambrian
Devonian
Permian
Triassic
Jurassic
Cretaceous
Pleistocene
```

For each:

```text
canonical identity
taxonomy
age range
occurrences
geography
basic ecology
basic morphology
key sources
crosswalk IDs
```

---

# 41. MVP environments

Build ~20 environment reconstructions.

Examples:

```text
Burgess Shale-type Cambrian marine
Devonian reef
Permian floodplain
Triassic river system
Morrison Formation floodplain
Hell Creek
Kem Kem
Western Interior Seaway
Pleistocene steppe
La Brea-type ecosystem
```

Each stores:

```text
time interval
location
climate assumptions
terrain
vegetation
water
known taxa
source basis
```

---

# 42. MVP behavior/capability layer

Start simple.

For each taxon:

```text
size
mass
speed class
turn class
stamina class
attack reach
defence
sensory radius
diet
sociality confidence
habitat preference
```

Not ultra-detailed biomechanics yet.

Use uncertainty ranges.

---

# 43. MVP scenario templates

Build ~20 templates:

```text
predator encounters prey
ambush
open chase
resource competition
territorial encounter
scavenging contest
group defence
juvenile survival
water crossing
heat stress
migration
ecosystem sampling
```

Then combine automatically.

---

# 44. MVP output goal

The critical MVP test is not:

> Can we make one cool T. rex video?

It is:

> Can the graph autonomously generate 100 scientifically defensible, genuinely interesting episode candidates?

And then:

> Can we simulate and produce 10 of them end-to-end without manually rebuilding the pipeline each time?

That proves the architecture.

---

# 45. Suggested MVP technical stack

## Python

Use for:

```text
API ingestion
normalization
scientific modelling
simulation
analytics
scenario generation
```

## PostgreSQL + PostGIS

Canonical world state.

## DuckDB + Parquet

Large:

```text
occurrence joins
simulation outputs
Monte Carlo analytics
```

## Polars

Fast transformation.

## NetworkX initially

For graph analysis.

No need for Neo4j.

## FastAPI

Expose internal API.

## TypeScript/Next.js

Dashboard later.

## R2/S3

Assets and simulation bundles.

---

# 46. Monorepo

```text
evidence-world/
│
├── core/
│   ├── ids/
│   ├── entities/
│   ├── relations/
│   ├── environments/
│   ├── scenarios/
│   ├── simulation/
│   ├── events/
│   └── versioning/
│
├── evidence/
│   ├── sources/
│   ├── claims/
│   ├── assertions/
│   ├── provenance/
│   ├── uncertainty/
│   └── reconstructions/
│
├── ingest/
│   ├── pbdb/
│   ├── macrostrat/
│   ├── gbif/
│   ├── obis/
│   ├── globi/
│   ├── eol/
│   ├── opentree/
│   └── openalex/
│
├── domains/
│   ├── paleo/
│   ├── marine/
│   ├── ecology/
│   ├── evolution/
│   └── exoplanets/
│
├── discovery/
│   ├── historical_overlap/
│   ├── interaction_candidates/
│   ├── novelty/
│   └── scoring/
│
├── simulations/
│   ├── encounter/
│   ├── predation/
│   ├── survival/
│   ├── ecology/
│   └── evolution/
│
├── narrative/
│   ├── evidence_pack/
│   ├── significance/
│   ├── story/
│   └── citations/
│
├── media/
│   ├── assets/
│   ├── shots/
│   ├── ltx/
│   ├── qa/
│   └── assembly/
│
└── channels/
    ├── lost-worlds/
    ├── prehistoric-matchups/
    ├── ancient-oceans/
    ├── deep-blue/
    ├── tree-of-life/
    ├── living-planet/
    └── extinction/
```

---

# 47. Core database tables

```text
entities
taxa
taxon_names
taxon_crosswalks

time_intervals
locations
paleolocations
occurrences

sources
claims

traits
trait_assertions

relations
relation_assertions

environments
environment_assertions

reconstructions
reconstruction_parameters

scenario_templates
scenarios

simulation_models
simulation_runs
simulation_events

story_candidates
stories
narrative_claims

assets
shots
episodes

content_history
performance_metrics
```

---

# 48. Example canonical flow

Suppose we want:

> Could Deinonychus hunt Tenontosaurus?

The system does:

```text
Deinonychus
↓
PBDB occurrences

Tenontosaurus
↓
PBDB occurrences

compare age/geography
↓
historical overlap = true

retrieve environment
↓
Cloverly context

retrieve traits/literature
↓
mass
speed
attack anatomy
group behavior uncertainty

create reconstructions
↓
DEINONYCHUS_R08
TENONTOSAURUS_R05

create scenario
↓
HISTORICAL_PREDATION

run 10,000 simulations
↓
outcome distribution

detect crux
↓
group coordination assumption dominates outcome

story
↓
"Everything depends on whether Deinonychus hunted cooperatively"

shots
↓
LTX
```

That's a real episode generated from the graph.

---

# 49. Deep Blue example

Question:

> What is the predator structure below 3,000m in the North Pacific?

Pipeline:

```text
OBIS
↓
occurrence filter:
depth > 3000m
North Pacific

taxa
↓
TraitBank / literature

GloBI
↓
known feeding edges

build local ecosystem graph
↓
identify likely predator hubs

uncertainty analysis
↓
missing interaction data flagged

episode candidates
↓
"The predators of the abyss"
```

No simulation may even be necessary initially.

Some channel episodes can be pure graph reconstruction.

---

# 50. Not every story needs a simulator

This is another important point.

The shared pipeline should support:

```text
DATA STORY
GRAPH STORY
SIMULATION STORY
TIMELINE STORY
COMPARISON STORY
```

Examples:

### Data story

> The deepest recorded animals in OBIS.

### Graph story

> Reconstructing a hydrothermal food web.

### Simulation story

> Could this predator catch this prey?

### Timeline story

> How whales returned to the ocean.

### Comparison

> Why two similarly sized predators evolved differently.

Same media pipeline.

Different evidence operators.

---

# 51. The editorial engine

The engine should continuously search for content opportunities.

```text
DiscoveryJob
```

could run daily.

Generate:

```text
candidate_id
channel
question
entities
evidence_strength
novelty
visual_interest
uncertainty
simulation_needed
estimated_asset_cost
content_score
```

Rank.

Eventually include performance feedback:

```text
historical CTR
retention
topic saturation
audience interest
```

But never let audience performance alter scientific truth.

It only affects editorial selection.

---

# 52. The content flywheel

```text
DATA INGEST
↓
GRAPH IMPROVES
↓
MORE SCENARIOS
↓
MORE CONTENT
↓
AUDIENCE DATA
↓
BETTER EDITORIAL SCORING
↓
MORE ASSETS
↓
CHEAPER FUTURE CONTENT
↓
MORE CONTENT
```

And scientific assets compound too.

After making five Hell Creek videos:

```text
Hell Creek environment exists
T. rex asset exists
Triceratops exists
Edmontosaurus exists
vegetation refs exist
camera/style grammar exists
```

Episode six is dramatically cheaper.

---

# 53. The real moat

The APIs are not the moat.

Anyone can hit PBDB or OBIS.

The moat is:

```text
NORMALIZED IDS
×
CLAIM PROVENANCE
×
RECONSTRUCTION HISTORY
×
SIMULATION MODELS
×
SCENARIO LIBRARY
×
EVENT HISTORY
×
CANONICAL ASSET LIBRARY
×
EDITORIAL PERFORMANCE DATA
```

The multiplication matters.

A competitor can copy:

```text
PBDB data
```

but not quickly replicate:

```text
1000 curated reconstructions
+
millions of simulation runs
+
validated interactions
+
versioned visual assets
+
episode history
+
known audience response
```

---

# 54. Relationship to RoboBladez

This is why building both simultaneously is interesting.

RoboBladez teaches us:

```text
determinism
simulation
event logs
persistent history
scenario selection
story compilation
LTX production
```

Evidence World teaches us:

```text
provenance
uncertainty
reconstruction
scientific claims
cross-database identity
source versioning
```

Then the shared infrastructure becomes unusually powerful.

```text
                   GENERIC ENGINE

ENTITY
MODEL
ENVIRONMENT
RELATION
SCENARIO
SIMULATION
EVENT
STORY
SHOT
ASSET
```

with extensions:

```text
SyntheticWorld:
    Policy
    AgentHistory

EvidenceWorld:
    Source
    Claim
    Assertion
    Reconstruction
```

---

# 55. The first real build order

I would execute this:

```text
1. canonical Entity + ID crosswalk
2. Source / Claim / Assertion schemas
3. PBDB ingest
4. Macrostrat ingest
5. OpenTree crosswalk
6. 100-taxon paleo seed corpus
7. 20 environment reconstructions
8. Trait/reconstruction schema
9. Historical overlap query
10. ScenarioDiscovery
11. 20 scenario templates
12. simple utility-AI simulation
13. Monte Carlo runner
14. significance detector
15. story compiler
16. provenance-aware narrative claims
17. shot compiler
18. first 10 factual videos
```

Then:

```text
19. OBIS ingest
20. GBIF ingest
21. GloBI ingest
22. TraitBank
23. Deep Blue discovery engine
24. ecological graph stories
25. first Deep Blue series
```

Then:

```text
26. lineage/evolution stories
27. extinction event model
28. asset reuse optimizer
29. automatic daily editorial discovery
```

---

# 56. MVP success criteria

The first Evidence World MVP passes only if it can do these things:

### Data

```text
100 taxa normalized
cross-source IDs attached
occurrences/time/location queryable
sources retained
```

### Reconstruction

```text
every simulation parameter has provenance/status
uncertainty distributions supported
versions immutable
```

### Discovery

```text
generate ≥100 useful candidate stories
without manually typing the topics
```

### Simulation

```text
run ≥1,000 seeded simulations/scenario
reproduce a selected run
report distributions rather than one winner
```

### Narrative

```text
story never silently converts model assumptions into facts
citations resolvable back to assertions
```

### Media

```text
same reconstructed entity remains visually consistent
shot order respects canonical events
```

### Production

```text
10 materially different episodes
generated through the same pipeline
```

If those pass, this isn't just a YouTube automation script.

It is the beginning of a **general evidence-constrained world reconstruction and media engine**.

And the strongest long-term positioning is probably:

> **RoboBladez creates worlds that never existed. Evidence World reconstructs worlds that did. The same engine discovers what happens inside both, and turns those events into stories.**
