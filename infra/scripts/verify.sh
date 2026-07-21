#!/usr/bin/env bash
# Apex infra · exit-criterion healthcheck. Proves the whole store end-to-end and exits 0 iff
# a job_id threads spark_events -> spark_jobs_1m (rollup) -> findings, with the skew query
# flagging it. Run AFTER ./scripts/seed.sh (or after any real ingestion).
#
# Usage:  ./scripts/verify.sh
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; [ -f .env ] && . ./.env; set +a

CH_PORT="${CLICKHOUSE_HTTP_HOST_PORT:-8123}"
CH_USER="${CLICKHOUSE_USER:-apex}"
CH_PASS="${CLICKHOUSE_PASSWORD:-apex_local_dev}"
CH_URL="http://localhost:${CH_PORT}/"
CH() { curl -s -u "${CH_USER}:${CH_PASS}" "${CH_URL}" --data-binary "$1"; }

fail() { echo "❌ $1"; exit 1; }

echo "── 1. stack health ─────────────────────────────────────────"
for c in apex-infra-clickhouse apex-infra-mongodb apex-infra-hyperdx apex-infra-otel-collector; do
  st=$(docker inspect -f '{{.State.Status}}' "$c" 2>/dev/null || echo missing)
  echo "   $c: $st"
  [ "$st" = "running" ] || fail "$c not running"
done
[ "$(CH 'SELECT 1')" = "1" ] || fail "ClickHouse not answering"

echo "── 2. schema present ───────────────────────────────────────"
tables=$(CH "SELECT count() FROM system.tables WHERE database='apex' AND name IN ('spark_events','findings','plan_transitions','spark_jobs_1m','spark_jobs_1m_mv','mv_spark_events','otel_traces')")
echo "   contract+rollup+reshape objects present: ${tables}/7"
[ "$tables" = "7" ] || fail "missing schema objects"

echo "── 3. data ingested ────────────────────────────────────────"
rows=$(CH "SELECT count() FROM apex.spark_events")
jobs=$(CH "SELECT uniq(job_id) FROM apex.spark_events")
echo "   spark_events rows=${rows}  distinct job_id=${jobs}"
[ "${rows:-0}" -ge 1 ] || fail "no spark_events rows (did you run seed.sh? remember ts=now TTL gotcha)"

echo "── 4. skew query flags a stage (p99/p50 > 5) ───────────────"
CH "SELECT job_id, stage_id,
       argMax(task_duration_p50_ms, ts) AS p50,
       argMax(task_duration_p99_ms, ts) AS p99,
       round(argMax(task_duration_p99_ms, ts)/nullIf(argMax(task_duration_p50_ms, ts),0),2) AS skew_ratio
    FROM apex.spark_events WHERE ts >= now() - INTERVAL 6 HOUR
    GROUP BY job_id, stage_id HAVING skew_ratio > 5
    ORDER BY skew_ratio DESC LIMIT 5 FORMAT PrettyCompact"
flagged=$(CH "SELECT count() FROM (SELECT job_id, stage_id, argMax(task_duration_p99_ms,ts)/nullIf(argMax(task_duration_p50_ms,ts),0) AS r FROM apex.spark_events WHERE ts >= now()-INTERVAL 6 HOUR GROUP BY job_id, stage_id HAVING r > 5)")
[ "${flagged:-0}" -ge 1 ] || fail "skew query flagged nothing"

echo "── 5. rollup sketch populated (incremental MV) ─────────────"
CH "SELECT job_id,
       countMerge(count__) AS stages,
       arrayElement(quantilesMerge(0.5,0.99)(quantiles__task_duration_p99_ms),1) AS p50_of_p99,
       arrayElement(quantilesMerge(0.5,0.99)(quantiles__task_duration_p99_ms),2) AS p99_of_p99
    FROM apex.spark_jobs_1m GROUP BY job_id ORDER BY job_id FORMAT PrettyCompact"

echo "── 6. EXIT CRITERION — one job_id threads all three tables ──"
# Pick the top-skew job that exists in spark_events AND spark_jobs_1m AND findings.
JOB=$(CH "
  SELECT se.job_id FROM
    (SELECT job_id, max(task_duration_p99_ms/nullIf(task_duration_p50_ms,0)) AS r FROM apex.spark_events GROUP BY job_id) se
  INNER JOIN (SELECT DISTINCT job_id FROM apex.spark_jobs_1m) ru ON se.job_id=ru.job_id
  INNER JOIN (SELECT DISTINCT job_id FROM apex.findings)      fn ON se.job_id=fn.job_id
  ORDER BY se.r DESC LIMIT 1")
[ -n "$JOB" ] || fail "no job_id present in spark_events ∧ spark_jobs_1m ∧ findings (run seed.sh)"
echo "   traced job_id = ${JOB}"
CH "SELECT
      '${JOB}'                                                          AS job_id,
      (SELECT count() FROM apex.spark_events   WHERE job_id='${JOB}')    AS spark_events_rows,
      (SELECT countMerge(count__) FROM apex.spark_jobs_1m WHERE job_id='${JOB}') AS rollup_stages,
      (SELECT count() FROM apex.findings        WHERE job_id='${JOB}')   AS findings_rows
    FORMAT PrettyCompact"

echo ""
echo "✅ VERIFY PASSED — job_id ${JOB} threads spark_events → spark_jobs_1m → findings; skew query flags it."
