-- Additive retry/speculation semantics for existing ClickHouse volumes.

ALTER TABLE apex.spark_events
    ADD COLUMN IF NOT EXISTS task_duration_sample_count Int32 DEFAULT 0
        AFTER task_duration_max_ms,
    ADD COLUMN IF NOT EXISTS task_killed_attempt_count Int32 DEFAULT 0
        AFTER task_failed_attempt_count;

-- The reshape MV picks these columns up in 040_mv_spark_events_resync.sql (one
-- in-place query replacement for every pre-existing volume), never here.
