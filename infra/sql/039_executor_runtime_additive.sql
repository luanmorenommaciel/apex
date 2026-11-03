-- Add Spark's measured executor wall-clock runtime in milliseconds. Historical
-- rows retain zero; ENGINE falls back to the attributes map for transitional
-- rows emitted before the typed column existed.

ALTER TABLE apex.spark_events
    ADD COLUMN IF NOT EXISTS executor_run_time_ms Int64 DEFAULT 0
        AFTER gc_time_ms;

-- The reshape MV picks these columns up in 040_mv_spark_events_resync.sql (one
-- in-place query replacement for every pre-existing volume), never here.
