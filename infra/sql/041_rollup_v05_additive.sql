-- Apex infra · spark_jobs_1m v0.5 columns, additive (existing volumes).
--
-- Fresh volumes get these columns from 004_rollup_mv.sql at initdb. A volume that
-- predates them gets them here: every ADD COLUMN appends in the same order 004 declares,
-- so SHOW CREATE converges on both paths, and the MV query is replaced in place
-- (no DROP VIEW, no unobserved ingestion window). Existing rows read as empty states.
-- The SELECT below must stay identical to 004's (tests/infra/test_rollup_v05_columns.py).

ALTER TABLE apex.spark_jobs_1m
    ADD COLUMN IF NOT EXISTS sum__task_count SimpleAggregateFunction(sum, Int64),
    ADD COLUMN IF NOT EXISTS sum__executor_run_time_ms SimpleAggregateFunction(sum, Int64),
    ADD COLUMN IF NOT EXISTS max__task_duration_max_ms SimpleAggregateFunction(max, Int64),
    ADD COLUMN IF NOT EXISTS sum__task_duration_sample_count SimpleAggregateFunction(sum, Int64),
    ADD COLUMN IF NOT EXISTS quantilesIf__successful_task_duration_p50_ms AggregateFunction(quantilesIf(0.5, 0.99), Int64, UInt8),
    ADD COLUMN IF NOT EXISTS quantilesIf__successful_task_duration_p99_ms AggregateFunction(quantilesIf(0.5, 0.99), Int64, UInt8),
    ADD COLUMN IF NOT EXISTS max__successful_task_duration_max_ms SimpleAggregateFunction(max, Int64),
    ADD COLUMN IF NOT EXISTS sum__successful_task_sample_count SimpleAggregateFunction(sum, Int64),
    ADD COLUMN IF NOT EXISTS quantilesIf__successful_task_shuffle_read_bytes_p50 AggregateFunction(quantilesIf(0.5, 0.99), Int64, UInt8),
    ADD COLUMN IF NOT EXISTS max__successful_task_shuffle_read_bytes_max SimpleAggregateFunction(max, Int64),
    ADD COLUMN IF NOT EXISTS sum__successful_task_shuffle_read_bytes_sample_count SimpleAggregateFunction(sum, Int64),
    ADD COLUMN IF NOT EXISTS sum__task_attempt_count SimpleAggregateFunction(sum, Int64),
    ADD COLUMN IF NOT EXISTS sum__task_failed_attempt_count SimpleAggregateFunction(sum, Int64),
    ADD COLUMN IF NOT EXISTS sum__task_counted_failure_attempt_count SimpleAggregateFunction(sum, Int64),
    ADD COLUMN IF NOT EXISTS sum__task_killed_attempt_count SimpleAggregateFunction(sum, Int64),
    ADD COLUMN IF NOT EXISTS sum__task_speculative_attempt_count SimpleAggregateFunction(sum, Int64);

ALTER TABLE apex.spark_jobs_1m_mv MODIFY QUERY
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
  quantilesState(0.5, 0.99)(task_duration_p99_ms)  AS quantiles__task_duration_p99_ms,
  sumSimpleState(toInt64(task_count))                                                                                      AS sum__task_count,
  sumSimpleState(executor_run_time_ms)                                                                                     AS sum__executor_run_time_ms,
  maxSimpleState(task_duration_max_ms)                                                                                     AS max__task_duration_max_ms,
  sumSimpleState(toInt64(task_duration_sample_count))                                                                      AS sum__task_duration_sample_count,
  quantilesIfState(0.5, 0.99)(successful_task_duration_p50_ms, successful_task_sample_count > 0)                           AS quantilesIf__successful_task_duration_p50_ms,
  quantilesIfState(0.5, 0.99)(successful_task_duration_p99_ms, successful_task_sample_count > 0)                           AS quantilesIf__successful_task_duration_p99_ms,
  maxSimpleState(successful_task_duration_max_ms)                                                                          AS max__successful_task_duration_max_ms,
  sumSimpleState(toInt64(successful_task_sample_count))                                                                    AS sum__successful_task_sample_count,
  quantilesIfState(0.5, 0.99)(successful_task_shuffle_read_bytes_p50, successful_task_shuffle_read_bytes_sample_count > 0) AS quantilesIf__successful_task_shuffle_read_bytes_p50,
  maxSimpleState(successful_task_shuffle_read_bytes_max)                                                                   AS max__successful_task_shuffle_read_bytes_max,
  sumSimpleState(toInt64(successful_task_shuffle_read_bytes_sample_count))                                                 AS sum__successful_task_shuffle_read_bytes_sample_count,
  sumSimpleState(toInt64(task_attempt_count))                                                                              AS sum__task_attempt_count,
  sumSimpleState(toInt64(task_failed_attempt_count))                                                                       AS sum__task_failed_attempt_count,
  sumSimpleState(toInt64(task_counted_failure_attempt_count))                                                              AS sum__task_counted_failure_attempt_count,
  sumSimpleState(toInt64(task_killed_attempt_count))                                                                       AS sum__task_killed_attempt_count,
  sumSimpleState(toInt64(task_speculative_attempt_count))                                                                  AS sum__task_speculative_attempt_count
FROM apex.spark_events
GROUP BY bucket, job_id, app_id;
