# LoRA / IC-LoRA / Fine-tuning

## Official trainer hardware guidance

The current trainer documentation recommends:
- Linux + CUDA
- 80GB VRAM for standard configuration
- low-VRAM configuration for 32GB cards with INT8/memory optimizations

Do not train before the asset library proves repeated failure modes.

## Standard LoRA
Use for:
- stable visual style
- recurring subject/domain appearance
- specialized materials/lighting/aesthetics

## IC-LoRA
Use when you want a transformation/control mapping:
- depth -> target
- pose -> target
- edges -> target
- motion/reference -> target
- restoration
- colorization
- style transfer
- specialized V2V control

Training data is paired:
```text
reference_video -> target_video
caption
```

## Project-specific good future candidates

RoboBladez:
- arena-specific visual grammar LoRA
- talisman material/style LoRA
- motion/control IC-LoRA from canonical sim trajectories
- effect-specific IC-LoRAs only after enough examples exist

Monstah:
- scientific reconstruction visual style
- underwater/deep-sea lighting domain LoRA
- paleo-environment consistency LoRA
- pose/motion IC-LoRA from rigged/3D guide renders

## Avoid premature training

First exhaust:
- better reference frame
- first/last frame
- keyframes
- depth/pose/edge controls
- Retake
- better shot decomposition

Then train.
