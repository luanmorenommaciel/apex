-- Apex collect · apex.spark_events — CANONICAL contract schema.
-- Mirror of contract/spark_events.ddl.sql (do NOT redefine/repurpose columns here;
-- this lane only applies the frozen schema so the reshape MV has a target to write into).
-- The clickhouseexporter NEVER writes here directly (it can't map custom columns) —
-- mv_spark_events (see 30_mv_spark_events.sql) reshapes apex.otel_traces into this table.
-- v0.5 adds ~15 columns for retry-safe task analysis; all DEFAULT 0 for historical data.

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
  executor_run_time_ms      Int64 DEFAULT 0,      -- v0.5: Spark's measured executor wall-clock runtime
  input_bytes               Int64,
  output_bytes              Int64,
  peak_execution_mem_bytes  Int64,
  task_count                Int32,
  task_duration_p50_ms      Int64,
  task_duration_p99_ms      Int64,
  task_duration_max_ms      Int64 DEFAULT 0,      -- v0.5: tail-outlier visibility
  task_duration_sample_count Int32 DEFAULT 0,     -- v0.5: attempts with duration available
  successful_task_duration_p50_ms Int64 DEFAULT 0,    -- v0.5: retry-safe (one success per partition)
  successful_task_duration_p99_ms Int64 DEFAULT 0,    -- v0.5
  successful_task_duration_max_ms Int64 DEFAULT 0,    -- v0.5
  successful_task_sample_count Int32 DEFAULT 0,       -- v0.5: partitions with success observed
  successful_task_shuffle_read_bytes_p50 Int64 DEFAULT 0,    -- v0.5
  successful_task_shuffle_read_bytes_max Int64 DEFAULT 0,    -- v0.5
  successful_task_shuffle_read_bytes_sample_count Int32 DEFAULT 0, -- v0.5
  task_attempt_count        Int32 DEFAULT 0,      -- v0.5: all onTaskEnd events
  task_failed_attempt_count Int32 DEFAULT 0,      -- v0.5: TaskInfo.failed=true
  task_counted_failure_attempt_count Int32 DEFAULT 0, -- v0.5: scheduler budget (countTowardsTaskFailures)
  task_killed_attempt_count Int32 DEFAULT 0,      -- v0.5: TaskInfo.killed=true
  task_speculative_attempt_count Int32 DEFAULT 0, -- v0.5: speculative attempts
  plan_fingerprint          FixedString(64),      -- SHA-256 of normalized logical plan (64 hex chars)
  plan_json                 String,
  attributes                Map(String, String)   -- extensibility escape hatch
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (job_id, stage_id, stage_attempt)
SETTINGS non_replicated_deduplication_window = 100
TTL toDateTime(ts) + INTERVAL 90 DAY;
