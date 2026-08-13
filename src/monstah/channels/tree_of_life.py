"""Tree of Life theme: evolution via OpenTree phylogeny (TREE OF LIFE).

Content is phylogenetic: common ancestor, nearest relatives, clades. Uses
OpenTree to resolve names (TNRS) and query the synthesized tree, with Open5e
statblocks only as labeled game-proxy where a combat matchup is wanted.
"""

from __future__ import annotations

from typing import Any

from ..core.models import Environment, Reference
from ..core.truth import Status
from ..discovery import Candidate, Taxon
from ..ingest.opentree import OpenTreeClient
from ..narrative import EpisodeSpec
from ..media.shots import compile_shots
from .base import Channel, ChannelManifest, EvidenceAdapter

# (label, scientific name hint)
TAXA = [
    ("Tyrannosaurus rex", "Tyrannosaurus rex"),
    ("Chicken", "Gallus gallus"),
    ("Great White Shark", "Carcharodon carcharias"),
    ("Sperm Whale", "Physeter macrocephalus"),
    ("Hippopotamus", "Hippopotamus amphibius"),
    ("Bottlenose Dolphin", "Tursiops truncatus"),
]


class TreeOfLifeAdapter(EvidenceAdapter):
    def __init__(self, *, cache_dir: str | None = None, offline: bool = False) -> None:
        self.opentree = None if offline else OpenTreeClient(cache_dir=cache_dir)
        self.offline = offline

    def load_taxa(self, limit: int = 20) -> list[Taxon]:
        out: list[Taxon] = []
        for label, scientific in TAXA[:limit]:
            ott = None if self.offline else self._resolve(scientific)
            t = Taxon(
                ref=Reference(namespace="ott", key=str(ott) if ott else scientific.lower()),
                name=label, min_ma=0.0, max_ma=0.0, env={"terrestrial"}, diet="herbivore", region="global",
            )
            t.set_evidence("scientific_name", scientific)
            if ott:
                t.set_evidence("ott_id", ott, status=Status.OBSERVED.value, source="opentree")
            out.append(t)
        return out

    def _resolve(self, scientific: str) -> int | None:
        try:
            res = self.opentree.tnrs_match(scientific)
            results = res.get("results") or []
            if results:
                matches = results[0].get("matches") or []
                if matches:
                    return matches[0].get("taxon", {}).get("ott_id")
        except Exception:
            pass
        return None

    def environments(self) -> list[Environment]:
        return [Environment(kind="phylogeny", name="Tree of Life", region="global", constraints={})]


class TreeOfLifeChannel(Channel):
    """Produces phylogenetic graph stories (non-combat) using OpenTree MRCA."""

    def __init__(self, manifest: ChannelManifest, adapter: TreeOfLifeAdapter, **kw: Any) -> None:
        super().__init__(manifest, adapter, **kw)
        self._adapter = adapter

    def produce_graph(self, candidate: Candidate, taxa_by_ref: dict[str, Taxon], overlap=None):
        a = taxa_by_ref[candidate.entities[0].key]
        b = taxa_by_ref[candidate.entities[1].key]
        mrca = self._mrca(a, b)
        evidence = f"Common ancestor (OpenTree MRCA): {mrca or 'unknown'}."
        story = EpisodeSpec(
            title=f"Common ancestor of {a.name} and {b.name}",
            scenario_id=candidate.template, channel=self.theme,
            hook=f"What links {a.name} and {b.name}?",
            evidence=evidence,
            conclusion="Phylogenetic story from the Open Tree of Life; no battle simulation.",
        )
        out = super().produce_graph(candidate, taxa_by_ref, overlap)
        out.story = story
        return out

    def _mrca(self, a: Taxon, b: Taxon) -> str:
        a_ott = a.facts.evidence.get("ott_id")
        b_ott = b.facts.evidence.get("ott_id")
        if not a_ott or not b_ott or self._adapter.offline:
            return ""
        try:
            res = self._adapter.opentree.mrca([int(a_ott.value), int(b_ott.value)])
            tax = (res.get("mrca") or {}).get("taxon") or {}
            return f"{tax.get('name')} (ott:{tax.get('ott_id')})"
        except Exception:
            return ""


def tree_of_life_channel(*, n_runs: int = 1000, offline: bool = False) -> Channel:
    manifest = ChannelManifest(
        name="tree-of-life",
        title="Tree of Life",
        description="Evolution via OpenTree phylogeny (non-combat)",
    )
    return TreeOfLifeChannel(manifest, TreeOfLifeAdapter(offline=offline), mode="historical", n_runs=n_runs)
