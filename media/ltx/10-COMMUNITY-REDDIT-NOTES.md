# Community / Reddit advice — treat as anecdotal

Community observations are useful for workflow heuristics, but not authoritative model documentation.

## Recurring useful pattern: two-pass generation

A July 2026 Reddit thread on LTX-2.3 upscaling emphasizes that the LTX spatial upscaler is meant to participate in a two-pass generation workflow rather than being treated like a generic post-render scaler.

This lines up with the official LTX workflow guide:
- generate low-resolution base
- judge composition/motion
- upscale the accepted base via the model's spatial pipeline

Practical takeaway:
**Do not waste final-resolution compute before the motion/composition is approved.**

## Finished-video LoRA warning

Community advice also warns that applying style independently frame-by-frame after render is likely to create temporal flicker/boiling.

Practical takeaway:
- use LoRA during generation, or
- use V2V/IC-LoRA with temporal conditioning,
not per-frame still-image processing.

## Community feature requests / pain points

Hugging Face discussions around 2.3 mention:
- documentation/examples being hard to discover
- object permanence / high-motion artifacts as areas users care about
- interest in future 2.5 architecture

Treat those as motivation for:
- smaller shots
- stronger reference conditioning
- explicit end states
- QA/Retake
rather than assuming future model improvements.
