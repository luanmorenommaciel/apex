-- Apex collect · apex.spark_events — CANONICAL contract schema.
-- Mirror of contract/spark_events.ddl.sql (do NOT redefine/repurpose columns here;
-- this lane only applies the frozen schema so the reshape MV has a target to write into).
-- The clickhouseexporter NEVER writes here directly (it can't map custom columns) —
-- mv_spark_events (see 30_mv_spark_events.sql) reshapes apex.otel_traces into this table.

CREATE TABLE IF NOT EXISTS apex.spark_events (
  job_id                    String,
  app_id                    String,
  app_name                  String,
  stage_id                  Int32,
  stage_attempt             Int32,
  ts                        DateTime64(3),
  shuffle_read_bytes        Int64,
  shuffle_write_bytes       Int64,
  spill_disk_bytes          Int64,
  spill_mem_bytes           Int64,
  gc_time_ms                Int64,
  input_bytes               Int64,
  output_bytes              Int64,
  peak_execution_mem_bytes  Int64,
  task_count                Int32,
  task_duration_p50_ms      Int64,
  task_duration_p99_ms      Int64,
  plan_fingerprint          FixedString(64),      -- SHA-256 of normalized logical plan (64 hex chars)
  plan_json                 String,
  attributes                Map(String, String)   -- extensibility escape hatch
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (job_id, stage_id, stage_attempt)
TTL toDateTime(ts) + INTERVAL 90 DAY;
