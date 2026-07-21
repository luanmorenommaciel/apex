-- Apex collect · mv_plan_transitions — reshape apex.otel_traces -> apex.plan_transitions.
--
-- The v0.2 AQE-decision signal. jar emits a distinct span named 'apex.plan_transition'
-- alongside 'apex.stage'; both land in otel_traces and this MV routes+flattens the
-- plan_transition spans into the contract v0.2 table. All descriptors (detail/before/after)
-- are already redacted in-JVM (no literals) — passed through opaquely.

CREATE MATERIALIZED VIEW IF NOT EXISTS apex.mv_plan_transitions TO apex.plan_transitions AS
SELECT
  SpanAttributes['job_id']                                   AS job_id,
  toInt64OrZero(SpanAttributes['execution_id'])              AS execution_id,
  toInt32OrZero(SpanAttributes['update_seq'])                AS update_seq,
  SpanAttributes['transition_type']                          AS transition_type,
  SpanAttributes['detail']                                   AS detail,
  SpanAttributes['before']                                   AS before,
  SpanAttributes['after']                                    AS after,
  SpanAttributes['confidence']                               AS confidence,
  fromUnixTimestamp64Milli(toInt64OrZero(SpanAttributes['ts'])) AS ts
FROM apex.otel_traces
WHERE SpanName = 'apex.plan_transition'
  AND SpanAttributes['job_id'] != '';
