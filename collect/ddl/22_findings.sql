-- Apex collect · apex.findings — CANONICAL contract schema.
-- Mirror of contract/findings.ddl.sql. Lane 5 (engine) writes, Lane 6 (serve) reads.
-- collect does NOT write this table; it is pre-created here only so the local test
-- instance has the full contract surface (SHOW TABLES FROM apex lists all four).

CREATE TABLE IF NOT EXISTS apex.findings (
  finding_id     String,                 -- uuid
  job_id         String,
  stage_id       Int32,
  type           String,                 -- SKEW_ON_JOIN | SPILL | BAD_SHUFFLE | DRIVER_OOM | ...
  severity       Enum8('info'=1,'warning'=2,'critical'=3,'blocker'=4),
  evidence       String,
  hot_key        String,
  impact         String,
  fix            String,
  confidence     Enum8('LOW'=1,'MEDIUM'=2,'HIGH'=3),
  detected_by    String,
  ts             DateTime64(3)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (job_id, severity, ts);
