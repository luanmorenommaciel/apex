-- Existing-volume migration for ClickHouse 26.1 async-insert/MV deduplication.
--
-- Fresh volumes already receive these settings from the canonical DDL. This
-- additive migration aligns volumes created before R8. It does not enable the
-- query-level async_insert settings; those belong to the Collector endpoint.

ALTER TABLE apex.otel_traces
  MODIFY SETTING non_replicated_deduplication_window = 100;
ALTER TABLE apex.otel_traces_trace_id_ts
  MODIFY SETTING non_replicated_deduplication_window = 100;
ALTER TABLE apex.spark_events
  MODIFY SETTING non_replicated_deduplication_window = 100;
ALTER TABLE apex.plan_transitions
  MODIFY SETTING non_replicated_deduplication_window = 100;
ALTER TABLE apex.spark_jobs_1m
  MODIFY SETTING non_replicated_deduplication_window = 100;
