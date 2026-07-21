-- Apex infra · job-level rollup — AggregatingMergeTree target + incremental MV.
--
-- WHY: stage rows in spark_events are fine for point queries, but HyperDX time tiles and the
-- rollup skew query want per-(minute, job) summaries. This rolls stage rows up to 1-minute
-- buckets. We store quantile SKETCHES (quantilesState), NOT finalized values, so any percentile
-- (p50, p95, p99, ...) is recoverable later from one state via quantilesMerge.
--
-- CONVENTIONS (do not deviate — HyperDX auto-acceleration maps queries to MV columns by these):
--   * column naming  <aggFn>__<sourceColumn>   e.g. sum__shuffle_read_bytes, quantiles__task_duration_p99_ms
--   * 1-minute buckets (toStartOfMinute) — composes with 15-min charts; NEVER 10-min.
--   * source types are Int64 (contract) -> the state/simple-agg types are Int64 to match.
--
-- ⚠️ Incremental MVs are BETA and NOT backfilled: spark_jobs_1m only contains rows inserted
--    into spark_events AFTER this MV exists. No POPULATE (can miss rows). When registering in
--    HyperDX set the source "min date" = min(ts). Backfill manually if needed (see README).

CREATE TABLE IF NOT EXISTS apex.spark_jobs_1m (
  bucket                          DateTime,
  job_id                          String,
  app_id                          String,
  count__                         AggregateFunction(count),
  sum__shuffle_read_bytes         SimpleAggregateFunction(sum, Int64),
  sum__shuffle_write_bytes        SimpleAggregateFunction(sum, Int64),
  sum__spill_disk_bytes           SimpleAggregateFunction(sum, Int64),
  sum__spill_mem_bytes            SimpleAggregateFunction(sum, Int64),
  sum__input_bytes                SimpleAggregateFunction(sum, Int64),
  sum__output_bytes               SimpleAggregateFunction(sum, Int64),
  max__gc_time_ms                 SimpleAggregateFunction(max, Int64),
  max__peak_execution_mem_bytes   SimpleAggregateFunction(max, Int64),
  quantiles__task_duration_p50_ms AggregateFunction(quantiles(0.5, 0.99), Int64),
  quantiles__task_duration_p99_ms AggregateFunction(quantiles(0.5, 0.99), Int64)
)
ENGINE = AggregatingMergeTree
PARTITION BY toYYYYMM(bucket)
ORDER BY (bucket, job_id, app_id)
TTL bucket + INTERVAL 90 DAY;

CREATE MATERIALIZED VIEW IF NOT EXISTS apex.spark_jobs_1m_mv TO apex.spark_jobs_1m AS
SELECT
  toStartOfMinute(ts)                              AS bucket,
  job_id,
  app_id,
  countState()                                     AS count__,
  sumSimpleState(shuffle_read_bytes)               AS sum__shuffle_read_bytes,
  sumSimpleState(shuffle_write_bytes)              AS sum__shuffle_write_bytes,
  sumSimpleState(spill_disk_bytes)                 AS sum__spill_disk_bytes,
  sumSimpleState(spill_mem_bytes)                  AS sum__spill_mem_bytes,
  sumSimpleState(input_bytes)                      AS sum__input_bytes,
  sumSimpleState(output_bytes)                     AS sum__output_bytes,
  maxSimpleState(gc_time_ms)                       AS max__gc_time_ms,
  maxSimpleState(peak_execution_mem_bytes)         AS max__peak_execution_mem_bytes,
  quantilesState(0.5, 0.99)(task_duration_p50_ms)  AS quantiles__task_duration_p50_ms,
  quantilesState(0.5, 0.99)(task_duration_p99_ms)  AS quantiles__task_duration_p99_ms
FROM apex.spark_events
GROUP BY bucket, job_id, app_id;
