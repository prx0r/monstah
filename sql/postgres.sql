-- Monstah canonical store: PostgreSQL + PostGIS.
-- DuckDB + Parquet are used for analytical joins / simulation outputs.

CREATE EXTENSION IF NOT EXISTS postgis;

-- Entity / taxon backbone -----------------------------------------------------
CREATE TABLE IF NOT EXISTS entities (
    id         TEXT PRIMARY KEY,
    kind       TEXT NOT NULL,           -- taxon | agent | lineage | planet | ...
    name       TEXT NOT NULL,
    properties JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS taxa (
    entity_id   TEXT PRIMARY KEY REFERENCES entities(id),
    rank        TEXT,
    status      TEXT,                    -- extant | extinct
    first_ma    DOUBLE PRECISION,
    last_ma     DOUBLE PRECISION,
    parent_id   TEXT REFERENCES entities(id)
);

-- Identifier crosswalk: one row per (entity, namespace) -----------------------
CREATE TABLE IF NOT EXISTS external_ids (
    entity_id   TEXT NOT NULL REFERENCES entities(id),
    namespace   TEXT NOT NULL,           -- pbdb | gbif | ott | eol | worms | wikidata | macrostrat | obis
    ext_id      TEXT NOT NULL,
    PRIMARY KEY (entity_id, namespace)
);
CREATE INDEX IF NOT EXISTS idx_ext_ids_namespace ON external_ids (namespace, ext_id);

-- Spatio-temporal occurrences -------------------------------------------------
CREATE TABLE IF NOT EXISTS occurrences (
    id         BIGSERIAL PRIMARY KEY,
    entity_id  TEXT REFERENCES entities(id),
    source     TEXT,
    ext_occ_id TEXT,
    geom       geometry(Point, 4326),
    min_ma     DOUBLE PRECISION,
    max_ma     DOUBLE PRECISION,
    depth_m    DOUBLE PRECISION,
    formation  TEXT,
    collection TEXT,
    metadata   JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_occ_geom ON occurrences USING gist (geom);
CREATE INDEX IF NOT EXISTS idx_occ_entity ON occurrences (entity_id);

-- Time intervals / environments ----------------------------------------------
CREATE TABLE IF NOT EXISTS time_intervals (
    id      TEXT PRIMARY KEY,
    name    TEXT,
    min_ma  DOUBLE PRECISION,
    max_ma  DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS environments (
    id         TEXT PRIMARY KEY,
    kind       TEXT,
    name       TEXT,
    region     TEXT,
    constraints JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Evidence layer -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sources (
    id           TEXT PRIMARY KEY,
    namespace    TEXT NOT NULL,
    external_id  TEXT NOT NULL,
    type         TEXT NOT NULL DEFAULT 'unknown',
    locator      TEXT,
    title        TEXT,
    access_date  TEXT,
    metadata     JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS trait_assertions (
    id            TEXT PRIMARY KEY,
    entity_id     TEXT NOT NULL REFERENCES entities(id),
    trait         TEXT NOT NULL,
    value_json    JSONB,
    status        TEXT NOT NULL,          -- OBSERVED | LITERATURE_ESTIMATE | INFERRED | MODELLED | SPECULATIVE
    confidence    DOUBLE PRECISION,
    unit          TEXT,
    value_lower   DOUBLE PRECISION,
    value_median  DOUBLE PRECISION,
    value_upper   DOUBLE PRECISION,
    source_id     TEXT REFERENCES sources(id),
    source_locator TEXT,
    method        TEXT,
    version       TEXT
);
CREATE INDEX IF NOT EXISTS idx_trait_assert_entity ON trait_assertions (entity_id, trait);

CREATE TABLE IF NOT EXISTS relation_assertions (
    id          TEXT PRIMARY KEY,
    relation    TEXT NOT NULL,           -- eats | host of | parasite of | pollinates | ...
    subject_id  TEXT NOT NULL REFERENCES entities(id),
    object_id   TEXT NOT NULL REFERENCES entities(id),
    status      TEXT,
    confidence  DOUBLE PRECISION,
    source_id   TEXT REFERENCES sources(id)
);
CREATE INDEX IF NOT EXISTS idx_rel_subject ON relation_assertions (subject_id, relation);

CREATE TABLE IF NOT EXISTS claims (
    id        TEXT PRIMARY KEY,
    entity_id TEXT,
    trait     TEXT,
    statement TEXT,
    source_id TEXT REFERENCES sources(id),
    status    TEXT,
    confidence DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS reconstructions (
    id           TEXT PRIMARY KEY,
    entity_id    TEXT NOT NULL REFERENCES entities(id),
    version      TEXT NOT NULL,
    parameters   JSONB NOT NULL DEFAULT '{}'::jsonb,
    assumptions  JSONB NOT NULL DEFAULT '{}'::jsonb,
    supersedes   TEXT,
    superseded_by TEXT,
    UNIQUE (entity_id, version)
);

-- Scenarios / simulations ----------------------------------------------------
CREATE TABLE IF NOT EXISTS scenarios (
    id         TEXT PRIMARY KEY,
    name       TEXT,
    template   TEXT,
    mode       TEXT,                    -- historical | lab
    entities   TEXT[],
    environment_id TEXT REFERENCES environments(id),
    params     JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS simulation_runs (
    id            TEXT PRIMARY KEY,
    scenario_id   TEXT REFERENCES scenarios(id),
    seed          BIGINT,
    model_versions JSONB NOT NULL DEFAULT '{}'::jsonb,
    result        JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS events (
    id        TEXT PRIMARY KEY,
    run_id    TEXT REFERENCES simulation_runs(id),
    kind      TEXT,
    ts        DOUBLE PRECISION,
    description TEXT,
    payload   JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Media ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stories (
    id        TEXT PRIMARY KEY,
    title     TEXT,
    events    TEXT[],
    claims    TEXT[],
    narrative JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS shots (
    id      TEXT PRIMARY KEY,
    story_id TEXT REFERENCES stories(id),
    index   INT,
    asset_uri TEXT,
    camera  JSONB NOT NULL DEFAULT '{}'::jsonb,
    action  JSONB NOT NULL DEFAULT '{}'::jsonb,
    duration DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS assets (
    id         TEXT PRIMARY KEY,
    kind       TEXT,
    uri        TEXT,
    tags       TEXT[],
    provenance JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Asset / image library -------------------------------------------------------
CREATE TABLE IF NOT EXISTS asset_sources (
    id            TEXT PRIMARY KEY,
    provider      TEXT NOT NULL,          -- gbif | inaturalist | wikimedia | bhl
    provider_id   TEXT NOT NULL,
    entity_id     TEXT REFERENCES entities(id),
    original_uri  TEXT,
    preview_uri   TEXT,
    creator       TEXT,
    source_url    TEXT,
    width         INT,
    height        INT,
    role          TEXT,                   -- OBSERVATIONAL_REFERENCE | FOSSIL_REFERENCE | ...
    epistemic_status TEXT,                -- OBSERVED_PHOTOGRAPH | HISTORICAL_ILLUSTRATION | ...
    score         DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS asset_licenses (
    asset_source_id TEXT PRIMARY KEY REFERENCES asset_sources(id),
    license         TEXT NOT NULL,
    tier            TEXT NOT NULL,        -- ALLOW | REVIEW | REJECT
    attribution     TEXT,
    verified_at     TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS asset_entity_links (
    asset_source_id TEXT NOT NULL REFERENCES asset_sources(id),
    entity_id       TEXT NOT NULL REFERENCES entities(id),
    role            TEXT NOT NULL,
    PRIMARY KEY (asset_source_id, entity_id, role)
);

CREATE TABLE IF NOT EXISTS asset_embeddings (
    asset_source_id TEXT PRIMARY KEY REFERENCES asset_sources(id),
    model           TEXT,
    vector          DOUBLE PRECISION[]
);

CREATE TABLE IF NOT EXISTS asset_reviews (
    id              TEXT PRIMARY KEY,
    asset_source_id TEXT REFERENCES asset_sources(id),
    reviewer        TEXT,
    verdict         TEXT,                 -- APPROVED | REJECTED | REVISION
    note            TEXT,
    reviewed_at     TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS visual_reconstructions (
    id                TEXT PRIMARY KEY,
    entity_id         TEXT NOT NULL REFERENCES entities(id),
    version           TEXT NOT NULL,       -- TREX_VISUAL_R17
    role              TEXT,
    image_uri         TEXT,
    evidence_refs     TEXT[],
    supersedes        TEXT,
    UNIQUE (entity_id, version)
);

CREATE TABLE IF NOT EXISTS visual_reconstruction_assets (
    visual_reconstruction_id TEXT NOT NULL REFERENCES visual_reconstructions(id),
    asset_source_id          TEXT NOT NULL REFERENCES asset_sources(id),
    PRIMARY KEY (visual_reconstruction_id, asset_source_id)
);

-- Episodes (channel output) --------------------------------------------------
CREATE TABLE IF NOT EXISTS episodes (
    id         TEXT PRIMARY KEY,
    channel    TEXT,
    story_id   TEXT REFERENCES stories(id),
    title      TEXT,
    status     TEXT,
    published_at TIMESTAMPTZ,
    metadata   JSONB NOT NULL DEFAULT '{}'::jsonb
);
