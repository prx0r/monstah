# ComfyUI Production Guide

## Official requirements for the Lightricks custom workflow repository

The official ComfyUI-LTXVideo README currently recommends:
- CUDA-compatible GPU
- 32GB+ VRAM
- 100GB+ free disk

Official LTX Desktop supports a different lower-memory local path on supported hardware; do not assume that means the full custom-node workflow has the same memory envelope.

## Install

```bash
git clone https://github.com/comfyanonymous/ComfyUI
# install ComfyUI normally

# In ComfyUI:
# Manager -> Install Custom Nodes -> search "LTXVideo"
```

Official custom nodes:
https://github.com/Lightricks/ComfyUI-LTXVideo

## Start with these official workflow classes

1. Text/image -> video full/distilled single stage
2. Text/image -> video distilled two stage
3. IC-LoRA depth + human pose + edges
4. IC-LoRA I2V motion tracking
5. IC-LoRA HDR
6. IC-LoRA LipDub two stage
7. IC-LoRA pixel spatial upscaling
8. Text-to-audio

## Production recommendation

Use two tiers:

### DRAFT
- distilled / fast
- low base resolution
- no expensive final upscale
- many seeds

### FINAL
- winning seed
- stronger/full/pro path
- two-stage spatial/temporal upscale
- QA and retake only failed shot intervals

This is much cheaper than rendering every candidate at final quality.

## Low-VRAM official advice

The custom-node repo includes low-VRAM loader nodes and recommends using ComfyUI `--reserve-vram`, e.g.:

```bash
python -m main --reserve-vram 5
```

Treat this as an optimization around the official 32GB workflow target, not proof that every workflow fits on much smaller cards.
