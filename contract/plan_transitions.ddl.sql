-- Apex contract v0.2 — AQE runtime plan-transition capture.
-- ADDITIVE: does not alter spark_events or findings.
-- One row per AQE re-plan (SparkListenerSQLAdaptiveExecutionUpdate, diffed per execution_id).
-- This is Spark's OWN optimization decision, captured as ground truth — the signal that
-- turns a heuristic skew finding (p99/p50 ratio + LLM) into a $0 ground-truth finding.

CREATE DATABASE IF NOT EXISTS apex;

CREATE TABLE IF NOT EXISTS apex.plan_transitions
(
    job_id          String,                    -- = applicationId (constant, always present)
    execution_id    Int64,                     -- SQL execution id (AQE's correlation key)
    update_seq      Int32,                     -- monotonic per execution_id (0,1,2… as AQE re-plans)
    transition_type LowCardinality(String),    -- join_switch | skew_split | coalesce | local_read | other
    detail          String,                    -- structured descriptor, e.g. "SortMergeJoin->BroadcastHashJoin" (REDACTED, no literals)
    before          String,                    -- prior structural descriptor (redacted)
    after           String,                    -- new structural descriptor (redacted)
    confidence      LowCardinality(String),    -- HIGH (node-type delta / AQEShuffleRead) | BEST_EFFORT (parsed counts)
    ts              DateTime64(3)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (job_id, execution_id, update_seq)
TTL toDateTime(ts) + INTERVAL 90 DAY DELETE
SETTINGS ttl_only_drop_parts = 1;
