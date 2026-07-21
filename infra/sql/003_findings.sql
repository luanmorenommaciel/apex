-- Apex infra · apex.findings — CANONICAL contract schema (contract/findings.ddl.sql).
-- Lane 5 (engine) WRITES; Lane 6 (serve) READS. infra only pre-creates it so the store
-- exposes the full contract surface and the E2E trace check (scripts/verify.sh) can join
-- spark_events -> spark_jobs_1m -> findings by job_id. Field names match the Finding object.
-- Applied verbatim from contract/ (only `IF NOT EXISTS` added). Never rename/repurpose a column.

CREATE TABLE IF NOT EXISTS apex.findings (
  finding_id     String,                 -- uuid
  job_id         String,
  stage_id       Int32,
  type           String,                 -- SKEW_ON_JOIN | SPILL | BAD_SHUFFLE | DRIVER_OOM | ...
  severity       Enum8('info'=1,'warning'=2,'critical'=3,'blocker'=4),
  evidence       String,                 -- "p99/p50 = 52.7x on customer_id"
  hot_key        String,                 -- "customer_id=12847" (or "")
  impact         String,                 -- "-38% runtime, -$211/run"
  fix            String,                 -- "enable AQE skew join"
  confidence     Enum8('LOW'=1,'MEDIUM'=2,'HIGH'=3),
  detected_by    String,                 -- "skew_watcher" | "correlation" | "judger"
  ts             DateTime64(3)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (job_id, severity, ts);
