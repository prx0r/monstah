"""Channel registry: a theme = evidence adapter + story policy over the core engine.

    monstah channel prehistoric
    monstah channel deep-blue

Both run the same chain: ingest -> discover -> battle -> story -> shots -> store.
Only the adapter (which APIs populate entities) and story policy differ.
"""

from __future__ import annotations

from .base import Channel, ChannelManifest, EvidenceAdapter
from .deepblue import DeepBlueAdapter, deepblue_channel
from .prehistoric import PrehistoricAdapter, prehistoric_channel

_CHANNELS = {
    "prehistoric": prehistoric_channel,
    "deep-blue": deepblue_channel,
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
    "DeepBlueAdapter",
    "EvidenceAdapter",
    "PrehistoricAdapter",
    "deepblue_channel",
    "get_channel",
    "list_channels",
    "prehistoric_channel",
]
