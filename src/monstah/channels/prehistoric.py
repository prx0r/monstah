"""Prehistoric theme: extinct-world reconstruction (LOST WORLDS / MATCHUPS).

Evidence adapter: 100-taxon paleo seed corpus for identity/ecology, plus
Open5e statblocks to power the shared d20 battle engine (T. rex, Triceratops,
Ankylosaurus all exist as real statblocks). If a taxon has no statblock, we
derive one from its size/mass.
"""

from __future__ import annotations

from typing import Any

from ..core.models import Environment, Reference
from ..discovery import Taxon
from ..domains.paleo.seed import SEED_TAXA, seed_environments
from ..ingest.open5e import Open5eClient
from .base import ChannelManifest, EvidenceAdapter

# name -> open5e slug where a real statblock exists
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
    def __init__(self, *, cache_dir: str | None = None, derived: bool = True) -> None:
        self.open5e = Open5eClient(cache_dir=cache_dir)
        self.derived = derived

    def load_taxa(self, limit: int = 50) -> list[Taxon]:
        out: list[Taxon] = []
        for s in SEED_TAXA[:limit]:
            lo, hi = s.age_range()
            out.append(
                Taxon(
                    ref=Reference(namespace="paleo", key=s.name.lower().replace(" ", "-")),
                    name=s.name,
                    min_ma=lo,
                    max_ma=hi,
                    env=set(s.env),
                    diet=s.diet,
                    traits={
                        "mass_kg": s.traits.get("mass_kg", 2000.0),
                        "era": s.era,
                        "region": s.region,
                    },
                )
            )
        return out

    def taxon_for_combat(self, name: str) -> dict:
        """Resolve combat stats: real Open5e statblock if available, else derive."""
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
        if self.derived:
            return _derive_combat(name)
        return {"armor_class": 12, "hit_points": 50, "attack_bonus": 5, "damage_dice": "2d6+3", "speed": 8.0}

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


def _derive_combat(name: str) -> dict:
    """Fallback combat stats from a name heuristic (size hint)."""
    low = name.lower()
    if any(k in low for k in ("tyranno", "megalodon", "mosa", "gigano")):
        return {"armor_class": 14, "hit_points": 120, "attack_bonus": 11, "damage_dice": "4d12+7", "speed": 10.0}
    if any(k in low for k in ("triceratops", "ankylosaurus", "stego", "brachio", "diplo", "apat")):
        return {"armor_class": 16, "hit_points": 95, "attack_bonus": 9, "damage_dice": "3d8+6", "speed": 8.0}
    return {"armor_class": 12, "hit_points": 60, "attack_bonus": 7, "damage_dice": "2d8+4", "speed": 9.0}


def prehistoric_channel(*, n_runs: int = 1000) -> "Channel":
    from .base import Channel, ChannelManifest

    manifest = ChannelManifest(
        name="prehistoric",
        title="Prehistoric Worlds",
        description="Extinct-world reconstruction via PBDB/Macrostrat/Open5e statblocks",
    )
    return Channel(manifest, PrehistoricAdapter(), mode="historical", n_runs=n_runs)
