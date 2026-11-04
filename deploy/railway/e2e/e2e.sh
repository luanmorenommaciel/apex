#!/usr/bin/env bash
# Railway e2e runner: submit one canonical pathology job to the Railway Spark cluster, then run
# scripts/e2e_six_lanes.py against the Railway ClickHouse/API. Every hostname comes from env.
# Exit 0 = gate passed. Prints no credentials.
set -euo pipefail
# Outer wrapper: hard 20-min cap (E2E_TIMEOUT_SECONDS), always prints the marker scale-up.sh polls for.
if [ -z "${E2E_INNER:-}" ]; then
  rc=0; E2E_INNER=1 timeout -k 30 "${E2E_TIMEOUT_SECONDS:-1200}" "$0" "$@" || rc=$?
  [ "$rc" = 124 ] && echo "e2e timed out after ${E2E_TIMEOUT_SECONDS:-1200}s"
  echo "E2E_EXIT=$rc"; exit "$rc"
fi
: "${SPARK_MASTER_URL:?}" "${CLICKHOUSE_HOST:?}" "${CLICKHOUSE_PASSWORD:?}" "${APEX_API_URL:?}"
E2E_JOB=${E2E_JOB:-skew_join}
JOB_ID=${E2E_JOB_ID:-railway-e2e-${E2E_JOB}-$(date -u +%Y%m%dT%H%M%S)}   # fresh id => no pre-existing findings
SETTLE=${E2E_SETTLE_SECONDS:-30}
SRC=/opt/apex/src

echo "== render spark-defaults.conf"; /opt/apex/railway/start.sh conf
echo "== api health: $APEX_API_URL"
curl -fsS ${APEX_API_TOKEN:+-H "Authorization: Bearer $APEX_API_TOKEN"} "$APEX_API_URL/v1/health" >/dev/null

# The Spark driver runs here: bind on all v6 addrs and advertise our private DNS name.
# "::" comes back as an unresolved "[::]" in the driver (UnresolvedAddressException); Java maps 0.0.0.0
# to a dual-stack socket on Linux, so it still accepts executors over Railway's IPv6 network.
export SPARK_LOCAL_IP=0.0.0.0 SPARK_LOCAL_HOSTNAME="${RAILWAY_PRIVATE_DOMAIN:-$(hostname)}"
echo "== submit $E2E_JOB job_id=$JOB_ID -> $SPARK_MASTER_URL"
/opt/spark/bin/spark-submit --master "$SPARK_MASTER_URL" --deploy-mode client \
  --conf spark.driver.bindAddress=0.0.0.0 --conf spark.apex.job_id="$JOB_ID" "/opt/apex/jobs/${E2E_JOB}.py"

echo "== wait ${SETTLE}s for OTLP -> ClickHouse"; sleep "$SETTLE"
echo "== six-lane gate"
cd "$SRC/engine"
uv run --frozen --no-sync --extra dev --extra clickhouse python ../scripts/e2e_six_lanes.py --job-id "$JOB_ID"
