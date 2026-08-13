"""Open5e client: D&D 5e / SRD / OGL monster statblocks.

This is the reusable capability-data corpus. A statblock maps 1:1 onto our
capability model:

    strength/dex/con  -> speed/perception/agility
    armor_class       -> defence
    hit_points        -> hp pool
    challenge_rating  -> balance scalar
    actions[] (attack_bonus + damage_dice) -> our attack primitive

Data is OGL/SRD licensed, so we can use it directly rather than hand-tuning
capability weights. Adapted into `CapabilityModel` for the shared battle engine.
"""

from __future__ import annotations

from typing import Any

from ..core.models import Capability, Reference
from .base import HttpApi, IngestError

# Open5e uses d20-style damage dice strings like "3d8+5".
DAMAGE_DICE = ("3d8+5", "2d6+3", "2d8+4", "1d12+5", "4d6", "3d6+4", "2d10+6")


def roll_dice(rng: Any, dice: str) -> int:
    """Roll a D&D dice string ('3d8+5') deterministically with a seeded rng."""
    import re

    m = re.match(r"(\d+)d(\d+)([+-]\d+)?", dice.strip())
    if not m:
        return 0
    num, sides = int(m.group(1)), int(m.group(2))
    mod = int(m.group(3) or 0)
    return sum(rng.randint(1, sides) for _ in range(num)) + mod


class Open5eClient(HttpApi):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__("https://api.open5e.com/v1", **kwargs)

    def monsters(self, *, limit: int = 50, page: int = 1, cr: str | None = None, **filters) -> list[dict]:
        params: dict[str, Any] = {"limit": limit, "page": page}
        if cr:
            params["cr"] = cr
        params.update(filters)
        data = self.get("monsters/", params)
        return data.get("results", [])

    def monster(self, slug: str) -> dict:
        try:
            return self.get(f"monsters/{slug}/")
        except IngestError:
            # fall back to fuzzy search by name
            hits = self.search(slug)
            return hits[0] if hits else {}

    def search(self, q: str) -> list[dict]:
        return self.monsters(limit=10, search=q)

    def to_capability_model(self, mon: dict, ref: Reference | None = None) -> dict:
        """Map an Open5e statblock to our battle-engine capability dict."""
        import re

        # strength is a decent proxy for mass/threat; armor_class for defence
        attack_bonus = 0
        damage_dice = "1d6"
        for action in mon.get("actions", []) or []:
            dmg = action.get("damage_dice")
            if dmg:
                damage_dice = dmg
                if isinstance(dmg, str):
                    m = re.search(r"([+-]\d+)", dmg)
                    attack_bonus = max(attack_bonus, 0)
        hp_dice = mon.get("hit_dice", "")
        stamina = 10.0
        if isinstance(hp_dice, str):
            m = re.match(r"(\d+)d", hp_dice)
            if m:
                stamina = float(m.group(1)) / 3.0  # normalize hit dice count
        speed = 8.0
        sp = mon.get("speed")
        if isinstance(sp, dict):
            speed = float(sp.get("walk", 30)) / 4.0  # 5e ft -> rough m/s-ish scale
        elif isinstance(sp, (int, float)):
            speed = float(sp) / 4.0
        return {
            "name": mon.get("name", ""),
            "ref": ref or Reference(namespace="open5e", key=mon.get("slug", "")),
            "hit_points": mon.get("hit_points", 30),
            "armor_class": mon.get("armor_class", 10),
            "challenge_rating": mon.get("challenge_rating", "1"),
            "attack_bonus": attack_bonus,
            "damage_dice": damage_dice,
            "speed": speed,
            "stamina": stamina,
            "perception": 60.0,
            "diet": "carnivore" if "creature_type" not in mon or mon.get("creature_type") != "plant" else "herbivore",
            "abilities": {k: mon.get(k) for k in ("strength", "dexterity", "constitution")},
            "actions": [a for a in mon.get("actions", []) if a.get("name")][:8],
        }
