# Monstah -> LTX production mapping

LTX must never decide scientific truth.

```text
EVIDENCE
→ RECONSTRUCTION VERSION
→ SCENARIO / EVENT
→ SHOT SPEC
→ LTX
→ EPISTEMIC + VISUAL QA
```

## Shot classes

### 1. Environment reconstruction
Use:
- environment reference image
- I2V
- restrained motion
- no unsupported species interactions

### 2. Animal hero shot
Use:
- versioned canonical reconstruction image
- I2V
- simple species-appropriate motion

### 3. Historical interaction
Use:
- only after temporal/spatial/environment validity
- exact scenario event
- controls/keyframes for critical actions

### 4. Counterfactual Lab Mode
Same workflow, but public metadata must retain:
`COUNTERFACTUAL`

### 5. Deep Blue data story
Many shots do not need simulation:
- occurrence maps
- depth transitions
- environmental plates
- animal reconstruction shots
- food-web graphics

## Example prompt

```text
A wide underwater documentary shot follows a single versioned marine-animal reconstruction moving slowly across a dark abyssal plain. The animal keeps the same body proportions and markings as the reference image, swimming from left to right with restrained tail motion. Fine suspended particles drift through the cold water while the seabed remains distant and sparsely textured. The camera tracks parallel at a respectful distance with no sudden zoom. A narrow cool light from above fades rapidly into darkness. Audio: low underwater ambience, subtle distant water movement, no music and no invented animal vocalization.
```

Any uncertain biological behavior should be tagged in the ShotSpec rather than hidden in prose.
