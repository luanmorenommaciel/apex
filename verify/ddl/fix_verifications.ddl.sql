-- Contract v0.3 (additive) · apex.fix_verifications — RATIFIED
-- (CONTRACT.md changelog v0.3; rationale in verify/CONTRACT-EXTENSION-v0.3.md).
-- `infra` owns applying this to the store ("infra owns application, contract
-- owns the schema"); until it is applied to a cluster, the verify lane writes
-- to a local database (default `apex_verify_local`).
--
-- One row per (finding, proposed_config) verification attempt. `verify` writes;
-- `serve` reads (suggest_fix joins it on finding_id to strengthen its rationale).
-- Rule, per CONTRACT.md: a lane may ADD a column; never rename or repurpose.

CREATE DATABASE IF NOT EXISTS apex;

CREATE TABLE apex.fix_verifications (
  -- ── identity ────────────────────────────────────────────────────────────
  verification_id   String,                    -- uuid, one per attempt
  finding_id        String,                    -- FK → apex.findings.finding_id
  job_id            String,                    -- the OBSERVED run the finding came from
  app_id            String DEFAULT '',         -- mirrors findings.app_id

  -- ── what was evaluated ──────────────────────────────────────────────────
  proposed_config   String,                    -- canonical JSON of the Spark conf overlay
                                               -- under test, e.g. {"spark.sql.shuffle.partitions":"200"}
                                               -- Spark conf keys/values only — never data, never a path.
  method            LowCardinality(String),    -- predicted | replayed | refused
                                               --   predicted = analytic only, nothing executed
                                               --   replayed  = measured on the synthetic bench
                                               --   refused   = not verifiable (unsafe / no-op / no bench)
  predictor         LowCardinality(String),    -- amdahl_tail_share | partition_sizing | noop_gate | none

  -- ── the prediction (always present; this lane never returns a bare guess) ─
  predicted_delta_pct   Float32,               -- SIGNED job-runtime change. negative = faster.
  -- Interval bounds, NUMERICALLY ordered: low <= delta <= high. Because negative
  -- means faster, `low` is the MOST improvement and `high` the LEAST. Naming them
  -- by numeric order (not by optimism) keeps the invariant checkable in SQL.
  predicted_low_pct     Float32,
  predicted_high_pct    Float32,

  -- ── the measurement (NULL ⇒ not measured; 0.0 ⇒ measured, no change) ─────
  measured_delta_pct    Nullable(Float32),
  baseline_ms           Nullable(Float64),     -- median of the baseline arm
  treatment_ms          Nullable(Float64),     -- median of the treatment arm
  noise_floor_pct       Nullable(Float32),     -- run-to-run CV of the BASELINE arm.
                                               -- |measured_delta_pct| below this is reported as
                                               -- "indistinguishable from zero", never as a number.
  replay_reps           UInt8 DEFAULT 0,       -- repetitions PER ARM (0 ⇒ no replay)
  bench                 String DEFAULT '',     -- e.g. "dev:skew_join" — the synthetic bench used
  shape_fidelity        Float32 DEFAULT 0,     -- 0–1: how well the bench reproduces the observed
                                               -- shape (task count, skew ratio, shuffle magnitude).
                                               -- Low fidelity caps confidence — a replay of the
                                               -- wrong shape is not evidence.

  -- ── the safety gate (OptiSpark-derived; see § Safety in the proposal) ────
  safe                  UInt8,                 -- 0/1. 0 ⇒ nothing was executed.
  safety_verdict        LowCardinality(String),-- allow | block_size | block_ast | block_no_bench | not_applicable
  safety_detail         String DEFAULT '',     -- e.g. "optimizedPlan.stats.sizeInBytes=8.0 EiB (unknown)"

  -- ── the verdict ─────────────────────────────────────────────────────────
  confidence        Enum8('LOW'=1,'MEDIUM'=2,'HIGH'=3),   -- human-facing tier (same ladder as findings)
  confidence_score  Float32 DEFAULT 0,         -- raw 0–1, same convention as findings.confidence_score
  evidence          String,                    -- human-readable derivation. Apex-authored, not job-authored.
  caveats           String DEFAULT '',         -- what would falsify this verdict

  -- ── provenance ──────────────────────────────────────────────────────────
  verify_version    LowCardinality(String) DEFAULT '',     -- verify lane version that produced the row
  verified_at       DateTime64(3)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(verified_at)
ORDER BY (job_id, finding_id, verified_at);
