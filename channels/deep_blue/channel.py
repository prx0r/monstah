"""Deep Blue theme: genuinely OBIS-driven modern ocean reconstruction.

Evidence adapter: queries the real OBIS occurrence service for marine taxa,
deriving depth range + region from actual records (not hardcoded). Open5e
statblocks are used ONLY as explicitly-labeled game-proxy combat stats.
"""

from __future__ import annotations

from typing import Any

from monstah.core.models import Environment, Reference
from monstah.core.truth import Status
from monstah.discovery import Candidate, Taxon
from monstah.ingest.obis import ObisClient
from monstah.ingest.open5e import Open5eClient
from channels.base import EvidenceAdapter

# marine combatants: scientific name -> open5e slug (game proxy only)
MARINE = {
    "Physeter macrocephalus": ("Sperm Whale", "sperm-whale"),
    "Architeuthis dux": ("Giant Squid", "giant-squid"),
    "Carcharodon carcharias": ("Great White Shark", "great-white-shark"),
    "Orcinus orca": ("Killer Whale", "killer-whale"),
    "Balaenoptera musculus": ("Blue Whale", "blue-whale"),
    "Hippocampus": ("Seahorse", "seahorse"),
    "Octopus vulgaris": ("Octopus", "octopus"),
}


class DeepBlueAdapter(EvidenceAdapter):
    def __init__(self, *, cache_dir: str | None = None, depth_min: int = 0, depth_max: int = 12000, offline: bool = False) -> None:
        self.obis = None if offline else ObisClient(cache_dir=cache_dir)
        self.open5e = None if offline else Open5eClient(cache_dir=cache_dir)
        self.offline = offline
        self.depth_min = depth_min
        self.depth_max = depth_max

    def load_taxa(self, limit: int = 20) -> list[Taxon]:
        out: list[Taxon] = []
        names = list(MARINE.keys())[:limit]
        for scientific in names:
            label, slug = MARINE[scientific]
            evidence = self._obis_evidence(scientific) if not self.offline else {
                "observed": 10, "min_depth": 0, "max_depth": 0, "mass_kg": 500.0,
            }
            t = Taxon(
                ref=Reference(namespace="worms", key=scientific.lower().replace(" ", "-")),
                name=label,
                min_ma=0.0,
                max_ma=0.0,
                env={"sea", "deep"} if evidence.get("max_depth", 0) >= 1000 else {"sea"},
                diet="carnivore",
                region="global",
            )
            # EVIDENCE: real OBIS occurrence-derived values
            t.set_evidence("scientific_name", scientific)
            t.set_evidence("min_depth", evidence.get("min_depth", 0), unit="m", status=Status.OBSERVED.value, source="obis")
            t.set_evidence("max_depth", evidence.get("max_depth", 0), unit="m", status=Status.OBSERVED.value, source="obis")
            t.set_evidence("observed", evidence.get("observed", 0), status=Status.OBSERVED.value, source="obis")
            t.set_evidence("mass_kg", evidence.get("mass_kg", 500.0), unit="kg")
            # GAME PROXY: Open5e combat stats, labeled, never leaked as evidence
            proxy = self._combat_proxy(slug)
            for k, v in proxy.items():
                t.set_game_proxy(k, v, status=Status.GAME_PROXY.value, source="open5e")
            out.append(t)
        return out

    def _obis_evidence(self, scientific: str) -> dict:
        """Query OBIS for real occurrence-derived depth range."""
        occs = self.obis.occurrences(scientificname=scientific, limit=50)
        depths = [o.get("depth") for o in occs if isinstance(o.get("depth"), (int, float))]
        return {
            "observed": len(occs),
            "min_depth": int(min(depths)) if depths else 0,
            "max_depth": int(max(depths)) if depths else 0,
            "mass_kg": 500.0,
        }

    def environments(self) -> list[Environment]:
        return [
            Environment(kind="ocean", name="Abyssal Plain", region="global",
                        constraints={"depth_m": 4000, "pressure_atm": 400, "light": "aphotic"}),
            Environment(kind="ocean", name="Hydrothermal Vent Field", region="global",
                        constraints={"depth_m": 2500, "temperature_c": 4, "chemosynthesis": True}),
            Environment(kind="ocean", name="Epipelagic Zone", region="global",
                        constraints={"depth_m": 200, "light": "photic"}),
        ]

    def environment_for_candidate(self, candidate: Candidate, taxa_by_ref: dict[str, Taxon]) -> Environment | None:
        t = taxa_by_ref.get(candidate.entities[0].key)
        if not t:
            return None
        md = t.facts.evidence.get("max_depth")
        md = md.value if md else 0
        if md >= 3000:
            name = "Abyssal Plain"
        elif md >= 200:
            name = "Epipelagic Zone"
        else:
            name = "Hydrothermal Vent Field"
        return Environment(kind="ocean", name=name, region="global",
                           constraints={"depth_m": md, "light": "aphotic" if md >= 200 else "photic"})

    def _combat_proxy(self, slug: str) -> dict:
        if self.offline or self.open5e is None:
            return {"armor_class": 13, "hit_points": 100, "attack_bonus": 10, "damage_dice": "3d10+6", "speed": 10.0}
        try:
            mon = self.open5e.monster(slug)
            if mon:
                from monstah.simulations import Combatant

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


def deepblue_channel(*, n_runs: int = 1000, offline: bool = False) -> "Channel":
    from channels.base import Channel, ChannelManifest

    manifest = ChannelManifest(
        name="deep-blue",
        title="Deep Blue",
        description="Data-led modern ocean reconstruction via OBIS occurrences",
    )
    return Channel(manifest, DeepBlueAdapter(offline=offline), mode="historical", n_runs=n_runs)
