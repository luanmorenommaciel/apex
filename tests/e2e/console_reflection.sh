#!/usr/bin/env bash
# Apex console E2E: ENGINE → MEMORY → SERVE (apex-api) → CONSOLE, for one job that
# has already landed in infra's canonical ClickHouse.
#
# tests/e2e/run.sh proves the plumbing up to the store (dev → jar → collect →
# infra). scripts/e2e_six_lanes.py proves engine and the MCP agree on one job.
# Neither reaches the console. This does: it takes a job_id, runs the two lanes
# that write what the console reads, starts the API over the same store, proves
# the console's rows are the same through both doors (the live parity gate),
# and then mounts the REAL App against that API and reads every screen for the
# job, the way a person would.
#
#   tests/e2e/console_reflection.sh <job_id>              # all steps
#   tests/e2e/console_reflection.sh --latest               # the newest job in the store
#   KEEP_API=1 tests/e2e/console_reflection.sh <job_id>   # leave apex-api running on :8099
#   SKIP_ENGINE=1 / SKIP_MEMORY=1                          # the job is already analysed / indexed
#
# Integration-only glue: it modifies no lane. The engine and memory lanes are
# invoked through their own CLIs, deterministic (--no-crew: never an LLM), on
# the job named — exactly as an operator would run them.
set -uo pipefail
# lsof lives in /usr/sbin on macOS, which a reduced PATH (an eval runner, cron)
# may not carry — and cleanup kills the API by its listening port.
export PATH="$PATH:/usr/sbin:/sbin"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
INFRA="$ROOT/infra"
JOB_ID="${1:-}"
[ -n "$JOB_ID" ] || { echo "usage: $0 <job_id> | --latest"; exit 2; }

FAIL=0
ok()   { printf '  \033[32mPASS\033[0m %s\n' "$1"; }
bad()  { printf '  \033[31mFAIL\033[0m %s\n' "$1"; FAIL=1; }
note() { printf '  \033[2m%s\033[0m\n' "$1"; }
step() { printf '\n\033[1m== %s ==\033[0m\n' "$1"; }
die()  { printf '\033[31mABORT:\033[0m %s\n' "$1"; exit 2; }

command -v docker >/dev/null || die "docker is required"
command -v uv     >/dev/null || die "uv is required"
command -v npx    >/dev/null || die "node/npx is required"
[ -f "$INFRA/.env" ] || die "infra/.env missing"

# The store's coordinates, from infra's env — the same ones every lane reads.
set -a; . "$INFRA/.env"; set +a
export CLICKHOUSE_HOST=127.0.0.1
export CLICKHOUSE_PORT="${CLICKHOUSE_HTTP_HOST_PORT:-8123}"
export CLICKHOUSE_USER="${CLICKHOUSE_USER:-apex}"
export CLICKHOUSE_PASSWORD="${CLICKHOUSE_PASSWORD:-apex_local_dev}"
export CLICKHOUSE_DATABASE="${CLICKHOUSE_DB:-apex}"
export UV_PYTHON="${UV_PYTHON:-3.12}"
ch() { docker exec apex-infra-clickhouse clickhouse-client --user "$CLICKHOUSE_USER" --password "$CLICKHOUSE_PASSWORD" -q "$1"; }

# --latest: the newest job in the store, resolved with the store's own
# credentials — so a caller (an eval, a cron) need not repeat them.
if [ "$JOB_ID" = "--latest" ]; then
  JOB_ID=$(ch "SELECT job_id FROM apex.spark_events GROUP BY job_id ORDER BY max(ts) DESC LIMIT 1")
  [ -n "$JOB_ID" ] || die "the store holds no job"
fi

API_PORT="${APEX_E2E_API_PORT:-8099}"
# Lane logs go OUTSIDE the tree: nothing here should leave an untracked file behind.
LOGS="${APEX_E2E_LOG_DIR:-${TMPDIR:-/tmp}/apex-e2e-console}"
mkdir -p "$LOGS"
API_URL="http://127.0.0.1:${API_PORT}"
API_PID=""
# The API is `uv run apex-api` under a subshell: killing the subshell leaves
# uvicorn listening. Kill whatever holds the port, which is what "stop the
# API we started" actually means.
api_listeners() { lsof -tiTCP:"$API_PORT" -sTCP:LISTEN 2>/dev/null; }
cleanup() {
  if [ -n "$API_PID" ] && [ "${KEEP_API:-0}" != "1" ]; then
    for pid in $(api_listeners); do kill "$pid" 2>/dev/null; done
    kill "$API_PID" 2>/dev/null; wait "$API_PID" 2>/dev/null
  fi
}
trap cleanup EXIT

step "1/6 the job is in the store (job_id=$JOB_ID)"
[ "$(docker inspect -f '{{.State.Running}}' apex-infra-clickhouse 2>/dev/null)" = "true" ] || die "apex-infra-clickhouse is not running (cd infra && docker compose up -d clickhouse)"
EVENTS=$(ch "SELECT count() FROM apex.spark_events WHERE job_id='$JOB_ID'")
[ "${EVENTS:-0}" -gt 0 ] && ok "spark_events: $EVENTS stage rows" || die "no spark_events rows for $JOB_ID — run the job first (tests/e2e/run.sh)"
CONF_ROWS=$(ch "SELECT count() FROM apex.job_conf WHERE job_id='$JOB_ID'")
note "stages: $(ch "SELECT uniqExact(stage_id) FROM apex.spark_events WHERE job_id='$JOB_ID'") · transitions stored: $(ch "SELECT count() FROM apex.plan_transitions WHERE job_id='$JOB_ID'") · job_conf rows: $CONF_ROWS"
if [ "${CONF_ROWS:-0}" -eq 0 ]; then
  printf '  \033[33mWARN\033[0m %s\n' "no apex.job_conf row: the plugin emitted no apex.job_conf span for this run. config_source will read 'unknown', every conf_* column null, and the no-op gate cannot tell whether a recommended flag was already on. The jar emits it since 2026-07-28 (ApexConfListener) — a dev image built before that, or before any later jar change, predates it: cd dev && make build."
