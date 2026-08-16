-- Apex infra · apex.run_outcomes — RATIFIED contract v0.3 schema (CONTRACT.md changelog v0.3).
-- MIRROR of memory/sql/031_run_outcomes.sql (the lane owns this DDL; infra only applies it).
-- Applied verbatim (CREATE DATABASE dropped — 001_database.sql owns it). Never
-- rename/repurpose a column; if memory/ changes the source, this file is re-mirrored.
--
-- Grain: one row per (plan_fingerprint, job_id).
-- "This plan shape, in this run, under this config, performed thus."
--
-- Why this grain and not one-row-per-job: Spark config is an APPLICATION-level
-- setting, but performance is only interpretable per plan shape. Keying by
-- fingerprint first is what lets recall() answer the ZEST question -- "every
-- historical run of this shape" -- with a single prefix scan.

CREATE TABLE IF NOT EXISTS apex.run_outcomes (
  job_id            String,
  app_id            String DEFAULT '',
  app_name          String DEFAULT '',
  plan_fingerprint  FixedString(64),

  -- ── What it RAN WITH ───────────────────────────────────────────────────────
  -- The six parameters ZEST tunes (arXiv 2503.03826, Table 1), typed so the
  -- parameter-wise mean is a plain SQL avg() and a future ZEST-seeded row lands
  -- in the same columns with no translation.
  --
  -- Nullable is load-bearing, not laziness: "we never captured this" and "this
  -- was set to 0" are different facts. Collapsing them onto a 0 sentinel would
  -- silently drag every avg() toward zero and manufacture a confident-looking
  -- recommendation out of missing data. See config_source.
  conf_shuffle_partitions Nullable(Int32),     -- spark.sql.shuffle.partitions
  conf_executor_instances Nullable(Int32),     -- spark.executor.instances
  conf_executor_cores     Nullable(Int32),     -- spark.executor.cores
  conf_executor_memory_mb Nullable(Int32),     -- spark.executor.memory, normalised to MiB
  conf_driver_cores       Nullable(Int32),     -- spark.driver.cores
  conf_driver_memory_mb   Nullable(Int32),     -- spark.driver.memory,  normalised to MiB
  conf_extra              Map(String, String), -- any other spark.* observed, verbatim
  config_source     LowCardinality(String),    -- 'observed' | 'zest-seed' | 'unknown'
                                               -- 'unknown' is the ONLY honest value for
                                               -- every row Apex can produce today. See
                                               -- the open dependency note below.

  -- ── How it PERFORMED ───────────────────────────────────────────────────────
  -- 100% derivable from apex.spark_events today. No new emission required.
  stage_count              UInt32,
  task_count               UInt64,
  wall_clock_ms            Int64,   -- ts span of this shape's stages within the job
  task_time_ms             Int64,   -- sum(task_count * p50), the work proxy
  shuffle_read_bytes       Int64,
  shuffle_write_bytes      Int64,
  spill_disk_bytes         Int64,
  spill_mem_bytes          Int64,
  gc_time_ms               Int64,
  input_bytes              Int64,
  output_bytes             Int64,
  peak_execution_mem_bytes Int64,
  max_skew_ratio           Float32, -- max(p99 / nullIf(p50,0)) over this shape's stages

  -- Corroboration from the two v0.2 tables, denormalised so a recall() hit is
  -- one query and its evidence is self-contained.
  aqe_skew_splits   UInt16,                  -- plan_transitions, HIGH confidence only
  aqe_coalesces     UInt16,
  finding_count     UInt16,                  -- apex.findings for this job
  worst_severity    LowCardinality(String),  -- ''|info|warning|critical|blocker

  outcome_source    LowCardinality(String),  -- 'apex' | 'zest-seed'
  observed_at       DateTime64(3),
  indexed_at        DateTime64(3)
)
ENGINE = ReplacingMergeTree(indexed_at)
PARTITION BY toYYYYMM(observed_at)
ORDER BY (plan_fingerprint, job_id)   -- fingerprint FIRST: the hot path is
                                      -- "every run of this shape", the exact
                                      -- inverse of spark_events' (job_id, stage_id)
TTL toDateTime(observed_at) + INTERVAL 365 DAY;

-- ── OPEN DEPENDENCY (the honest part) ────────────────────────────────────────
-- Verified against the live store: Apex captures NO Spark configuration at all.
--   SELECT count() FROM apex.spark_events
--    WHERE arrayExists(x -> position(x,'spark.')>0, mapKeys(attributes));  -- 0
-- `attributes` currently just mirrors the typed columns; it holds no spark.* keys.
--
-- Consequence: every row this lane can write today has config_source='unknown'
-- and six NULL config columns. run_outcomes is therefore fully useful as an
-- OUTCOME/evidence store immediately, but `best_known_config` cannot be
-- populated from Apex's own history until config is emitted.
--
-- Closing it is a JAR-lane change (not this lane's to make): emit the resolved
-- SparkConf subset once per application. Proposed as a v0.3 companion item.
-- Until then recall() returns best_known_config = null with an explicit
-- `config_unavailable` reason rather than inventing one.
