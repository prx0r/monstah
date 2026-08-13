# RoboBladez -> LTX production mapping

LTX must be downstream of canonical simulation.

```text
MATCH REPLAY
→ EVENT SELECTION
→ SHOT SPEC
→ CONTROL ASSETS
→ LTX
→ VISION/LOGIC QA
→ EPISODE
```

## Shot classes

### 1. Establishing arena shot
Use:
- T2V or canonical arena I2V
- wide/simple motion

### 2. Competitor intro
Use:
- canonical character/talisman reference
- I2V
- consistent portrait/turnaround refs

### 3. Exact battle event
Use:
- selected replay event
- pre-render trajectory/depth/pose/motion guide
- IC-LoRA where possible
- explicit start/end states

### 4. Daimon manifestation
Use:
- canonical identity refs
- I2V/keyframes
- more generative styling is acceptable because manifestation is narrative projection
- still preserve actor/body identity

### 5. Replay analysis
Do not rely on LTX for truth.
Use:
- deterministic overlays
- diagrams
- replay renderer
- generated footage only as dramatization

## Example prompt

```text
A low tracking shot follows the two fictional spinning-top competitors as they circle across the illuminated virtual arena. Boris's black-and-silver talisman holds the inner line while Morty's brighter talisman cuts inward from the outer ring. The camera stays just above arena height and pans smoothly with Boris, preserving both competitors in frame. At the canonical collision point they strike once, separate immediately, and Boris remains closer to the center while Morty is deflected outward. Cold overhead arena light reflects across the floor. Audio: a rising mechanical hum, one sharp synthetic impact synchronized exactly with contact, then the arena ambience returns.
```

Note: visuals remain fictional/virtual; canonical outcome comes from the game engine.
