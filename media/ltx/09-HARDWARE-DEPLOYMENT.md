# Hardware / deployment strategy

## Official current signals

### ComfyUI custom workflow repo
- 32GB+ VRAM
- 100GB+ disk

### Official trainer
- 80GB recommended
- 32GB low-VRAM config

### LTX Desktop
- local generation support can start lower on supported systems than the full custom workflow path
- API mode exists for unsupported hardware

## Recommended project architecture

```text
CPU ORCHESTRATOR
    |
    +-- ShotSpec JSON
    |
GPU RENDER WORKER
    |
    +-- LTX ComfyUI or local pipelines
    |
OBJECT STORAGE
    |
QA / EDITOR
```

Never require the simulation/world engine machine to have a GPU.

## Batch strategy

1. compile 20–100 shot specs on CPU
2. render drafts
3. score/QA
4. final-render only accepted seeds
5. Retake only failed intervals
6. upload artifacts
7. terminate rented GPU

## Cache
Persistent volume should hold:
- checkpoints
- Gemma encoder/components
- upscalers
- LoRAs
- ComfyUI custom nodes
- workflow JSON
