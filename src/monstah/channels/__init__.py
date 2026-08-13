"""Back-compat facade: the canonical channel definitions now live at the repo
root in the `channels/` package (one folder per theme). This module re-exports
them so existing imports of `monstah.channels.get_channel` keep working.
"""

from __future__ import annotations

from channels import (  # noqa: F401
    Channel,
    ChannelManifest,
    DiscoveryPolicy,
    EvidenceAdapter,
    MediaPolicy,
    NarrativePolicy,
    ReconstructionPolicy,
    SimulationPolicy,
    TruthPolicy,
    get_channel,
    list_channels,
)

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
