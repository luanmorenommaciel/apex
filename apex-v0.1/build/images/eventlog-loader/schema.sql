-- Single source of truth for the Spark observability schema.
-- The eventlog-loader embeds this file and applies every statement on each run
-- (CREATE TABLE IF NOT EXISTS), so a fresh ClickHouse data dir is not required.
-- Table names are unqualified; the loader connects with the target database set.
-- The loader also runs CREATE DATABASE IF NOT EXISTS for that target database
-- (see ensureDatabase in main.go) before applying this file, so the store is
-- fully bootstrapped regardless of the ClickHouse data-dir state.

CREATE TABLE IF NOT EXISTS spark_eventlog_files
(
    bucket String,
    object_key String,
    etag String,
    size UInt64,
    last_modified DateTime64(3, 'UTC'),
    line_count UInt64,
    ingested_at DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(ingested_at)
ORDER BY (bucket, object_key, etag);

CREATE TABLE IF NOT EXISTS spark_raw_events
(
    event_uid String,
    app_id String,
    event_type LowCardinality(String),
    event_time_ms UInt64,
    bucket String,
    object_key String,
    line_no UInt64,
    raw String,
    ingested_at DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(ingested_at)
ORDER BY (app_id, event_type, event_uid);

CREATE TABLE IF NOT EXISTS spark_sql_executions
(
    app_id String,
    execution_id UInt64,
    description String,
    details String,
    physical_plan String,
    start_time_ms UInt64,
    event_uid String,
    ingested_at DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(ingested_at)
ORDER BY (app_id, execution_id);

CREATE TABLE IF NOT EXISTS spark_sql_execution_ends
(
    app_id String,
    execution_id UInt64,
    end_time_ms UInt64,
    error_message String,
    event_uid String,
    ingested_at DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(ingested_at)
-- Natural key (one end per execution): dedups re-ingested rows regardless of
-- file position/event_uid, so compacted event logs collapse correctly.
ORDER BY (app_id, execution_id);

CREATE TABLE IF NOT EXISTS spark_stages
(
    app_id String,
    stage_id UInt64,
    stage_attempt_id UInt64,
    stage_name String,
    num_tasks UInt64,
    submission_time_ms UInt64,
    completion_time_ms UInt64,
    event_uid String,
    ingested_at DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(ingested_at)
ORDER BY (app_id, stage_id, stage_attempt_id);

CREATE TABLE IF NOT EXISTS spark_tasks
(
    app_id String,
    stage_id UInt64,
    stage_attempt_id UInt64,
    task_id UInt64,
    task_index UInt64,
    task_attempt UInt64,
    executor_id String,
    host String,
    launch_time_ms UInt64,
    finish_time_ms UInt64,
    duration_ms UInt64,
    task_type LowCardinality(String),
    successful UInt8,
    reason String,
    executor_run_time_ms UInt64,
    executor_cpu_time_ns UInt64,
    peak_execution_memory UInt64,
    input_bytes UInt64,
    input_records UInt64,
    output_bytes UInt64,
    output_records UInt64,
    shuffle_read_bytes UInt64,
    shuffle_write_bytes UInt64,
    shuffle_fetch_wait_ms UInt64,
    shuffle_write_time_ns UInt64,
    jvm_gc_time_ms UInt64,
    memory_bytes_spilled UInt64,
    disk_bytes_spilled UInt64,
    event_uid String,
    ingested_at DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(ingested_at)
-- Natural task key (NOT event_uid): a task is uniquely identified by
-- (stage, stage_attempt, task_id, task_attempt). Ordering by event_uid (a
-- position-in-file hash) let the SAME task re-appear from a compacted
-- (.compact) event log with a different uid and NOT collapse, double-counting
-- shuffle/GC/spill in every aggregation. The natural key dedups correctly.
ORDER BY (app_id, stage_id, stage_attempt_id, task_id, task_attempt);

CREATE TABLE IF NOT EXISTS spark_jobs
(
    app_id String,
    job_id UInt64,
    sql_execution_id Int64,
    submission_time_ms UInt64,
    completion_time_ms UInt64,
    result LowCardinality(String),
    num_stages UInt64,
    stage_ids Array(UInt64),
    event_uid String,
    ingested_at DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(ingested_at)
ORDER BY (app_id, job_id);

CREATE TABLE IF NOT EXISTS spark_sql_execution_jobs
(
    app_id String,
    execution_id UInt64,
    job_id UInt64,
    event_uid String,
    ingested_at DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(ingested_at)
ORDER BY (app_id, execution_id, job_id);

CREATE TABLE IF NOT EXISTS spark_sql_adaptive_plans
(
    app_id String,
    execution_id UInt64,
    physical_plan String,
    spark_plan_info String,
    event_uid String,
    ingested_at DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(ingested_at)
ORDER BY (app_id, execution_id, event_uid);

CREATE TABLE IF NOT EXISTS spark_diagnostic_reports
(
    app_id String,
    report_uid String,
    status LowCardinality(String),
    max_severity LowCardinality(String),
    findings_count UInt32,
    report_json String,
    llm_model String,
    generated_at DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(generated_at)
ORDER BY (app_id, report_uid);

-- Derived views for dashboards: individual SQL query latency requires joining
-- execution starts and ends, which chart builders cannot do over one table.
-- FINAL collapses any not-yet-merged ReplacingMergeTree duplicates so the join
-- never fans out; LEFT JOIN keeps still-running executions visible (a query
-- running for a long time is itself a useful signal) with a NULL duration.
-- IF NOT EXISTS (not OR REPLACE) keeps ensureSchema idempotent and race-free on
-- every loader run; to update this definition on an existing DB, DROP VIEW first.
CREATE VIEW IF NOT EXISTS spark_sql_execution_durations AS
SELECT
    s.app_id AS app_id,
    s.execution_id AS execution_id,
    s.start_time_ms AS start_time_ms,
    e.end_time_ms AS end_time_ms,
    if(e.end_time_ms > 0, e.end_time_ms - s.start_time_ms, NULL) AS duration_ms,
    coalesce(e.error_message, '') != '' AS has_error,
    s.description AS description
FROM spark_sql_executions AS s FINAL
LEFT JOIN spark_sql_execution_ends AS e FINAL
    ON e.app_id = s.app_id AND e.execution_id = s.execution_id;

-- Cached-block tracking: SparkListenerBlockUpdated events land in
-- spark_raw_events when spark.eventLog.logBlockUpdates.enabled=true (the
-- cache_heavy workload turns it on per-session). Normalized here as a view.
-- SparkListenerBlockUpdated carries no event timestamp in the Spark schema, so
-- event_time_ms is 0 for these rows; fall back to ingest time so the dashboard
-- time-axis is usable (approximate, not the true block-update instant) instead
-- of collapsing every block onto 1970-01-01.
CREATE VIEW IF NOT EXISTS spark_cache_blocks AS
SELECT
    app_id,
    if(event_time_ms > 0, event_time_ms, toUnixTimestamp64Milli(ingested_at)) AS event_time_ms,
    JSONExtractString(raw, 'Block Updated Info', 'Block ID') AS block_id,
    JSONExtractString(raw, 'Block Updated Info', 'Block Manager ID', 'Executor ID') AS executor_id,
    JSONExtractBool(raw, 'Block Updated Info', 'Storage Level', 'Use Memory') AS in_memory,
    JSONExtractBool(raw, 'Block Updated Info', 'Storage Level', 'Use Disk') AS on_disk,
    JSONExtractUInt(raw, 'Block Updated Info', 'Memory Size') AS memory_size,
    JSONExtractUInt(raw, 'Block Updated Info', 'Disk Size') AS disk_size
FROM spark_raw_events
WHERE event_type = 'SparkListenerBlockUpdated';

-- Migrations: CREATE TABLE IF NOT EXISTS above does not add columns to a
-- pre-existing spark_tasks table, so existing ClickHouse data dirs need these
-- ALTERs to pick up the GC/spill metrics. Idempotent and safe to re-run.
ALTER TABLE spark_tasks ADD COLUMN IF NOT EXISTS jvm_gc_time_ms UInt64 AFTER shuffle_write_bytes;
ALTER TABLE spark_tasks ADD COLUMN IF NOT EXISTS memory_bytes_spilled UInt64 AFTER jvm_gc_time_ms;
ALTER TABLE spark_tasks ADD COLUMN IF NOT EXISTS disk_bytes_spilled UInt64 AFTER memory_bytes_spilled;
ALTER TABLE spark_tasks ADD COLUMN IF NOT EXISTS shuffle_fetch_wait_ms UInt64 AFTER shuffle_write_bytes;
ALTER TABLE spark_tasks ADD COLUMN IF NOT EXISTS shuffle_write_time_ns UInt64 AFTER shuffle_fetch_wait_ms;
