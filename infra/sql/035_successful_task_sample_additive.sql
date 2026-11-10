-- Additive migration for retry-safe task-duration analysis.
-- Legacy duration columns retain their original all-attempt semantics.
ALTER TABLE apex.spark_events
    ADD COLUMN IF NOT EXISTS successful_task_duration_p50_ms Int64 DEFAULT 0
        AFTER task_duration_max_ms,
    ADD COLUMN IF NOT EXISTS successful_task_duration_p99_ms Int64 DEFAULT 0
        AFTER successful_task_duration_p50_ms,
    ADD COLUMN IF NOT EXISTS successful_task_duration_max_ms Int64 DEFAULT 0
        AFTER successful_task_duration_p99_ms,
    ADD COLUMN IF NOT EXISTS successful_task_sample_count Int32 DEFAULT 0
        AFTER successful_task_duration_max_ms,
    ADD COLUMN IF NOT EXISTS task_attempt_count Int32 DEFAULT 0
        AFTER successful_task_sample_count,
    ADD COLUMN IF NOT EXISTS task_failed_attempt_count Int32 DEFAULT 0
        AFTER task_attempt_count,
    ADD COLUMN IF NOT EXISTS task_speculative_attempt_count Int32 DEFAULT 0
        AFTER task_failed_attempt_count;

-- The reshape MV picks these columns up in 040_mv_spark_events_resync.sql (one
-- in-place query replacement for every pre-existing volume), never here.
