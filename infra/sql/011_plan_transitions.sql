-- Apex infra · apex.plan_transitions — CANONICAL contract v0.2 schema
-- (contract/plan_transitions.ddl.sql). One row per AQE runtime re-plan — Spark's OWN
-- optimization decision captured as ground truth (the $0 signal that beats DataFlint).
-- Reshaped from apex.otel_traces (SpanName='apex.plan_transition') by mv_plan_transitions.
-- Applied verbatim from contract/ (only formatting). Never rename/repurpose a column.

CREATE TABLE IF NOT EXISTS apex.plan_transitions
(
    job_id          String,                    -- = applicationId (constant, always present)
    execution_id    Int64,                     -- SQL execution id (AQE's correlation key)
    update_seq      Int32,                     -- monotonic per execution_id (0,1,2… as AQE re-plans)
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
