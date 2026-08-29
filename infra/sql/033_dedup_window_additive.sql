-- Apex infra · non-replicated deduplication window, additive.
--
-- Pairs with the Collector's exporter config (async_insert=0 +
-- deduplicate_blocks_in_dependent_materialized_views=1): ClickHouse 24.8
-- rejects that combination when async_insert=1, and without a dedup
-- window a retry_on_failure resend duplicates the row in otel_traces and
-- inflates every downstream non-argMax aggregate (spark_jobs_1m rollup,
-- sql/005 skew query, run_outcomes, memory lane). Applying the window to
-- source and target keeps a retried block from landing twice; genuinely
-- distinct blocks are unaffected (block hash, not row content).
--
-- Existing-volume migration. Fresh volumes should carry this setting in
-- their canonical DDL going forward.

ALTER TABLE apex.otel_traces
    MODIFY SETTING non_replicated_deduplication_window = 100;

ALTER TABLE apex.spark_events
    MODIFY SETTING non_replicated_deduplication_window = 100;

ALTER TABLE apex.plan_transitions
    MODIFY SETTING non_replicated_deduplication_window = 100;

ALTER TABLE apex.spark_jobs_1m
    MODIFY SETTING non_replicated_deduplication_window = 100;
