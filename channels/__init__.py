"""Channel registry — one folder per theme, organized by dataflow.

Each theme is a self-contained package under `channels/<theme>/`:

    channels/
    ├── base.py            shared Channel + policies + EvidenceAdapter
    ├── prehistoric/       extinct-world reconstruction (battle)
    ├── ancient_oceans/    marine prehistory (battle)
    ├── deep_blue/         modern ocean, OBIS-driven (battle)
    ├── living_planet/     ecology graph stories (non-combat)
    └── tree_of_life/      evolution/phylogeny (non-combat)

Every theme folder contains:
    channel.py   the builder (manifest + adapter + policy bundle)
    __init__.py  exposes `<theme>_channel`
    DATAFLOW.md  the source→adapter→policy→output dataflow for the theme
"""

from __future__ import annotations

from .ancient_oceans import ancient_oceans_channel
from .base import (
    Channel,
    ChannelManifest,
    DiscoveryPolicy,
    EvidenceAdapter,
    MediaPolicy,
    NarrativePolicy,
    ReconstructionPolicy,
    SimulationPolicy,
    TruthPolicy,
)
from .deep_blue import deepblue_channel
from .living_planet import living_planet_channel
from .prehistoric import prehistoric_channel
from .tree_of_life import tree_of_life_channel

_CHANNELS = {
    "prehistoric": prehistoric_channel,
    "ancient-oceans": ancient_oceans_channel,
    "deep-blue": deepblue_channel,
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
    "Channel",
    "ChannelManifest",
    "DiscoveryPolicy",
    "EvidenceAdapter",
    "MediaPolicy",
    "NarrativePolicy",
    "ReconstructionPolicy",
    "SimulationPolicy",
    "TruthPolicy",
    "get_channel",
    "list_channels",
]
