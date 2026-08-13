# Local Python / CLI / API Guide

## Official local packages

```bash
git clone https://github.com/Lightricks/LTX-2
cd LTX-2
uv sync --frozen
source .venv/bin/activate
```

Packages:
- `ltx-core`
- `ltx-pipelines`
- `ltx-trainer`

Pipelines documented in the official repo include:
- TI2VidOneStagePipeline
- TI2VidTwoStagesPipeline
- DistilledPipeline
- ICLoraPipeline
- KeyframeInterpolationPipeline
- additional video/audio/retake paths in `ltx-pipelines`

## API production pattern

For interactive tests:
- synchronous v1 endpoints

For batch production:
- asynchronous v2 endpoints
- submit -> store job id -> poll -> download -> QA

Current API model names:
- `ltx-2-3-fast`
- `ltx-2-3-pro`

Do not build against deprecated:
- `ltx-2-fast`
- `ltx-2-pro`

## Renderer adapter

Your core projects should call an interface like:

```python
class VideoRenderer:
    def submit(self, shot_spec) -> RenderJob: ...
    def status(self, job_id) -> RenderStatus: ...
    def fetch(self, job_id) -> RenderArtifact: ...
```

Implementations:
- `LTXApiRenderer`
- `LTXComfyRenderer`
- `LTXLocalPipelineRenderer`

The application should not know which one generated the clip.
