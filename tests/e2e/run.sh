#!/usr/bin/env bash
# Apex P0 end-to-end: one real broken Spark job flows dev → jar → collect(∥) → infra
# and lands as queryable rows (spark_events + plan_transitions) flagged by the skew
# watchers and visible through HyperDX's query engine.
#
# Integration-only glue — it does NOT modify any lane. What it does:
#   1. Brings up infra's canonical ClickStack (ClickHouse + HyperDX + Mongo + collector).
#   2. Network glue: publishes infra's collector under the contracted DNS name
#      `apex-otel-collector` on the external `apex-collect-net`, so dev's C3/C4
#      overlay targets it verbatim. (If collect's real collector is already running,
#      the glue is skipped and collect's collector is used instead — same contract.)
#   3. Builds/starts the dev lane (plugin jar is baked from ../jar by dev's Dockerfile).
#   4. Runs the instrumented skew pathology: spark.plugins=apex.ApexPlugin,
#      spark.apex.otlp.endpoint=http://apex-otel-collector:4318, AQE on (CONTRACT §Activation).
#   5. Asserts in infra's ClickHouse, threaded by ONE job_id:
#        spark_events rows landed · plan_transitions has the AQE decision ·
#        sql/005 skew query flags the run · plan_json carries no literals/PII.
#   6. Best-effort: proves HyperDX's chart engine returns the job (needs the first
#      user registered; skipped otherwise).
#
# Usage:  tests/e2e/run.sh            # leaves stacks up so you can open HyperDX :8090
#         TEARDOWN=1 tests/e2e/run.sh # tear both stacks down at the end (keeps volumes)
#         SKIP_BUILD=1 tests/e2e/run.sh  # reuse the existing apex-spark:local image
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
INFRA="$ROOT/infra"
DEV="$ROOT/dev"
DEV_COMPOSE=(docker compose -f "$DEV/docker-compose.yml" -f "$DEV/docker-compose.c3-otlp.yml" --project-directory "$DEV")

FAIL=0
ok()   { printf '  \033[32mPASS\033[0m %s\n' "$1"; }
bad()  { printf '  \033[31mFAIL\033[0m %s\n' "$1"; FAIL=1; }
step() { printf '\n\033[1m== %s ==\033[0m\n' "$1"; }
die()  { printf '\033[31mABORT:\033[0m %s\n' "$1"; exit 2; }

command -v docker  >/dev/null || die "docker is required"
command -v curl    >/dev/null || die "curl is required"
command -v python3 >/dev/null || die "python3 is required"
[ -f "$INFRA/.env" ] || die "infra/.env missing — copy infra/.env.example and set HYPERDX_API_KEY"

# ClickHouse creds come from infra's env (defaults mirror the compose defaults).
CH_USER=$(grep -E '^CLICKHOUSE_USER='     "$INFRA/.env" | tail -1 | cut -d= -f2); CH_USER=${CH_USER:-apex}
CH_PASS=$(grep -E '^CLICKHOUSE_PASSWORD=' "$INFRA/.env" | tail -1 | cut -d= -f2); CH_PASS=${CH_PASS:-apex_local_dev}
ch() { docker exec apex-infra-clickhouse clickhouse-client --user "$CH_USER" --password "$CH_PASS" -q "$1"; }

step "1/6 infra up (canonical ClickStack)"
(cd "$INFRA" && docker compose up -d --wait) || die "infra stack failed to come up healthy"
for t in spark_events plan_transitions findings otel_traces; do
  ch "EXISTS TABLE apex.$t" | grep -q 1 && ok "apex.$t exists" || bad "apex.$t missing"
done
curl -sf -m 5 http://localhost:13133/ >/dev/null && ok "collector health :13133" || bad "collector health"
curl -sf -m 5 -o /dev/null http://localhost:8090/ && ok "HyperDX UI :8090" || bad "HyperDX UI :8090"

step "2/6 network glue: apex-otel-collector alias on apex-collect-net"
docker network create apex-collect-net >/dev/null 2>&1 || true
if [ "$(docker inspect -f '{{.State.Running}}' apex-otel-collector 2>/dev/null)" = "true" ]; then
  ok "collect's own collector is running — using it (no alias needed)"
else
  if docker network inspect apex-collect-net -f '{{range .Containers}}{{.Name}} {{end}}' | grep -q apex-infra-otel-collector; then
    ok "infra collector already aliased on apex-collect-net"
  else
    docker network connect --alias apex-otel-collector apex-collect-net apex-infra-otel-collector \
      && ok "infra collector joined apex-collect-net as apex-otel-collector" \
      || die "could not alias infra collector onto apex-collect-net"
  fi
fi

step "3/6 dev lane up (plugin baked from ../jar)"
[ -f "$DEV/.env" ] || (cd "$DEV" && python3 scripts/ensure_env.py .env.example .env) || die "could not create dev/.env"
if [ "${SKIP_BUILD:-0}" != "1" ]; then
  (cd "$DEV" && docker compose build) || die "dev image build failed"
fi
"${DEV_COMPOSE[@]}" up -d --wait || die "dev cluster failed to come up healthy"
"${DEV_COMPOSE[@]}" exec -T spark-master sh -c \
  'curl -s -m 5 -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d "{}" http://apex-otel-collector:4318/v1/traces' \
  | grep -q 200 && ok "dev → apex-otel-collector:4318 reachable" || bad "dev cannot reach the collector"