fi

step "2/6 engine: deterministic findings for the job (no LLM)"
if [ "${SKIP_ENGINE:-0}" = "1" ]; then
  note "skipped by SKIP_ENGINE=1"
else
  BEFORE=$(ch "SELECT count() FROM apex.findings WHERE job_id='$JOB_ID'")
  if (cd "$ROOT/engine" && uv run --extra clickhouse python -m apex_engine "$JOB_ID" --no-crew > "$LOGS/engine.log" 2>&1); then
    AFTER=$(ch "SELECT count() FROM apex.findings WHERE job_id='$JOB_ID'")
    ok "engine ran · findings for the job: $BEFORE → $AFTER"
    grep -iE "llm|crew|finding" "$LOGS/engine.log" | head -5 | sed 's/^/      /'
  else
    bad "engine failed — tail of $LOGS/engine.log:"; tail -15 "$LOGS/engine.log" | sed 's/^/      /'
  fi
fi

step "3/6 memory: index the job into plan_memory + run_outcomes"
if [ "${SKIP_MEMORY:-0}" = "1" ]; then
  note "skipped by SKIP_MEMORY=1"
else
  if (cd "$ROOT/memory" && uv run --extra clickhouse python -m apex_memory index --job "$JOB_ID" > "$LOGS/memory.log" 2>&1); then
    ok "memory indexed · run_outcomes rows for the job: $(ch "SELECT count() FROM apex.run_outcomes FINAL WHERE job_id='$JOB_ID'") · shapes known: $(ch "SELECT uniqExact(plan_fingerprint) FROM apex.plan_memory FINAL")"
  else
    bad "memory index failed — tail of $LOGS/memory.log:"; tail -15 "$LOGS/memory.log" | sed 's/^/      /'
  fi
fi

step "4/6 apex-api over the same store (:$API_PORT)"
TOKEN=$(python3 -c 'import secrets; print(secrets.token_urlsafe(24))')
if curl -sf -m 2 "$API_URL/v1/health" >/dev/null 2>&1; then
  die "something already answers on $API_URL — stop it or set APEX_E2E_API_PORT"
fi
(cd "$ROOT/serve" && APEX_API_TOKENS="$TOKEN" APEX_API_HOST=127.0.0.1 APEX_API_PORT="$API_PORT" \
  uv run apex-api > "$LOGS/api.log" 2>&1) &
API_PID=$!
for _ in $(seq 1 40); do curl -sf -m 2 "$API_URL/v1/health" >/dev/null 2>&1 && break; sleep 0.5; done
HEALTH=$(curl -sf -m 5 "$API_URL/v1/health" 2>/dev/null)
echo "$HEALTH" | grep -q '"store":"ok"' && ok "api up · $HEALTH" || { bad "api not healthy: ${HEALTH:-no answer}"; tail -10 "$LOGS/api.log" | sed 's/^/      /'; }
CODE=$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $TOKEN" "$API_URL/v1/runs/$JOB_ID")
[ "$CODE" = "200" ] && ok "GET /v1/runs/$JOB_ID → 200" || bad "GET /v1/runs/$JOB_ID → $CODE"

step "5/6 the console's rows, through both doors (console_parity_gate --job-id, read-only)"
if (cd "$ROOT/serve" && uv run python tools/console_parity_gate.py --job-id "$JOB_ID" --api-url "$API_URL" --api-token "$TOKEN" > "$LOGS/gate.log" 2>&1); then
  ok "parity gate passed"
else
  bad "parity gate failed"
fi
grep -E "^\s+(PASS|FAIL|NOT EXERCISED)|passed ·|CONSOLE_PARITY_GATE" "$LOGS/gate.log" | sed 's/^/      /'

step "6/6 the console itself: the real App against the live API, every screen for the job"
if (cd "$ROOT/front" && APEX_E2E_API_URL="$API_URL" APEX_E2E_API_TOKEN="$TOKEN" APEX_E2E_JOB_ID="$JOB_ID" \
    npx vitest run src/e2e/console.live.test.tsx > "$LOGS/front.log" 2>&1); then
  ok "console reflection passed"
else
  bad "console reflection failed"
fi
grep -E "✓|×|Tests |Test Files|AssertionError|Error:|shows \"" "$LOGS/front.log" | head -40 | sed 's/^/      /'

printf '\n  logs: %s\n' "$LOGS"
if [ $FAIL -eq 0 ]; then
  printf '\033[32m✔ CONSOLE E2E GREEN\033[0m — job_id %s: engine → memory → apex-api → every screen\n' "$JOB_ID"
else
  printf '\033[31m✘ CONSOLE E2E FAILED\033[0m — see FAIL lines above (job_id %s)\n' "$JOB_ID"
fi
[ "${KEEP_API:-0}" = "1" ] && printf '  apex-api left running on %s (pid %s) · token: %s\n' "$API_URL" "$API_PID" "$TOKEN"
exit $FAIL
