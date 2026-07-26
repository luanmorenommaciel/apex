#!/usr/bin/env bash
# Canonical four-pathology E2E: Spark plugin -> OTLP -> collect -> infra ClickHouse.
# It deliberately keeps collect/infra running and never reads the JSONL compatibility sink.
set -uo pipefail
cd "$(dirname "$0")/.."

# Git Bash otherwise rewrites container paths such as /opt/spark/bin/spark-submit
# into host paths before docker.exe receives them. It is harmless on Linux/macOS.
export MSYS_NO_PATHCONV=1

COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.c3-otlp.yml)
MASTER="spark://spark-master:7077"
DRIVER_HOST="${APEX_CANONICAL_DRIVER_HOST:-spark-master}"
REQUESTED_SCENARIOS=("$@")
if [ "${#REQUESTED_SCENARIOS[@]}" -eq 0 ]; then
  REQUESTED_SCENARIOS=(skew_join spill bad_shuffle driver_oom)
fi
FAIL=0
ok() { printf '  \033[32mPASS\033[0m %s\n' "$1"; }
bad() { printf '  \033[31mFAIL\033[0m %s\n' "$1"; FAIL=1; }
step() { printf '\n\033[1m== %s ==\033[0m\n' "$1"; }

[ -f .env ] || { echo "no .env - run: make env"; exit 2; }
[ -n "${APEX_CANONICAL_CH_PASSWORD:-}" ] || { echo "APEX_CANONICAL_CH_PASSWORD is required"; exit 2; }
command -v python3 >/dev/null || { echo "python3 is required"; exit 2; }
for requested in "${REQUESTED_SCENARIOS[@]}"; do
  case "$requested" in skew_join|tail_outlier|spill|bad_shuffle|driver_oom) ;; *) echo "unknown scenario: $requested"; exit 2;; esac
done

# The collector is owned by collect; the persistent store is owned by infra.
docker network inspect apex-collect-net >/dev/null 2>&1 || {
  echo "apex-collect-net is missing - start collect connected to infra first"; exit 2;
}
[ "$(docker inspect -f '{{.State.Running}}' apex-otel-collector 2>/dev/null || true)" = "true" ] || {
  echo "apex-otel-collector is not running - start collect/infra first"; exit 2;
}

export APEX_OTLP_ENDPOINT="http://apex-otel-collector:4318"

submit_job() {
  local scenario="$1" job="$2" log="out/e2e-canonical-${scenario}.log" aqe="$3" fix="$4" safe="$5" driver_mem="$6"
  local -a submit_args=(
    /opt/spark/bin/spark-submit --master "$MASTER"
    --conf spark.plugins=apex.ApexPlugin
    --conf spark.apex.otlp.endpoint="$APEX_OTLP_ENDPOINT"
    --conf spark.driver.host="$DRIVER_HOST"
    --conf spark.driver.bindAddress=0.0.0.0
  )
  if [ -n "$driver_mem" ]; then
    submit_args+=(--driver-memory "$driver_mem")
  fi
  submit_args+=("/opt/apex/jobs/$job")
  "${COMPOSE[@]}" exec -T \
    -e APEX_AQE="$aqe" -e APEX_FIX="$fix" -e APEX_SAFE="$safe" spark-master \
    "${submit_args[@]}" >"$log" 2>&1
}

extract_job_id() {
  grep -oE 'APEX_SESSION job_id=[^ ]+' "$1" | tail -1 | cut -d= -f2
}

assert_canonical() {
  local scenario="$1" job_id="$2"
  python3 scripts/canonical_e2e_assert.py --job-id "$job_id" --scenario "$scenario"
}

should_run() {
  local wanted="$1"
  local scenario
  for scenario in "${REQUESTED_SCENARIOS[@]}"; do
    [ "$scenario" = "$wanted" ] && return 0
  done
  return 1
}

run_success() {
  local scenario="$1" job="$2" aqe="$3" fix="$4"
  local log="out/e2e-canonical-${scenario}.log"
  if submit_job "$scenario" "$job" "$aqe" "$fix" off ""; then
    ok "$scenario Spark job completed"
  else
    bad "$scenario Spark job failed (see $log)"; return
  fi
  local job_id
  job_id="$(extract_job_id "$log")"
  if [ -z "$job_id" ]; then bad "$scenario did not print APEX_SESSION job_id"; return; fi
  if assert_canonical "$scenario" "$job_id"; then
    ok "$scenario canonical ClickHouse assertion (job_id=$job_id)"
  else
    bad "$scenario canonical ClickHouse assertion failed (job_id=$job_id)"
  fi
}

run_oom() {
  local scenario="driver_oom" log="out/e2e-canonical-driver_oom.log"
  if submit_job "$scenario" driver_oom.py off off off 512m; then
    bad "driver_oom unexpectedly completed"
  else
    ok "driver_oom failed as expected"
  fi
  local job_id
  job_id="$(extract_job_id "$log")"
  if [ -z "$job_id" ]; then bad "driver_oom did not print APEX_SESSION job_id"; return; fi
  if assert_canonical "$scenario" "$job_id"; then
    ok "driver_oom pre-failure telemetry reached ClickHouse (job_id=$job_id)"
  else
    bad "driver_oom canonical telemetry missing (job_id=$job_id)"
  fi
}

step "1/6 verify shared canonical platform"
ok "collector and overlay network are available"

step "2/6 start only the dev stack on the C3 overlay"
if [ "${E2E_CANONICAL_REUSE_DEV:-0}" = "1" ]; then
  ok "reusing already healthy dev cluster"
elif "${COMPOSE[@]}" up -d --build --wait --wait-timeout 300; then
  ok "dev cluster healthy"
else
  bad "dev cluster did not become healthy"
fi

step "3/6 generate deterministic skewed data"
if [ "${E2E_CANONICAL_SKIP_GENERATE:-0}" = "1" ]; then
  ok "reusing existing deterministic data"
else
  "${COMPOSE[@]}" exec -T spark-master /opt/spark/bin/spark-submit --master "$MASTER" \
    --conf spark.plugins=apex.ApexPlugin --conf spark.apex.otlp.endpoint="$APEX_OTLP_ENDPOINT" \
    --conf spark.driver.host="$DRIVER_HOST" --conf spark.driver.bindAddress=0.0.0.0 \
    /opt/apex/jobs/generate_data.py >out/e2e-canonical-generate-data.log 2>&1
  if grep -q 'hot_key_~50pct=PASS' out/e2e-canonical-generate-data.log; then
    ok "deterministic hot key generated"
  else
    bad "data generation did not prove hot key distribution"
  fi
fi

step "4/6 skew_join and spill against canonical telemetry"
should_run skew_join && run_success skew_join skew_join.py off off
should_run tail_outlier && run_success tail_outlier tail_outlier.py off off
should_run spill && run_success spill spill.py off off

step "5/6 bad_shuffle against canonical telemetry"
should_run bad_shuffle && run_success bad_shuffle bad_shuffle.py off off

step "6/6 driver_oom plus pre-failure canonical telemetry"
should_run driver_oom && run_oom

echo
if [ "$FAIL" = 0 ]; then
  printf '\033[1;32mOK E2E CANONICAL PASSED - requested pathologies reached ClickHouse\033[0m\n'
else
  printf '\033[1;31mX E2E CANONICAL FAILED - see scenario logs under dev/out\033[0m\n'
fi
echo "dev remains running for inspection; use 'make down' when appropriate."
exit "$FAIL"
