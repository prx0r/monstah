"""Channel registry: a theme = evidence adapter + policies over the core engine.

    monstah channel prehistoric
    monstah channel deep-blue
    monstah channel ancient-oceans
    monstah channel living-planet
    monstah channel tree-of-life

All run the same chain: ingest -> discover -> battle-or-graph -> story -> shots.
Only the adapter (which APIs populate entities) and policy bundle differ.
"""

from __future__ import annotations

from .base import Channel, ChannelManifest, EvidenceAdapter
from .ancient_oceans import AncientOceansAdapter, ancient_oceans_channel
from .deepblue import DeepBlueAdapter, deepblue_channel
from .livingplanet import LivingPlanetAdapter, LivingPlanetChannel, living_planet_channel
from .prehistoric import PrehistoricAdapter, prehistoric_channel
from .tree_of_life import TreeOfLifeAdapter, TreeOfLifeChannel, tree_of_life_channel

_CHANNELS = {
    "prehistoric": prehistoric_channel,
    "deep-blue": deepblue_channel,
    "ancient-oceans": ancient_oceans_channel,
    "living-planet": living_planet_channel,
    "tree-of-life": tree_of_life_channel,
}


def get_channel(name: str, **kwargs) -> Channel:
    if name not in _CHANNELS:
        raise KeyError(f"unknown channel '{name}'; available: {list(_CHANNELS)}")
    return _CHANNELS[name](**kwargs)


def list_channels() -> list[str]:
    return list(_CHANNELS)


__all__ = [
    "AncientOceansAdapter",
    "Channel",
    "ChannelManifest",
    "DeepBlueAdapter",
    "EvidenceAdapter",
    "LivingPlanetAdapter",
    "LivingPlanetChannel",
    "PrehistoricAdapter",
    "TreeOfLifeAdapter",
    "TreeOfLifeChannel",
    "ancient_oceans_channel",
    "deepblue_channel",
    "get_channel",
    "list_channels",
    "living_planet_channel",
    "prehistoric_channel",
    "tree_of_life_channel",
]
