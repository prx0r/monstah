# Feature Matrix — LTX-2.3 production capabilities

## Use now

| Capability | Best interface | Why |
|---|---|---|
| Text-to-video | API / ComfyUI / pipelines | Pure shot synthesis |
| Image-to-video | API / ComfyUI / pipelines | Strongest route for character/asset consistency |
| First + last frame interpolation | LTX-2.3 API / keyframe pipeline | Great for state-to-state transitions |
| Keyframe interpolation | `ltx-pipelines` | Constrain start/end or multiple state anchors |
| Synchronized audio+video | native model/API | Foley, ambience, dialogue in one pass |
| Audio-to-video | Pro/API; trainer supports A2V | Music/dialogue-driven motion |
| Video-to-audio | trainer / pipeline family | Generate/learn foley from visuals |
| Retake | Pro/API | Surgical regeneration of a time range |
| Extend | Pro/API / trained extension mode | Continue shots forward/backward |
| IC-LoRA V2V | ComfyUI / trainer | Depth, pose, edges, motion tracking, transformation |
| LipDub IC-LoRA | ComfyUI | Replace spoken dialogue while retaining video |
| HDR IC-LoRA | ComfyUI examples | HDR-style transformation/control |
| Pixel spatial upscaler IC-LoRA | ComfyUI | Generative 2×/4× detail synthesis |
| Latent spatial upscaler | two-stage pipeline | Draft low-res, upscale only winning takes |
| Temporal upscaler | ComfyUI two-stage | Increase temporal resolution in two-stage path |
| Standard LoRA | trainer | Style/character/domain specialization |
| Full fine-tuning | trainer | Expensive; only after LoRA proves insufficient |
| Video inpainting/outpainting | trainer modes | Specialized learned repair/extension |
| Audio inpainting/extension | trainer modes | Specialized audio control |

## Best architectural interpretation

Treat LTX as a **renderer**, not a truth engine.

Your software should provide:
- canonical subjects
- canonical state before shot
- canonical state after shot
- event to dramatize
- environment
- camera grammar
- audio intent
- hard constraints
- optional reference frames/control video

LTX returns:
- candidate media

A QA layer then determines whether that candidate respects the canonical shot spec.
