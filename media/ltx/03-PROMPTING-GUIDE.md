# Prompting Guide — practical LTX grammar

Official guidance converges on one principle:

> Write chronologically like a cinematographer describing one shot, not as a bag of image keywords.

## Core order

1. Main action
2. Secondary motion / gestures
3. Subject appearance
4. Environment
5. Camera position + camera movement
6. Lighting / texture / palette
7. Audio in chronological context
8. End state / sudden change

## Recommended template

```text
[SHOT SCALE + MAIN ACTION]. [SUBJECT] is [CONCRETE MOTION] while [SECONDARY MOTION].
The scene is [ENVIRONMENT WITH MATERIALS / WEATHER / DEPTH].
The camera [RELATIONSHIP TO SUBJECT + MOVEMENT], ending with [FINAL COMPOSITION].
Lighting is [SOURCE + DIRECTION + QUALITY], with [COLOR / TEXTURE].
Audio: [AMBIENCE], then [SFX synchronized with event], while [music/dialogue if required].
By the end of the shot, [explicit end state].
```

## Rules that matter

- Use present-tense action.
- One shot = one dominant action.
- Describe time ordering explicitly: `as`, `then`, `while`, `after`.
- Camera motion should be described relative to the subject.
- Physical acting cues usually work better than abstract emotion labels.
- Avoid contradictory camera moves.
- Avoid asking for many unrelated events in a 6–10 second shot.
- Avoid relying on readable text/logos.
- Avoid chaotic/complex physics when a constrained reference/control route can be used.
- For recurring characters/objects, prefer I2V/keyframes/IC-LoRA over repeatedly re-describing them from text.
- Keep seed fixed while testing prompt changes when possible.

## Dialogue

Use short quoted phrases with acting/motion direction around them.

Better:
```text
He turns toward the camera, shoulders still, and says quietly, "We misread the opening."
```

Avoid long speeches in a single short shot.

## Audio

Write audio into the chronology, not as a detached list:

```text
A low arena hum fills the space. As the impact occurs, a sharp metallic strike cuts through the ambience; the crowd reacts a beat later.
```

## Negative-control philosophy

LTX's official guidance favors positive, explicit scene direction. When a workflow exposes negatives, reserve them for recurring failure modes rather than trying to encode the whole shot negatively.
