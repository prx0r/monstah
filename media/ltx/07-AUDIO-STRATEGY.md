# Audio strategy

LTX-2.3 is a joint audio/video model, so sound can be part of shot generation.

Use native joint generation for:
- ambience
- environmental foley
- impacts
- crowd/arena atmosphere
- water/deep-sea ambience
- short dialogue

Use audio-to-video for:
- pre-authored narration fragments
- rhythm-driven montage
- dialogue-driven facial/body motion
- music-synchronized shots

Use separate post audio when:
- exact narration wording/timing matters
- canonical commentary must be preserved
- voice identity must remain highly consistent
- mixing needs to span many shots

Recommended hybrid:
```text
LTX shot audio = ambience + foley + local effects
final editor = narration + score + global mix
```

This prevents each generated shot from independently inventing incompatible music or narration.
