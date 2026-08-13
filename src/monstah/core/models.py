"""Shared world-engine substrate.

These primitives are domain-agnostic. Synthetic worlds (RoboBladez) and
evidence worlds (paleo / marine / extant life / evolution) both reduce to:

    ENTITY -> MODEL -> ENVIRONMENT -> RELATION -> SCENARIO -> EVENT -> STORY -> SHOT

Truth semantics differ by domain, but the shapes below are universal.
"""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field

DOMAIN = Literal[
    "robobladez",
    "paleo",
    "extant-life",
    "marine",
    "evolution",
    "exoplanets",
    "ancient-worlds",
]


def new_id() -> str:
    return uuid.uuid4().hex


class Reference(BaseModel):
    """Namespace-scoped, immutable object identity.

    Names are *not* identity; identifiers are. A Reference points at a stable
    ID in a known namespace (internal or external like `pbdb`, `gbif`...).
    """

    namespace: str
    key: str

    @property
    def uri(self) -> str:
        return f"{self.namespace}:{self.key}"


class Capability(BaseModel):
    """A named ability a model may exercise inside a scenario."""

    name: str
    description: str = ""
    params: dict[str, Any] = Field(default_factory=dict)


class Entity(BaseModel):
    """The thing being modelled (taxon, agent, lineage, planet...)."""

    id: str = Field(default_factory=new_id)
    refs: list[Reference] = Field(default_factory=list)
    kind: str = "entity"
    name: str
    labels: dict[str, str] = Field(default_factory=dict)
    traits: dict[str, Any] = Field(default_factory=dict)
    capabilities: list[Capability] = Field(default_factory=list)
    properties: dict[str, Any] = Field(default_factory=dict)


class Environment(BaseModel):
    """Conditions that constrain a scenario (geography, depth, climate...)."""

    id: str = Field(default_factory=new_id)
    kind: str = "environment"
    name: str
    region: str = ""
    constraints: dict[str, Any] = Field(default_factory=dict)
    properties: dict[str, Any] = Field(default_factory=dict)


class Relation(BaseModel):
    """A typed edge between entities: eats, hosts, competes, ancestor-of..."""

    id: str = Field(default_factory=new_id)
    kind: str = "relation"
    relation: str
    subject: Reference
    object: Reference
    properties: dict[str, Any] = Field(default_factory=dict)


class Scenario(BaseModel):
    """A parameterized configuration of entities in an environment."""

    id: str = Field(default_factory=new_id)
    kind: str = "scenario"
    name: str
    template: str
    entities: list[Reference] = Field(default_factory=list)
    environment: Reference | None = None
    mode: Literal["historical", "lab"] = "historical"
    params: dict[str, Any] = Field(default_factory=dict)


class SimulationRun(BaseModel):
    """One execution of a scenario under a random seed."""

    id: str = Field(default_factory=new_id)
    scenario: str
    seed: int
    model_versions: dict[str, str] = Field(default_factory=dict)
    params: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] = Field(default_factory=dict)


class Event(BaseModel):
    """A discrete outcome the simulation produced."""

    id: str = Field(default_factory=new_id)
    run: str | None = None
    kind: str = "event"
    timestamp: float = 0.0
    description: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)


class Story(BaseModel):
    """An editorial narrative over events."""

    id: str = Field(default_factory=new_id)
    title: str
    events: list[str] = Field(default_factory=list)
    claims: list[str] = Field(default_factory=list)
    narrative: dict[str, Any] = Field(default_factory=dict)


class Shot(BaseModel):
    """A renderable scene beat."""

    id: str = Field(default_factory=new_id)
    story: str | None = None
    index: int = 0
    asset_ref: str = ""
    camera: dict[str, Any] = Field(default_factory=dict)
    action: dict[str, Any] = Field(default_factory=dict)
    duration: float = 0.0


class Asset(BaseModel):
    """Canonical media asset (render, model, image, ltx scene)."""

    id: str = Field(default_factory=new_id)
    kind: str = "asset"
    uri: str = ""
    tags: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)


class History(BaseModel):
    """Ordered, versioned record of states/events for a world line."""

    world: str = ""
    events: list[Event] = Field(default_factory=list)
    versions: dict[str, str] = Field(default_factory=dict)
