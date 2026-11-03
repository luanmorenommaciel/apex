#!/usr/bin/env bash
# Apex infra · exit-criterion healthcheck. Proves the whole store end-to-end and exits 0 iff
# a job_id threads spark_events -> spark_jobs_1m (rollup) -> findings, with the skew query
# flagging it. Run AFTER ./scripts/seed.sh (or after any real ingestion).
#
# Usage:  APEX_CLUSTER_SLOTS=8 ./scripts/verify.sh
#   APEX_CLUSTER_SLOTS is the cluster width (worker cores) the closed-form skew verdict
#   needs (CONTRACT.md rule 1). Unset => the width is unknown, every verdict abstains
#   (NULL) and step 4 fails, because a guessed width would manufacture verdicts.
#   seed.sh's skewed stages are tail-bound at 8.
set -euo pipefail
cd "$(dirname "$0")/.."
ENV_FILE="${INFRA_ENV_FILE:-.env}"
set -a; [ -f "$ENV_FILE" ] && . "$ENV_FILE"; set +a

# Credentials resolve lazily (inside main) so `source verify.sh` for skew_query_a needs none.
resolve_creds() {
  CH_PORT="${CLICKHOUSE_HTTP_HOST_PORT:-8123}"
  CH_USER="${CLICKHOUSE_USER:-apex}"
  CH_PASS="${CLICKHOUSE_PASSWORD:-$(cat "${INFRA_SECRETS_DIR:-secrets}/clickhouse_password" 2>/dev/null || true)}"
  [ -n "$CH_PASS" ] || fail "CLICKHOUSE_PASSWORD is required (set it in infra/.env and run scripts/preflight.sh; there is no default)"
  CH_URL="http://localhost:${CH_PORT}/"
}
CH() { curl -s -u "${CH_USER}:${CH_PASS}" "${CH_URL}" --data-binary "$1"; }

fail() { echo "❌ $1"; exit 1; }

# Skew query (A) exactly as sql/050_skew.sql states it, with the operator width written
# into the marker line. $1 = slots (empty => NULL: unknown width, verdicts abstain).
skew_query_a() {
  local slots="${1:-NULL}"
  sed -n '/^-- (A)/,/^-- (B)/p' sql/050_skew.sql \
    | sed '/^-- (B)/d' \
    | sed "s/^WITH NULL AS operator_slots/WITH ${slots} AS operator_slots/" \
    | sed 's/--.*$//' \
    | sed 's/;[[:space:]]*$//'
}

main() {
  resolve_creds
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

  echo "── 4. skew query (sql/050 A): retry-safe ratio, closed-form verdict ──"
  SLOTS="${APEX_CLUSTER_SLOTS:-}"
  if [ -z "$SLOTS" ]; then
    echo "   APEX_CLUSTER_SLOTS is unset: width unknown, every verdict abstains (NULL)"
  else
    echo "   operator width: ${SLOTS} slots (job_conf width wins when present)"
  fi
  CH "SELECT job_id, stage_id, population, n_tasks, p50_ms, p99_ms, skew_ratio, slots, tail_bound_threshold, tail_bound, min_slots_for_tail_bound
      FROM ($(skew_query_a "$SLOTS"))
      ORDER BY tail_bound DESC NULLS LAST, skew_ratio DESC LIMIT 5 FORMAT PrettyCompact"
  flagged=$(CH "SELECT count() FROM ($(skew_query_a "$SLOTS")) WHERE tail_bound = 1")
  [ "${flagged:-0}" -ge 1 ] || fail "no tail-bound stage (set APEX_CLUSTER_SLOTS to the cluster width; seed.sh data is tail-bound at 8)"

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
}

# Sourced by tests to reach skew_query_a without running the checks.
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then main "$@"; fi
