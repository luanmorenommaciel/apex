-- Apex collect · apex.plan_transitions — CANONICAL contract v0.2 schema.
-- Mirror of contract/plan_transitions.ddl.sql. One row per AQE re-plan.
-- Reshaped from apex.otel_traces (span name 'apex.plan_transition') by mv_plan_transitions.

CREATE TABLE IF NOT EXISTS apex.plan_transitions
(
    job_id          String,                    -- = applicationId (constant, always present)
    execution_id    Int64,                     -- SQL execution id (AQE's correlation key)
    update_seq      Int32,                     -- monotonic per execution_id (0,1,2…)
    transition_type LowCardinality(String),    -- join_switch | skew_split | coalesce | local_read | other
    detail          String,                    -- structured descriptor (REDACTED, no literals)
    before          String,                    -- prior structural descriptor (redacted)
    after           String,                    -- new structural descriptor (redacted)
    confidence      LowCardinality(String),    -- HIGH | BEST_EFFORT
    ts              DateTime64(3)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (job_id, execution_id, update_seq)
TTL toDateTime(ts) + INTERVAL 90 DAY DELETE
SETTINGS ttl_only_drop_parts = 1;
