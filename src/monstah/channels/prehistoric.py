"""Prehistoric theme: extinct-world reconstruction (LOST WORLDS / MATCHUPS).

Evidence adapter: 100-taxon paleo seed corpus for identity/ecology, plus
Open5e statblocks as EXPLICITLY-LABELED game-proxy combat stats (never leaked
into scientific reconstruction state via the type firewall).
"""

from __future__ import annotations

from typing import Any

from ..core.models import Environment, Reference
from ..core.truth import Layer, Status, TypedValue
from ..discovery import Candidate, Taxon
from ..domains.paleo.seed import SEED_TAXA, seed_environments
from ..ingest.open5e import Open5eClient
from .base import EvidenceAdapter

STATBLOCK_SLUGS = {
    "Tyrannosaurus rex": "tyrannosaurus-rex",
    "Triceratops": "triceratops",
    "Ankylosaurus magniventris": "ankylosaurus",
    "Pteranodon": "pteranodon",
    "Velociraptor": "velociraptor",
    "Brachiosaurus altithorax": "brachiosaurus",
    "Stegosaurus stenops": "stegosaurus",
    "Spinosaurus aegyptiacus": "spinosaurus",
    "Compsognathus": "compsognathus",
    "Parasaurolophus": "parasaurolophus",
    "Allosaurus fragilis": "allosaurus",
    "Megaloceros giganteus": "giant-elk",
}


class PrehistoricAdapter(EvidenceAdapter):
    def __init__(self, *, cache_dir: str | None = None, offline: bool = False) -> None:
        self.open5e = None if offline else Open5eClient(cache_dir=cache_dir)
        self.offline = offline
        self._envs = {e["name"]: e for e in seed_environments()}

    def load_taxa(self, limit: int = 50) -> list[Taxon]:
        out: list[Taxon] = []
        for s in SEED_TAXA[:limit]:
            lo, hi = s.age_range()
            t = Taxon(
                ref=Reference(namespace="paleo", key=s.name.lower().replace(" ", "-")),
                name=s.name,
                min_ma=lo,
                max_ma=hi,
                env=set(s.env),
                diet=s.diet,
                region=s.region if s.region not in ("", "global") else "global",
            )
            # EVIDENCE: from the seed corpus (identity/ecology), not combat stats
            t.set_evidence("mass_kg", s.traits.get("mass_kg", 2000.0), unit="kg")
            t.set_evidence("era", s.era)
            # GAME PROXY: Open5e combat stats, explicitly labeled, separate layer
            proxy = self._combat_proxy(s.name)
            for k, v in proxy.items():
                t.set_game_proxy(k, v, status=Status.GAME_PROXY.value, source="open5e")
            out.append(t)
        return out

    def environments(self) -> list[Environment]:
        return [
            Environment(
                kind="paleoenvironment",
                name=e["name"],
                region=e.get("loc", ""),
                constraints={"era": e["era"], "min_ma": e["min_ma"], "max_ma": e["max_ma"], "terrain": e.get("terrain")},
            )
            for e in seed_environments()
        ]

    def environment_for_candidate(self, candidate: Candidate, taxa_by_ref: dict[str, Taxon]) -> Environment | None:
        """Bind a real paleoenvironment by matching the candidate's era."""
        t = taxa_by_ref.get(candidate.entities[0].key)
        if not t:
            return None
        era = t.facts.evidence.get("era")
        era = era.value if era else ""
        for env in self._envs.values():
            if env["era"] == era:
                return Environment(
                    kind="paleoenvironment",
                    name=env["name"],
                    region=env.get("loc", ""),
                    constraints={"era": env["era"], "min_ma": env["min_ma"], "max_ma": env["max_ma"]},
                )
        return None

    def _combat_proxy(self, name: str) -> dict:
        if self.offline or self.open5e is None:
            return _derive_combat(name)
        slug = STATBLOCK_SLUGS.get(name)
        if slug:
            try:
                mon = self.open5e.monster(slug)
                if mon:
                    from ..simulations import Combatant

                    cb = Combatant.from_open5e(mon)
                    return {
                        "armor_class": cb.armor_class,
                        "hit_points": cb.hit_points,
                        "attack_bonus": cb.attack_bonus,
                        "damage_dice": cb.damage_dice,
                        "speed": cb.speed,
                    }
            except Exception:
                pass
        return _derive_combat(name)


def _derive_combat(name: str) -> dict:
    low = name.lower()
    if any(k in low for k in ("tyranno", "megalodon", "mosa", "gigano")):
        return {"armor_class": 14, "hit_points": 120, "attack_bonus": 11, "damage_dice": "4d12+7", "speed": 10.0}
    if any(k in low for k in ("triceratops", "ankylosaurus", "stego", "brachio", "diplo", "apat")):
        return {"armor_class": 16, "hit_points": 95, "attack_bonus": 9, "damage_dice": "3d8+6", "speed": 8.0}
    return {"armor_class": 12, "hit_points": 60, "attack_bonus": 7, "damage_dice": "2d8+4", "speed": 9.0}


def prehistoric_channel(*, n_runs: int = 1000, offline: bool = False) -> "Channel":
    from .base import Channel, ChannelManifest

    manifest = ChannelManifest(
        name="prehistoric",
        title="Prehistoric Worlds",
        description="Extinct-world reconstruction via PBDB/Macrostrat/Open5e statblocks",
    )
    return Channel(manifest, PrehistoricAdapter(offline=offline), mode="historical", n_runs=n_runs)
