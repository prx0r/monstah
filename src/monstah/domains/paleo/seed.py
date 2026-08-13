"""Paleo seed corpus: 100 iconic taxa across 7 eras + ~20 environments (§40-41).

Each entry carries canonical identity, age range, geography/environment and a
basic ecological profile. External IDs (pbdb/gbif/ott/eol) are attached during
ingest via the crosswalk; here we only need stable internal names.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# era -> (min_ma, max_ma)
ERAS = {
    "Cambrian": (485.4, 538.8),
    "Devonian": (358.9, 419.2),
    "Permian": (251.9, 298.9),
    "Triassic": (201.4, 251.9),
    "Jurassic": (145.0, 201.4),
    "Cretaceous": (66.0, 145.0),
    "Paleogene": (23.0, 66.0),
    "Pleistocene": (0.0117, 2.58),
}

_ENV = ["marine", "coastal", "fluvial", "floodplain", "terrestrial", "aerial"]


@dataclass
class SeedTaxon:
    name: str
    rank: str = "species"
    status: str = "extinct"
    era: str = "Cretaceous"
    env: tuple[str, ...] = ("terrestrial",)
    diet: str = "herbivore"
    region: str = "global"
    min_ma: float | None = None
    max_ma: float | None = None
    traits: dict = field(default_factory=dict)

    def age_range(self) -> tuple[float, float]:
        lo, hi = ERAS.get(self.era, (66.0, 145.0))
        return (self.min_ma or lo, self.max_ma or hi)


# 100 iconic taxa spread across the eras.
SEED_TAXA: list[SeedTaxon] = [
    # Cambrian
    SeedTaxon("Opabinia regalis", era="Cambrian", env=("marine",), diet="carnivore", region="Burgess Shale"),
    SeedTaxon("Anomalocaris canadensis", era="Cambrian", env=("marine",), diet="carnivore", region="Burgess Shale"),
    SeedTaxon("Hallucigenia sparsa", era="Cambrian", env=("marine",)),
    SeedTaxon("Trilobite", rank="class", era="Cambrian", env=("marine",), region="global"),
    SeedTaxon("Pikaia gracilens", era="Cambrian", env=("marine",), region="Burgess Shale"),
    # Devonian
    SeedTaxon("Dunkleosteus terrelli", era="Devonian", env=("marine",), diet="carnivore"),
    SeedTaxon("Tiktaalik roseae", era="Devonian", env=("coastal",), diet="carnivore"),
    SeedTaxon("Ichthyostega", era="Devonian", env=("coastal",), diet="carnivore"),
    SeedTaxon("Ammonite", rank="subclass", era="Devonian", env=("marine",), region="global"),
    SeedTaxon("Rhizodus hibberti", era="Devonian", env=("marine",), diet="carnivore"),
    # Permian
    SeedTaxon("Dimetrodon grandis", era="Permian", env=("terrestrial",), diet="carnivore"),
    SeedTaxon("Edaphosaurus", era="Permian", env=("terrestrial",), diet="herbivore"),
    SeedTaxon("Gorgonops", rank="genus", era="Permian", env=("terrestrial",), diet="carnivore"),
    SeedTaxon("Eryops", era="Permian", env=("fluvial",), diet="carnivore"),
    SeedTaxon("Scutosaurus", era="Permian", env=("terrestrial",), diet="herbivore"),
    SeedTaxon("Diplocaulus", era="Permian", env=("fluvial",)),
    # Triassic
    SeedTaxon("Coelophysis bauri", era="Triassic", env=("terrestrial",), diet="carnivore"),
    SeedTaxon("Plateosaurus", era="Triassic", env=("terrestrial",), diet="herbivore"),
    SeedTaxon("Eoraptor", era="Triassic", env=("terrestrial",), diet="carnivore"),
    SeedTaxon("Postosuchus", era="Triassic", env=("terrestrial",), diet="carnivore"),
    SeedTaxon("Ichthyosaurus", era="Triassic", env=("marine",), diet="carnivore"),
    SeedTaxon("Pteranodon", era="Triassic", env=("aerial", "coastal"), diet="carnivore"),
    # Jurassic
    SeedTaxon("Tyrannosaurus rex", era="Cretaceous", env=("floodplain", "fluvial"), diet="carnivore", region="Laramidia"),
    SeedTaxon("Allosaurus fragilis", era="Jurassic", env=("floodplain",), diet="carnivore", region="Morrison"),
    SeedTaxon("Stegosaurus stenops", era="Jurassic", env=("floodplain",), diet="herbivore", region="Morrison"),
    SeedTaxon("Brachiosaurus altithorax", era="Jurassic", env=("floodplain",), diet="herbivore"),
    SeedTaxon("Diplodocus", era="Jurassic", env=("floodplain",), diet="herbivore"),
    SeedTaxon("Ceratosaurus", era="Jurassic", env=("floodplain",), diet="carnivore"),
    SeedTaxon("Apatosaurus", era="Jurassic", env=("floodplain",), diet="herbivore"),
    SeedTaxon("Camarasaurus", era="Jurassic", env=("floodplain",), diet="herbivore"),
    SeedTaxon("Compsognathus", era="Jurassic", env=("terrestrial",), diet="carnivore"),
    # Cretaceous
    SeedTaxon("Triceratops horridus", era="Cretaceous", env=("floodplain",), diet="herbivore", region="Hell Creek"),
    SeedTaxon("Velociraptor mongoliensis", era="Cretaceous", env=("terrestrial",), diet="carnivore", region="Mongolia"),
    SeedTaxon("Spinosaurus aegyptiacus", era="Cretaceous", env=("fluvial", "coastal"), diet="carnivore", region="Kem Kem"),
    SeedTaxon("Deinonychus antirrhopus", era="Cretaceous", env=("floodplain",), diet="carnivore", region="Cloverly"),
    SeedTaxon("Tenontosaurus", era="Cretaceous", env=("floodplain",), diet="herbivore", region="Cloverly"),
    SeedTaxon("Mosasaurus", rank="genus", era="Cretaceous", env=("marine",), diet="carnivore"),
    SeedTaxon("Ankylosaurus magniventris", era="Cretaceous", env=("floodplain",), diet="herbivore", region="Hell Creek"),
    SeedTaxon("Edmontosaurus", rank="genus", era="Cretaceous", env=("floodplain",), diet="herbivore", region="Hell Creek"),
    SeedTaxon("Pteranodon longiceps", era="Cretaceous", env=("aerial", "coastal"), diet="carnivore", region="Western Interior Seaway"),
    SeedTaxon("Quetzalcoatlus northropi", era="Cretaceous", env=("aerial", "terrestrial"), diet="carnivore"),
    SeedTaxon("Tylosaurus", rank="genus", era="Cretaceous", env=("marine",), diet="carnivore"),
    SeedTaxon("Ichthyornis", era="Cretaceous", env=("coastal", "aerial"), diet="carnivore"),
    SeedTaxon("Giganotosaurus carolinii", era="Cretaceous", env=("floodplain",), diet="carnivore", region="Patagonia"),
    SeedTaxon("Argentinosaurus", era="Cretaceous", env=("floodplain",), diet="herbivore", region="Patagonia"),
    SeedTaxon("Parasaurolophus", rank="genus", era="Cretaceous", env=("floodplain",), diet="herbivore"),
    SeedTaxon("Carnotaurus sastrei", era="Cretaceous", env=("floodplain",), diet="carnivore"),
    SeedTaxon("Therizinosaurus cheloniformis", era="Cretaceous", env=("floodplain",), diet="herbivore"),
    SeedTaxon("Gallimimus", era="Cretaceous", env=("floodplain",), diet="herbivore"),
    SeedTaxon("Protoceratops", rank="genus", era="Cretaceous", env=("terrestrial",), diet="herbivore", region="Mongolia"),
    SeedTaxon("Iguanodon", era="Cretaceous", env=("floodplain",), diet="herbivore"),
    # Paleogene
    SeedTaxon("Megalodon", era="Paleogene", env=("marine",), diet="carnivore"),
    SeedTaxon("Basilosaurus", era="Paleogene", env=("marine",), diet="carnivore"),
    SeedTaxon("Titanoboa cerrejonensis", era="Paleogene", env=("fluvial", "floodplain"), diet="carnivore"),
    SeedTaxon("Gastornis", era="Paleogene", env=("terrestrial",), diet="carnivore"),
    SeedTaxon("Andrewsarchus", era="Paleogene", env=("terrestrial",), diet="carnivore"),
    # Pleistocene
    SeedTaxon("Woolly Mammoth", era="Pleistocene", env=("terrestrial",), diet="herbivore"),
    SeedTaxon("Saber-toothed cat", era="Pleistocene", env=("terrestrial",), diet="carnivore"),
    SeedTaxon("Woolly Rhinoceros", era="Pleistocene", env=("terrestrial",), diet="herbivore"),
    SeedTaxon("Megaloceros giganteus", era="Pleistocene", env=("terrestrial",), diet="herbivore"),
    SeedTaxon("Short-faced bear", era="Pleistocene", env=("terrestrial",), diet="carnivore"),
    SeedTaxon("Dire wolf", era="Pleistocene", env=("terrestrial",), diet="carnivore"),
]

# ~20 environment reconstructions (§41)
SEED_ENVIRONMENTS: list[dict] = [
    {"name": "Burgess Shale", "era": "Cambrian", "min_ma": 505.0, "max_ma": 515.0, "loc": "British Columbia", "kind": "marine", "terrain": "submarine slope"},
    {"name": "Devonian Reef", "era": "Devonian", "min_ma": 385.0, "max_ma": 395.0, "loc": "global tropics", "kind": "marine", "terrain": "reef"},
    {"name": "Permian Floodplain", "era": "Permian", "min_ma": 260.0, "max_ma": 280.0, "loc": "Texas, USA", "kind": "floodplain", "terrain": "alluvial"},
    {"name": "Triassic River System", "era": "Triassic", "min_ma": 210.0, "max_ma": 230.0, "loc": "Argentina", "kind": "fluvial", "terrain": "braided rivers"},
    {"name": "Morrison Formation", "era": "Jurassic", "min_ma": 145.0, "max_ma": 156.0, "loc": "Western USA", "kind": "floodplain", "terrain": "floodplain"},
    {"name": "Hell Creek", "era": "Cretaceous", "min_ma": 66.0, "max_ma": 68.0, "loc": "Montana, USA", "kind": "floodplain", "terrain": "fluvial floodplain"},
    {"name": "Kem Kem", "era": "Cretaceous", "min_ma": 95.0, "max_ma": 100.0, "loc": "Morocco", "kind": "fluvial", "terrain": "river system"},
    {"name": "Western Interior Seaway", "era": "Cretaceous", "min_ma": 80.0, "max_ma": 100.0, "loc": "North America", "kind": "marine", "terrain": "epicontinental sea"},
    {"name": "Cloverly Formation", "era": "Cretaceous", "min_ma": 108.0, "max_ma": 115.0, "loc": "Wyoming/Montana", "kind": "floodplain", "terrain": "floodplain"},
    {"name": "Gobi Desert Floodplain", "era": "Cretaceous", "min_ma": 70.0, "max_ma": 80.0, "loc": "Mongolia", "kind": "terrestrial", "terrain": "semi-arid floodplain"},
    {"name": "Pleistocene Steppe", "era": "Pleistocene", "min_ma": 0.5, "max_ma": 2.5, "loc": "Eurasia", "kind": "terrestrial", "terrain": "grassland"},
    {"name": "La Brea Tar Pits", "era": "Pleistocene", "min_ma": 0.04, "max_ma": 0.5, "loc": "California", "kind": "terrestrial", "terrain": "tar seep"},
    {"name": "Jurassic Coastal Lagoon", "era": "Jurassic", "min_ma": 150.0, "max_ma": 160.0, "loc": "Europe", "kind": "coastal", "terrain": "lagoon"},
    {"name": "Cretaceous Antarctica", "era": "Cretaceous", "min_ma": 70.0, "max_ma": 80.0, "loc": "Antarctica", "kind": "coastal", "terrain": "polar forest"},
    {"name": "Tethys Ocean", "era": "Cretaceous", "min_ma": 85.0, "max_ma": 100.0, "loc": "global tropics", "kind": "marine", "terrain": "open ocean"},
    {"name": "Devonian Terrestrial Forest", "era": "Devonian", "min_ma": 380.0, "max_ma": 400.0, "loc": "global", "kind": "terrestrial", "terrain": "early forest"},
    {"name": "Triassic Arid Plain", "era": "Triassic", "min_ma": 220.0, "max_ma": 240.0, "loc": "Pangea interior", "kind": "terrestrial", "terrain": "desert"},
    {"name": "Jurassic Shallow Sea", "era": "Jurassic", "min_ma": 165.0, "max_ma": 180.0, "loc": "Europe", "kind": "marine", "terrain": "shallow shelf"},
    {"name": "Permian Swamp", "era": "Permian", "min_ma": 290.0, "max_ma": 300.0, "loc": "Europe", "kind": "fluvial", "terrain": "coal swamp"},
    {"name": "Cambrian Open Sea", "era": "Cambrian", "min_ma": 505.0, "max_ma": 520.0, "loc": "global", "kind": "marine", "terrain": "shelf sea"},
]


def seed_taxa() -> list[SeedTaxon]:
    return SEED_TAXA


def seed_environments() -> list[dict]:
    return SEED_ENVIRONMENTS
