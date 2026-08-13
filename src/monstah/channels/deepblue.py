"""Deep Blue theme: modern ocean data-led reconstruction (DEEP BLUE).

Evidence adapter: OBIS (marine occurrences) for identity/ecology, plus Open5e
statblocks for combat. Open5e ships real marine combatants (Sperm Whale, Giant
Squid, Great White Shark...), so the shared battle engine works unchanged —
an ocean matchup is the same code path as a prehistoric one.
"""

from __future__ import annotations

from ..core.models import Environment, Reference
from ..discovery import Taxon
from ..ingest.obis import ObisClient
from ..ingest.open5e import Open5eClient
from .base import ChannelManifest, EvidenceAdapter

# name -> open5e slug for marine combatants
MARINE_STATBLOCKS = {
    "Sperm Whale": "sperm-whale",
    "Giant Squid": "giant-squid",
    "Great White Shark": "great-white-shark",
    "Killer Whale": "killer-whale",
    "Megalodon": "megalodon",
    "Mosasaurus": "mosasaurus",
    "Leviathan": "leviathan",
}


class DeepBlueAdapter(EvidenceAdapter):
    def __init__(self, *, cache_dir: str | None = None) -> None:
        self.obis = ObisClient(cache_dir=cache_dir)
        self.open5e = Open5eClient(cache_dir=cache_dir)

    def load_taxa(self, limit: int = 20) -> list[Taxon]:
        # start from known marine combatants + a couple of OBIS-driven taxa
        names = list(MARINE_STATBLOCKS.keys())[:limit]
        out: list[Taxon] = []
        for name in names:
            out.append(
                Taxon(
                    ref=Reference(namespace="marine", key=name.lower().replace(" ", "-")),
                    name=name,
                    min_ma=0.0,
                    max_ma=0.0,
                    env={"sea", "deep"},
                    diet="carnivore",
                    traits={"depth": 3000, "region": "global"},
                )
            )
        return out

    def taxon_for_combat(self, name: str) -> dict:
        from ..simulations import Combatant

        slug = MARINE_STATBLOCKS.get(name)
        if slug:
            try:
                mon = self.open5e.monster(slug)
                if mon:
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
        return {"armor_class": 13, "hit_points": 100, "attack_bonus": 10, "damage_dice": "3d10+6", "speed": 10.0}

    def environments(self) -> list[Environment]:
        return [
            Environment(
                kind="ocean",
                name="Abyssal Plain",
                region="global",
                constraints={"depth_m": 4000, "pressure_atm": 400, "light": "aphotic"},
            ),
            Environment(
                kind="ocean",
                name="Hydrothermal Vent Field",
                region="global",
                constraints={"depth_m": 2500, "temperature_c": 4, "chemosynthesis": True},
            ),
        ]


def deepblue_channel(*, n_runs: int = 1000) -> "Channel":
    from .base import Channel, ChannelManifest

    manifest = ChannelManifest(
        name="deep-blue",
        title="Deep Blue",
        description="Data-led modern ocean reconstruction via OBIS + Open5e",
    )
    return Channel(manifest, DeepBlueAdapter(), mode="historical", n_runs=n_runs)
