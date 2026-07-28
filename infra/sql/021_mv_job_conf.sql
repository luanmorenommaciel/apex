-- Apex infra · mv_job_conf — reshape apex.otel_traces -> apex.job_conf (PROPOSED v0.4).
-- Mirrors collect/ddl/32_mv_job_conf.sql exactly — a span landing in otel_traces
-- flows into the same typed row whether it arrived via infra's own collector or
-- collect's. Identity attributes become typed columns; every remaining attribute
-- IS the allowlisted conf map (the jar only ever sets allowlisted spark.* keys,
-- so this passthrough cannot carry a credential). Adding a key to the jar
-- allowlist needs NO DDL change here.

CREATE MATERIALIZED VIEW IF NOT EXISTS apex.mv_job_conf TO apex.job_conf AS
SELECT
  SpanAttributes['job_id']                                      AS job_id,
  SpanAttributes['app_id']                                      AS app_id,
  SpanAttributes['app_name']                                    AS app_name,
  mapFilter((k, v) -> k NOT IN ('job_id', 'app_id', 'app_name', 'ts'), SpanAttributes) AS conf,
  fromUnixTimestamp64Milli(toInt64OrZero(SpanAttributes['ts'])) AS ts
FROM apex.otel_traces
WHERE SpanName = 'apex.job_conf'
  AND SpanAttributes['job_id'] != '';
