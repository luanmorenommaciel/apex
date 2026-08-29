-- Add the exact Spark scheduler failure-budget signal without reinterpreting
-- task_failed_attempt_count. The view is modified in place to keep ingestion live.

ALTER TABLE apex.spark_events
    ADD COLUMN IF NOT EXISTS task_counted_failure_attempt_count Int32 DEFAULT 0
        AFTER task_failed_attempt_count;

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
