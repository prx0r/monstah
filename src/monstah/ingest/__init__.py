"""Data ingest facade: one entry point to every external world source."""

from .eol import EolClient
from .gbif import GbifClient
from .globi import GlobiClient
from .macrostrat import MacrostratClient
from .obis import ObisClient
from .open5e import Open5eClient
from .openalex import OpenAlexClient
from .opentree import OpenTreeClient
from .pbdb import PbdbClient

__all__ = [
    "EolClient",
    "GbifClient",
    "GlobiClient",
    "MacrostratClient",
    "ObisClient",
    "Open5eClient",
    "OpenAlexClient",
    "OpenTreeClient",
    "PbdbClient",
]
