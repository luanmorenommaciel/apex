-- Lane 0 — Frozen Contract · apex.findings
-- Canonical DDL per docs/CONTRACT-FULL.md §2.2. One row per detected issue.
-- Lane 5 (engine) writes; Lane 6 (serve) reads. Field names match the Finding
-- object (§3) exactly. Rule: a lane may ADD a column; never rename or repurpose.

CREATE DATABASE IF NOT EXISTS apex;

CREATE TABLE apex.findings (
  finding_id       String,                 -- uuid
  job_id           String,
  app_id           String DEFAULT '',      -- v0.2 additive: engine holds it in-memory; persist for joins
  stage_id         Int32,
  type             String,                 -- SKEW_ON_JOIN | SPILL | BAD_SHUFFLE | DRIVER_OOM | ...
  severity         Enum8('info'=1,'warning'=2,'critical'=3,'blocker'=4),
  evidence         String,                 -- "p99/p50 = 52.7x on customer_id"
  hot_key          String,                 -- "customer_id=12847" (nullable-ish, "")
  impact           String,                 -- "-38% runtime, -$211/run"
  fix              String,                 -- "enable AQE skew join"
  confidence       Enum8('LOW'=1,'MEDIUM'=2,'HIGH'=3),  -- human-facing tier (drives the display)
  confidence_score Float32 DEFAULT 0,      -- v0.2 additive: raw 0–1 that engine's gate uses + serve's compare_runs reads
  detected_by      String,                 -- "skew_watcher" | "correlation" | "judger"
  ts               DateTime64(3)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (job_id, severity, ts);
