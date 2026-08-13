# Renderer-agnostic integration

Do not build either project around ComfyUI nodes, LTX API field names, or a specific checkpoint.

Canonical software objects:

```text
ShotSpec
RenderRequest
RenderJob
RenderArtifact
QAVerdict
```

Backend maps `ShotSpec` into:
- LTX API
- ComfyUI workflow JSON
- local `ltx-pipelines`
- future LTX-2.5
- even a non-LTX renderer later

## RenderRequest

```json
{
  "shot_spec_uri": "...",
  "renderer": {
    "family": "ltx",
    "version": "2.3",
    "profile": "draft"
  }
}
```

Profiles:

```text
draft
final
retake
control-heavy
audio-driven
```

The world/game projects should never parse model-specific output beyond the `RenderArtifact` contract.
