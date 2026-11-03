-- Additive successful-task shuffle-read distribution for existing volumes.

ALTER TABLE apex.spark_events
    ADD COLUMN IF NOT EXISTS successful_task_shuffle_read_bytes_p50 Int64 DEFAULT 0
        AFTER successful_task_sample_count,
    ADD COLUMN IF NOT EXISTS successful_task_shuffle_read_bytes_max Int64 DEFAULT 0
        AFTER successful_task_shuffle_read_bytes_p50,
    ADD COLUMN IF NOT EXISTS successful_task_shuffle_read_bytes_sample_count Int32 DEFAULT 0
        AFTER successful_task_shuffle_read_bytes_max;

-- The reshape MV picks these columns up in 040_mv_spark_events_resync.sql (one
-- in-place query replacement for every pre-existing volume), never here.
