#!/usr/bin/env bash
# Railway e2e runner: submit one canonical pathology job to the Railway Spark cluster, then run
# scripts/e2e_six_lanes.py against the Railway ClickHouse/API. Every hostname comes from env.
# Exit 0 = gate passed. Prints no credentials.
set -euo pipefail
: "${SPARK_MASTER_URL:?}" "${CLICKHOUSE_HOST:?}" "${CLICKHOUSE_PASSWORD:?}" "${APEX_API_URL:?}"
E2E_JOB=${E2E_JOB:-skew_join}
JOB_ID=${E2E_JOB_ID:-railway-e2e-${E2E_JOB}-$(date -u +%Y%m%dT%H%M%S)}   # fresh id => no pre-existing findings
SETTLE=${E2E_SETTLE_SECONDS:-30}
SRC=/opt/apex/src

echo "== render spark-defaults.conf"; /opt/apex/railway/start.sh conf
echo "== api health: $APEX_API_URL"
curl -fsS ${APEX_API_TOKEN:+-H "Authorization: Bearer $APEX_API_TOKEN"} "$APEX_API_URL/v1/health" >/dev/null

echo "== submit $E2E_JOB job_id=$JOB_ID -> $SPARK_MASTER_URL"
/opt/spark/bin/spark-submit --master "$SPARK_MASTER_URL" --deploy-mode client \
  --conf spark.apex.job_id="$JOB_ID" "/opt/apex/jobs/${E2E_JOB}.py"

echo "== wait ${SETTLE}s for OTLP -> ClickHouse"; sleep "$SETTLE"
echo "== six-lane gate"
cd "$SRC/engine"
exec uv run --frozen --no-sync --extra dev --extra clickhouse python ../scripts/e2e_six_lanes.py --job-id "$JOB_ID"
