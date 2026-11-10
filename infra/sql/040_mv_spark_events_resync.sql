-- Apex infra · mv_spark_events resync — the ONE in-place query replacement for volumes
-- that predate any of the additive migrations 034–039.
--
-- Fresh volumes get this exact SELECT from 020_mv_reshape.sql at initdb; on those this
-- ALTER is a no-op. Pre-existing volumes got their columns from 034–039 (ADD COLUMN only)
-- and pick up the reshape here. ClickHouse 24.8 replaces the query in place, so ingestion
-- stays attached and no DROP VIEW opens an unobserved window.
--
-- This SELECT must stay byte-equal (whitespace aside) to 020 and to collect/ddl/30 —
-- tests/infra/test_mv_single_query.py enforces it. When the contract adds a column:
-- ADD COLUMN in a new additive file, then update collect/ddl/30, 020 and this file together.

ALTER TABLE apex.mv_spark_events MODIFY QUERY
SELECT
  SpanAttributes['job_id']                                      AS job_id,
  SpanAttributes['app_id']                                      AS app_id,
  SpanAttributes['app_name']                                    AS app_name,
  toInt32OrZero(SpanAttributes['stage_id'])                     AS stage_id,
  toInt32OrZero(SpanAttributes['stage_attempt'])                AS stage_attempt,
  fromUnixTimestamp64Milli(toInt64OrZero(SpanAttributes['ts'])) AS ts,
  toInt64OrZero(SpanAttributes['shuffle_read_bytes'])           AS shuffle_read_bytes,
  toInt64OrZero(SpanAttributes['shuffle_write_bytes'])          AS shuffle_write_bytes,
  toInt64OrZero(SpanAttributes['spill_disk_bytes'])             AS spill_disk_bytes,
  toInt64OrZero(SpanAttributes['spill_mem_bytes'])              AS spill_mem_bytes,
  toInt64OrZero(SpanAttributes['gc_time_ms'])                   AS gc_time_ms,
  toInt64OrZero(SpanAttributes['executor_run_time_ms'])         AS executor_run_time_ms,
  toInt64OrZero(SpanAttributes['input_bytes'])                  AS input_bytes,
  toInt64OrZero(SpanAttributes['output_bytes'])                 AS output_bytes,
  toInt64OrZero(SpanAttributes['peak_execution_mem_bytes'])     AS peak_execution_mem_bytes,
  toInt32OrZero(SpanAttributes['task_count'])                   AS task_count,
  toInt64OrZero(SpanAttributes['task_duration_p50_ms'])         AS task_duration_p50_ms,
  toInt64OrZero(SpanAttributes['task_duration_p99_ms'])         AS task_duration_p99_ms,
  toInt64OrZero(SpanAttributes['task_duration_max_ms'])         AS task_duration_max_ms,
  toInt32OrZero(SpanAttributes['task_duration_sample_count'])   AS task_duration_sample_count,
  toInt64OrZero(SpanAttributes['successful_task_duration_p50_ms']) AS successful_task_duration_p50_ms,
  toInt64OrZero(SpanAttributes['successful_task_duration_p99_ms']) AS successful_task_duration_p99_ms,
  toInt64OrZero(SpanAttributes['successful_task_duration_max_ms']) AS successful_task_duration_max_ms,
  toInt32OrZero(SpanAttributes['successful_task_sample_count']) AS successful_task_sample_count,
  toInt64OrZero(SpanAttributes['successful_task_shuffle_read_bytes_p50']) AS successful_task_shuffle_read_bytes_p50,
  toInt64OrZero(SpanAttributes['successful_task_shuffle_read_bytes_max']) AS successful_task_shuffle_read_bytes_max,
  toInt32OrZero(SpanAttributes['successful_task_shuffle_read_bytes_sample_count']) AS successful_task_shuffle_read_bytes_sample_count,
  toInt32OrZero(SpanAttributes['task_attempt_count'])           AS task_attempt_count,
  toInt32OrZero(SpanAttributes['task_failed_attempt_count'])    AS task_failed_attempt_count,
  toInt32OrZero(SpanAttributes['task_counted_failure_attempt_count']) AS task_counted_failure_attempt_count,
  toInt32OrZero(SpanAttributes['task_killed_attempt_count'])    AS task_killed_attempt_count,
  toInt32OrZero(SpanAttributes['task_speculative_attempt_count']) AS task_speculative_attempt_count,
  toFixedString(SpanAttributes['plan_fingerprint'], 64)         AS plan_fingerprint,
  SpanAttributes['plan_json']                                   AS plan_json,
  CAST(SpanAttributes, 'Map(String, String)')                   AS attributes
FROM apex.otel_traces
WHERE SpanName = 'apex.stage'
  AND SpanAttributes['job_id'] != '';
