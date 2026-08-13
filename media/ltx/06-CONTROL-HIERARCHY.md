# Control hierarchy — use the least generative route that solves the shot

Ranked from loose to constrained:

1. Text-to-video
2. Image-to-video
3. First/last frame or keyframe interpolation
4. Reference-video / motion tracking IC-LoRA
5. Depth / pose / edge IC-LoRA
6. Retake a failed section
7. V2V / custom IC-LoRA
8. Fine-tuned LoRA / domain LoRA

## Practical rule

If a shot encodes a canonical event, increase control as event specificity increases.

### Loose establishing shot
T2V is fine.

### Recognizable recurring competitor/species
I2V with canonical reference.

### Exact transition
first/last frame or keyframe interpolation.

### Exact trajectory/pose/motion
motion/depth/pose/edge IC-LoRA.

### 2 seconds wrong in an otherwise good shot
Retake, not full regeneration.

## Why this matters

Prompting should not carry constraints that a reference/control signal can express more reliably.
