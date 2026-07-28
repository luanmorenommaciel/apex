-- Apex collect · mv_job_conf — reshape apex.otel_traces -> apex.job_conf.
--
-- The proposed v0.4 conf-capture signal. jar emits a distinct span named
-- 'apex.job_conf' once per application; it lands in otel_traces alongside the
-- other span types and this MV routes+flattens it into the job_conf table.
-- Identity attributes (job_id/app_id/app_name/ts) become typed columns; every
-- remaining attribute IS the allowlisted conf map — the jar only ever sets
-- allowlisted spark.* keys (see ApexJobConfAllowlist), so the passthrough below
-- cannot carry a credential. Adding a key to the jar allowlist needs NO DDL
-- change here (the Map column absorbs it).

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
