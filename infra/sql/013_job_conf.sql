-- Apex infra · apex.job_conf — PROPOSED contract v0.4 schema
-- (contract/job_conf.ddl.sql, awaiting central ratification). One row per
-- application run: the resolved, allowlisted SparkConf subset ("the config that
-- worked" for memory/, the NO-OP gate input for verify/).
-- Reshaped from apex.otel_traces (SpanName='apex.job_conf') by mv_job_conf (021_).
-- Applied verbatim from contract/ (only formatting). Never rename/repurpose a column.

CREATE TABLE IF NOT EXISTS apex.job_conf
(
    job_id   String,                 -- contract trace key (= applicationId or spark.apex.job_id override)
    app_id   String,                 -- Spark applicationId
    app_name String,
    conf     Map(String, String),    -- allowlisted spark.* key -> RESOLVED value (SQL defaults included)
    ts       DateTime64(3)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (job_id)
TTL toDateTime(ts) + INTERVAL 90 DAY DELETE
SETTINGS ttl_only_drop_parts = 1;
