-- Apex collect · mv_spark_events — reshape apex.otel_traces -> apex.spark_events.
--
-- WHY THIS EXISTS: the clickhouseexporter INSERT is bound to fixed OTLP columns
-- (Timestamp, TraceId, SpanName, SpanAttributes, ...) and CANNOT target custom columns
-- like shuffle_read_bytes. So spans land in otel_traces and this MV flattens the
-- snake_case SpanAttributes (contract §"telemetry event") into typed contract columns.
--
-- Filters to SpanName='apex.stage' so plan_transition spans are NOT reshaped here.
-- ts: the contract event ts is epoch-millis, carried on the span attribute 'ts'.
-- plan_fingerprint: opaque, computed upstream (Lane 2) — passed through, never recomputed.
-- v0.5 adds ~15 columns for retry-safe task analysis.

CREATE MATERIALIZED VIEW IF NOT EXISTS apex.mv_spark_events TO apex.spark_events AS
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
