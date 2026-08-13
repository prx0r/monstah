"""Provider-neutral reconstruction image backend (MVP Phase 5).

`ReconstructionImageBackend.generate(spec, references, view)` is the contract.
For the MVP, `LocalSpecBackend` produces deterministic, offline ImageCandidates
by composing the approved reference pack (the visual moat) — no GPU/API needed.
A remote backend (e.g. an image API) can be swapped in.
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ..media.asset import AssetCandidate, AssetRole, EpistemicStatus
from .reference_pack import ReferencePack
from .visual_spec import VisualReconstructionSpec


@dataclass
class ViewSpec:
    name: str = "lateral"
    camera: str = "level"
    framing: str = "full body"


@dataclass
class ImageCandidate:
    """A candidate generated reconstruction image (one view)."""

    id: str = ""
    entity_id: str = ""
    reconstruction_id: str = ""
    view: str = ""
    uri: str = ""
    data: bytes | None = None
    role: AssetRole = AssetRole.CANONICAL_RECONSTRUCTION
    epistemic_status: EpistemicStatus = EpistemicStatus.GENERATED_RECONSTRUCTION
    generator: str = ""
    generator_manifest: dict[str, Any] = field(default_factory=dict)

    def sha256(self) -> str:
        blob = self.data if self.data is not None else (self.uri or "").encode()
        return hashlib.sha256(blob if isinstance(blob, bytes) else blob.encode()).hexdigest()


class ReconstructionImageBackend(ABC):
    """Contract: turn a spec + approved references into view candidates."""

    @abstractmethod
    def generate(
        self,
        spec: VisualReconstructionSpec,
        references: ReferencePack,
        view: ViewSpec,
    ) -> list[ImageCandidate]:
        ...


class LocalSpecBackend(ReconstructionImageBackend):
    """Offline backend: composes the approved reference pack into a view bundle.

    Deterministic and GPU-free; the "rendered" candidate carries the reference
    URIs + the machine-readable spec as its generator manifest. A future remote
    backend produces actual pixels; this proves the dataflow and the moat.
    """

    generator = "local-spec"

    def generate(
        self,
        spec: VisualReconstructionSpec,
        references: ReferencePack,
        view: ViewSpec,
    ) -> list[ImageCandidate]:
        # for each matching reference, emit a candidate bound to the spec
        refs = [c for c in references.selected if view.name in (c.view or "") or not c.view]
        if not refs:
            refs = references.selected[:1]
        out: list[ImageCandidate] = []
        for i, ref in enumerate(refs):
            out.append(
                ImageCandidate(
                    id=f"{spec.reconstruction_id}:{view.name}:{i}",
                    entity_id=spec.entity_id,
                    reconstruction_id=spec.reconstruction_id,
                    view=view.name,
                    uri=ref.original_uri,
                    generator=self.generator,
                    generator_manifest={
                        "spec": {
                            "entity_id": spec.entity_id,
                            "reconstruction_id": spec.reconstruction_id,
                            "morphology": spec.morphology,
                            "dimensions": spec.dimensions,
                            "required_views": spec.required_views,
                            "forbidden": spec.forbidden,
                        },
                        "reference_pack_id": references.digest,
                        "view": {"name": view.name, "camera": view.camera, "framing": view.framing},
                    },
                )
            )
        return out
