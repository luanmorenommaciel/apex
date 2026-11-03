-- Add the exact Spark scheduler failure-budget signal without reinterpreting
-- task_failed_attempt_count.

ALTER TABLE apex.spark_events
    ADD COLUMN IF NOT EXISTS task_counted_failure_attempt_count Int32 DEFAULT 0
        AFTER task_failed_attempt_count;

-- The reshape MV picks these columns up in 040_mv_spark_events_resync.sql (one
-- in-place query replacement for every pre-existing volume), never here.
