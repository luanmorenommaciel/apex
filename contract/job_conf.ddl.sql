-- Apex contract — PROPOSED v0.4 (awaiting central ratification; see
-- contract/CONTRACT-EXTENSION-v0.4-job_conf.md). ADDITIVE: one new table,
-- no existing column renamed, retyped or repurposed.
--
-- apex.job_conf — one row per application run: the RESOLVED, ALLOWLISTED
-- SparkConf subset. Lets memory/ recall "the config that worked" and verify/
-- run its NO-OP gate ("was skewJoin.enabled already true on this run?") from
-- ClickHouse alone, with no History Server.
--
-- Emitted by jar as a distinct `apex.job_conf` OTLP span (spark.apex.conf.enabled,
-- default on), once per application; reshaped from apex.otel_traces by mv_job_conf.
--
-- SECURITY: `conf` only ever carries the jar's hard-coded allowlist (ZEST's 6
-- tunables, the AQE flags, autoBroadcastJoinThreshold) — pure performance knobs,
-- values are numbers/byte-sizes/booleans. The whole conf is NEVER shipped: it can
-- carry s3a secret keys, JDBC passwords, and tokens.

CREATE DATABASE IF NOT EXISTS apex;

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
