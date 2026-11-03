-- Additive migration for tail-outlier visibility on existing ClickHouse volumes.
-- Existing rows receive zero; no stored telemetry is rewritten or deleted.
ALTER TABLE apex.spark_events
    ADD COLUMN IF NOT EXISTS task_duration_max_ms Int64 DEFAULT 0
    AFTER task_duration_p99_ms;

-- The reshape MV picks these columns up in 040_mv_spark_events_resync.sql (one
-- in-place query replacement for every pre-existing volume), never here.
