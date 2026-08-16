-- Apex infra · apex.plan_memory — RATIFIED contract v0.3 schema (CONTRACT.md changelog v0.3).
-- MIRROR of memory/sql/030_plan_memory.sql (the lane owns this DDL; infra only applies it).
-- Applied verbatim (CREATE DATABASE dropped — 001_database.sql owns it). Never
-- rename/repurpose a column; if memory/ changes the source, this file is re-mirrored.
--
-- Grain: one row per (plan_fingerprint, encoder_version).
-- This is the FUZZY half of plan recall. The EXACT half needs no table at all --
-- plan_fingerprint equality already gives it, for free, from apex.spark_events.

CREATE TABLE IF NOT EXISTS apex.plan_memory (
  plan_fingerprint  FixedString(64),           -- contract v0.2 key: SHA-256 of the
                                               -- literal-NORMALIZED LOGICAL plan
  encoder_version   LowCardinality(String),    -- 'struct-v1' today; 'jina-v3' etc. later
  embedding_kind    LowCardinality(String),    -- 'structural' | 'text'
  embedding         Array(Float32),            -- L2-NORMALISED. cosineDistance-ready.
  dim               UInt16,                    -- len(embedding); asserted on read

  -- Decoded features. Not redundant with `embedding`: these are what a human (or
  -- an LLM writing an explanation) reads to answer "WHY did these two plans match?".
  -- An opaque vector cannot be cited as evidence; these can.
  op_counts         Map(LowCardinality(String), UInt32),
  node_count        UInt32,
  max_depth         UInt16,
  join_count        UInt16,
  agg_count         UInt16,
  exchange_count    UInt16,
  scan_count        UInt16,
  has_udf           UInt8,
  plan_chars        UInt32,

  sample_plan_json  String,                    -- ONE redacted exemplar, for citation.
                                               -- Already redacted upstream (jar); this
                                               -- table never sees raw plan text.
  first_seen        DateTime64(3),
  last_seen         DateTime64(3),
  indexed_at        DateTime64(3)
)
ENGINE = ReplacingMergeTree(indexed_at)
ORDER BY (plan_fingerprint, encoder_version)
TTL toDateTime(last_seen) + INTERVAL 365 DAY;

-- ── Three deliberate deviations from the v0.2 house pattern ──────────────────
--
-- 1. NO `PARTITION BY toYYYYMM(...)`.
--    spark_events partitions by month because it is an append-only time series.
--    plan_memory is a DIMENSION keyed by fingerprint: a single plan shape recurs
--    across many months, so monthly partitioning would shatter one logical row
--    across N parts and defeat the ReplacingMergeTree collapse.
--
-- 2. ReplacingMergeTree(indexed_at), not plain MergeTree.
--    Re-indexing must CONVERGE, mirroring engine's "re-analysis converges" rule.
--    Re-running the indexer replaces a fingerprint's row instead of duplicating it.
--    Reads still use `FINAL` or argMax -- replacement is asynchronous.
--
-- 3. TTL 365 DAY, deliberately LONGER than spark_events' 90 DAY.
--    This is the point of the lane: memory must OUTLIVE the raw events it was
--    derived from. At day 91 the stage rows are gone but the learned plan shape
--    and its outcome remain. Flagged explicitly because it is the one place this
--    lane intentionally disagrees with an existing retention choice.

-- ── Vector index: intentionally NOT in this DDL ──────────────────────────────
-- Verified live against this deployment (ClickHouse 24.8.14.39):
--   * cosineDistance(Array(Float32), Array(Float32))     -> works, no flag needed.
--   * vector_similarity('hnsw','cosineDistance')          -> works, TWO args only,
--     and only with allow_experimental_vector_similarity_index=1.
--     The 3-arg form documented for newer releases FAILS here:
--     "Vector similarity index must have two or six arguments."
-- At Apex's current scale (a few thousand distinct fingerprints) a brute-force
-- scan is exact, faster than HNSW build cost, and needs no experimental flag.
-- Add the index only when volume justifies it:
--
--   SET allow_experimental_vector_similarity_index = 1;
--   ALTER TABLE apex.plan_memory
--     ADD INDEX emb_idx embedding TYPE vector_similarity('hnsw','cosineDistance') GRANULARITY 1;
--   ALTER TABLE apex.plan_memory MATERIALIZE INDEX emb_idx SETTINGS mutations_sync = 2;
--
-- NOTE: an ANN index makes recall APPROXIMATE. Recall currently returns exact
-- top-k. Turning this on is a correctness-visible change, not just a speed knob.