step "4/6 run instrumented pathology: skew_join, ApexPlugin, AQE on (CONTRACT §Activation)"
LOG=$(mktemp)
"${DEV_COMPOSE[@]}" exec -T -e APEX_AQE=on -e APEX_FIX=off -e APEX_SAFE=off spark-master \
  /opt/spark/bin/spark-submit --master spark://spark-master:7077 \
  --conf spark.plugins=apex.ApexPlugin \
  --conf spark.apex.otlp.endpoint=http://apex-otel-collector:4318 \
  --conf spark.apex.aqe.enabled=true \
  /opt/apex/jobs/skew_join.py >"$LOG" 2>&1
RC=$?
JOB_ID=$(grep -oE 'APEX_SESSION job_id=[^ ]+' "$LOG" | tail -1 | cut -d= -f2)
[ $RC -eq 0 ] && ok "skew_join completed (exit 0)" || { bad "skew_join exited $RC — tail of log:"; tail -20 "$LOG"; }
[ -n "$JOB_ID" ] && ok "job_id=$JOB_ID" || die "no APEX_SESSION job_id in job output"

step "5/6 assert the signal landed in infra ClickHouse (job_id=$JOB_ID)"
EVENTS=0
for _ in $(seq 1 12); do   # collector batches ~1s + async insert; poll up to ~60s
  EVENTS=$(ch "SELECT count() FROM apex.spark_events WHERE job_id='$JOB_ID'")
  [ "${EVENTS:-0}" -gt 0 ] && break
  sleep 5
done
[ "${EVENTS:-0}" -gt 0 ] && ok "spark_events: $EVENTS stage rows" || bad "no spark_events rows for $JOB_ID"

TRANS=$(ch "SELECT count() FROM apex.plan_transitions WHERE job_id='$JOB_ID'")
[ "${TRANS:-0}" -gt 0 ] \
  && ok "plan_transitions: $TRANS AQE decision(s): $(ch "SELECT groupArray(concat(transition_type,'/',confidence)) FROM apex.plan_transitions WHERE job_id='$JOB_ID'")" \
  || bad "no plan_transitions for $JOB_ID (AQE fired nothing — see dev's c4-aqe-skewsplit calibration)"

SKEW=$(ch "SELECT count() FROM (SELECT stage_id FROM apex.spark_events WHERE job_id='$JOB_ID' GROUP BY stage_id HAVING argMax(task_duration_p99_ms,ts)/nullIf(argMax(task_duration_p50_ms,ts),0) > 5)")
[ "${SKEW:-0}" -gt 0 ] && ok "skew watcher (sql/005 A): $SKEW stage(s) flagged > 5x" || bad "skew query flags nothing for $JOB_ID"

FP=$(ch "SELECT countDistinct(plan_fingerprint) FROM apex.spark_events WHERE job_id='$JOB_ID' AND plan_fingerprint != ''")
[ "${FP:-0}" -gt 0 ] && ok "plan_fingerprint present ($FP distinct plans)" || bad "no plan_fingerprint captured"

PII=$(ch "SELECT countIf(match(plan_json, '= [0-9]{2,}|@|/opt/|hot_key')) FROM apex.spark_events WHERE job_id='$JOB_ID'")
[ "${PII:-1}" -eq 0 ] && ok "redaction: plan_json carries no literals/paths/emails" || bad "plan_json redaction leak in $PII row(s)"

step "6/6 HyperDX query engine sees the job (best-effort — needs registered first user)"
if [ "$(curl -sf -m 5 http://localhost:8000/installation)" = '{"isTeamExisting":true}' ] \
   && docker exec apex-infra-mongodb mongosh --quiet --eval 'quit(0)' >/dev/null 2>&1; then
  UKEY=$(docker exec apex-infra-mongodb mongosh --quiet hyperdx --eval 'print(db.users.findOne({}).accessKey)' 2>/dev/null)
  SRC=$(docker exec apex-infra-mongodb mongosh --quiet hyperdx --eval 'print(db.sources.findOne({name:"Spark Events"})._id.toString())' 2>/dev/null)
  if [ -n "$UKEY" ] && [ -n "$SRC" ]; then
    NOW=$(python3 -c 'import time; print(int(time.time()*1000))')
    HDX=$(curl -s -m 20 -X POST -H "Authorization: Bearer $UKEY" -H "Content-Type: application/json" \
      http://localhost:8000/api/v2/charts/series \
      -d '{"startTime":'$((NOW-6*3600*1000))',"endTime":'$NOW',"series":[{"type":"table","sourceId":"'$SRC'","aggFn":"max","field":"task_duration_p99_ms","where":"","groupBy":["job_id"]}]}')
    echo "$HDX" | grep -q "$JOB_ID" && ok "HyperDX charts/series returns $JOB_ID" || bad "HyperDX charts/series missing $JOB_ID: $(echo "$HDX" | head -c 200)"
  else
    echo "  SKIP — could not read accessKey/source from Mongo"
  fi
else
  echo "  SKIP — no team registered yet: open http://localhost:8090, register, re-run"
fi

if [ "${TEARDOWN:-0}" = "1" ]; then
  step "teardown"
  "${DEV_COMPOSE[@]}" down
  (cd "$INFRA" && docker compose down)
fi

printf '\n'
if [ $FAIL -eq 0 ]; then
  printf '\033[32m✔ P0 E2E GREEN\033[0m — job_id %s threaded dev → jar → collector → ClickHouse → HyperDX\n' "$JOB_ID"
  printf '  Inspect: http://localhost:8090 (HyperDX) · clickhouse-client on :9000 · job logs in dev/out/\n'
else
  printf '\033[31m✘ P0 E2E FAILED\033[0m — see FAIL lines above (job_id %s)\n' "${JOB_ID:-unknown}"
fi
exit $FAIL
