# Asset System — canonical images & reconstructions

**SOURCE IMAGE ≠ CANONICAL RECONSTRUCTION.** For extant taxa a source photo can
directly represent the animal; for extinct taxa a museum photo / fossil plate /
paleoart is *evidence*, and the approved `TREX_RECON_R17` is what LTX animates.

```
ENTITY → IMAGE DISCOVERY → LICENSE FILTER → SOURCE IMAGE SET
  → EVIDENCE/REFERENCE PACK → CANONICAL RECONSTRUCTION IMAGE → LTX I2V
```

## Providers (provider-agnostic like LTX)

`ImageResolver` merges candidates from all providers; `AssetPack` scores them.

| Provider | Covers | Live? |
|---|---|---|
| **GBIF** | extant observational photos + occurrence metadata | yes (no auth) |
| **iNaturalist** | research-grade open-license photos up to 2048px | yes (no auth) |
| **Wikimedia Commons** | skeletons, fossils, plates, diagrams, public-domain | yes (proper UA) |
| **BHL** | 19th-c. scientific plates | needs API key |

## License policy (part of asset identity)

- **ALLOW (score 1.0):** Public Domain, CC0, CC BY, CC BY-SA
- **REVIEW (0.5):** CC BY-NC / BY-NC-SA / BY-ND / GFDL (check downstream use)
- **REJECT (0.0):** all-rights-reserved, proprietary, unclear

License is stored independently from occurrence data (never assumed reusable).

## Ranking — evidence fit, not popularity

```
asset_score = taxonomic_confidence
            × license_usability
            × resolution_factor
            × image_quality
            × viewpoint_value
            × provenance_quality
            × reconstruction_relevance
```

A T. rex pack wants: mounted-skeleton lateral, skull lateral, fossil specimen,
anatomical reconstruction, environment reference, historical reconstruction —
not six "cool" pictures.

## Roles & epistemic status

- roles: `OBSERVATIONAL_REFERENCE | FOSSIL_REFERENCE | ANATOMICAL_REFERENCE |
  ENVIRONMENT_REFERENCE | HISTORICAL_RECONSTRUCTION | CANONICAL_RECONSTRUCTION | EDITORIAL`
- epistemic: `OBSERVED_PHOTOGRAPH | PRIMARY_SPECIMEN_IMAGE | HISTORICAL_ILLUSTRATION |
  MODERN_RECONSTRUCTION | GENERATED_RECONSTRUCTION`

## R2 layout

```
assets/
├── source/{gbif|inaturalist|wikimedia|bhl}/
├── entities/<entity-id>/{references,reconstructions}/
└── environments/<env-id>/
```

## Wiring
- `media/asset.py` — AssetCandidate / AssetPack, license policy, scoring
- `media/providers.py` — GbifImageProvider, INaturalistProvider, WikimediaProvider,
  BhlProvider (key-gated), ImageResolver
- `media/storage.py` — AssetStore (R2 layout)
- Channel `_attach_references` resolves licensed references into each LTX ShotSpec's
  `references` (I2V conditioning) when online; skipped in offline simulate.
- SQL: `asset_sources`, `asset_licenses`, `asset_entity_links`, `asset_embeddings`,
  `asset_reviews`, `visual_reconstructions`, `visual_reconstruction_assets`

## The moat
Once a reconstruction asset is approved + versioned, every future episode in every
channel reuses it. GBIF+iNaturalist make extant channels (Deep Blue, Living Planet)
near-trivial on the image side; Commons+BHL back the extinct/scientific-history side.
