#!/usr/bin/env bash
# One controlled long-lived-driver experiment.  It writes only ignored local
# logs under dev/out; a reviewed sanitized evidence manifest is produced later.
set -euo pipefail
cd "$(dirname "$0")/.."

COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.c3-otlp.yml)
CYCLES="${APEX_SOAK_CYCLES:-60}"
RECORDS="${APEX_SOAK_RECORDS:-20000}"
PARTITIONS="${APEX_SOAK_PARTITIONS:-8}"
INTERVAL="${APEX_SOAK_SAMPLE_SECONDS:-5}"
DELIVERY_WAIT_SECONDS="${APEX_SOAK_DELIVERY_WAIT_SECONDS:-180}"
PLUGIN="${APEX_SOAK_PLUGIN:-on}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="out/driver-listener-soak-${STAMP}.log"
SAMPLES="out/driver-listener-soak-${STAMP}-containers.csv"

[[ "$CYCLES" =~ ^[1-9][0-9]*$ ]] || { echo "APEX_SOAK_CYCLES must be positive" >&2; exit 2; }
[[ "$RECORDS" =~ ^[1-9][0-9]*$ ]] || { echo "APEX_SOAK_RECORDS must be positive" >&2; exit 2; }
[[ "$PARTITIONS" =~ ^[1-9][0-9]*$ ]] || { echo "APEX_SOAK_PARTITIONS must be positive" >&2; exit 2; }
[[ "$INTERVAL" =~ ^[1-9][0-9]*$ ]] || { echo "APEX_SOAK_SAMPLE_SECONDS must be positive" >&2; exit 2; }
[[ "$DELIVERY_WAIT_SECONDS" =~ ^[1-9][0-9]*$ ]] || { echo "APEX_SOAK_DELIVERY_WAIT_SECONDS must be positive" >&2; exit 2; }
[[ "$PLUGIN" == on || "$PLUGIN" == off ]] || { echo "APEX_SOAK_PLUGIN must be on or off" >&2; exit 2; }
[[ -f .env ]] || { echo "dev/.env missing; run: make env-spark41" >&2; exit 2; }
mkdir -p out
printf 'timestamp_utc,container,cpu_percent,mem_usage,mem_percent\n' >"$SAMPLES"
sample() {
  local now
  now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  docker stats --no-stream --format '{{.Name}},{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}}' \
    apex-dev-spark-master-1 apex-dev-spark-worker-1 apex-otel-collector 2>/dev/null \
    | sed "s/^/${now},/" >>"$SAMPLES" || true
}
sampler() { while kill -0 "$1" 2>/dev/null; do sample; sleep "$INTERVAL"; done; sample; }

[[ "$(docker inspect -f '{{.State.Running}}' apex-otel-collector 2>/dev/null || true)" == true ]] || {
  echo "apex-otel-collector must be running" >&2; exit 2;
}
"${COMPOSE[@]}" up -d --wait --no-recreate >/dev/null

set +e
SUBMIT_CONF=(--conf spark.driver.host=spark-master --conf spark.driver.bindAddress=0.0.0.0)
if [[ "$PLUGIN" == on ]]; then
  SUBMIT_CONF=(
    --conf spark.plugins=apex.ApexPlugin
    --conf "spark.apex.otlp.endpoint=http://apex-otel-collector:4318"
    "${SUBMIT_CONF[@]}"
  )
else
  # The mounted dev/conf/spark-defaults.conf declares spark.plugins; the OFF
  # arm must explicitly override it with an empty value at submit time.
  SUBMIT_CONF=(--conf spark.plugins= "${SUBMIT_CONF[@]}")
fi
"${COMPOSE[@]}" exec -T \
  -e APEX_SOAK_CYCLES="$CYCLES" -e APEX_SOAK_RECORDS="$RECORDS" -e APEX_SOAK_PARTITIONS="$PARTITIONS" \
  spark-master /bin/sh /opt/apex/scripts/with-s3-credentials.sh \
  /opt/spark/bin/spark-submit --master spark://spark-master:7077 \
  "${SUBMIT_CONF[@]}" \
  /opt/apex/jobs/listener_soak.py >"$LOG" 2>&1 &
submit_pid=$!
sampler "$submit_pid" & sampler_pid=$!
wait "$submit_pid"; rc=$?
wait "$sampler_pid" || true
set -e

job_id="$(grep -oE 'APEX_SESSION job_id=[^ ]+' "$LOG" | tail -1 | cut -d= -f2 || true)"
completed="$(grep -c '^APEX_SOAK cycle=' "$LOG" || true)"
if [[ -z "$job_id" ]]; then
  echo "SOAK_RESULT status=failed plugin=$PLUGIN reason=missing_job_id completed_cycles=$completed log=$LOG" >&2
  exit 1
fi

if [[ "$PLUGIN" == off ]]; then
  # No plugin means no telemetry by design; delivery assertions do not apply.
  if (( rc != 0 || completed != CYCLES )); then
    echo "SOAK_RESULT status=failed plugin=off job_id=$job_id completed_cycles=$completed expected_cycles=$CYCLES samples=$SAMPLES log=$LOG" >&2
    exit 1
  fi
  echo "SOAK_RESULT status=passed plugin=off job_id=$job_id completed_cycles=$completed samples=$SAMPLES log=$LOG"
  exit 0
fi

# The credentials remain inside the container environment and are never printed.
events=0
unique_events=0
query_failures=0
delivery_waited_seconds=0
delivery_poll_seconds=5
delivery_attempts=$(( (DELIVERY_WAIT_SECONDS + delivery_poll_seconds - 1) / delivery_poll_seconds ))
for _ in $(seq 1 "$delivery_attempts"); do
  if counts="$(docker exec -e APEX_SOAK_JOB_ID="$job_id" apex-infra-clickhouse sh -lc \
    'clickhouse-client --user "$CLICKHOUSE_USER" --password "$CLICKHOUSE_PASSWORD" --param_job_id "$APEX_SOAK_JOB_ID" -q "SELECT count(), countDistinct((stage_id, stage_attempt)) FROM apex.spark_events WHERE job_id = {job_id:String}"' 2>/dev/null)"; then
    :
  else
    counts="0 0"
    query_failures=$((query_failures + 1))
  fi
  read -r events unique_events <<<"$counts"
  [[ "$events" =~ ^[0-9]+$ && "$unique_events" =~ ^[0-9]+$ ]] && (( unique_events > 0 )) && break
  sleep "$delivery_poll_seconds"
  delivery_waited_seconds=$((delivery_waited_seconds + delivery_poll_seconds))
done

if (( rc != 0 || completed != CYCLES || unique_events == 0 )); then
  echo "SOAK_RESULT status=failed plugin=on job_id=$job_id completed_cycles=$completed expected_cycles=$CYCLES event_rows=$events unique_stage_attempts=$unique_events delivery_waited_seconds=$delivery_waited_seconds query_failures=$query_failures samples=$SAMPLES log=$LOG" >&2
  exit 1
fi
duplicate_rows=$((events - unique_events))
echo "SOAK_RESULT status=passed plugin=on job_id=$job_id completed_cycles=$completed event_rows=$events unique_stage_attempts=$unique_events duplicate_rows=$duplicate_rows delivery_waited_seconds=$delivery_waited_seconds query_failures=$query_failures samples=$SAMPLES log=$LOG"
