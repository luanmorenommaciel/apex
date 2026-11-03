#!/usr/bin/env bash
# Apex infra · gate — the integration proof of the hardened stack, end to end, on THIS host.
#
# Every leaf of the infra hardening proves itself on a disposable server or a rendered
# compose; this is the one run that boots the REAL stack from .env, with secrets, migration,
# HyperDX bootstrap, a collector restart mid-outage and the e2e runner, and prints one
# PASS/FAIL line per step. Exit 0 only if every step passed. Record a run in VALIDATION.md.
#
# Usage:  make gate WIPE=1|0            (APEX_CLUSTER_SLOTS=8 WIPE=1 ./scripts/gate.sh)
#   WIPE=1   docker compose down -v first: proves the FRESH path (initdb, bootstrap, first user)
#   WIPE=0   keep the volumes: proves the CONVERGE path (ddl-migrate on a pre-existing volume)
#            — the flag is REQUIRED either way, because WIPE=1 deletes the store.
#   APEX_CLUSTER_SLOTS   cluster width for the skew verdict (dev lab = 8); REQUIRED
#   SKIP_E2E=1           stop after the store proof (no dev lane build/run)
#   SKIP_BUILD / DEV_EXTRA_COMPOSE_FILES   passed through to tests/e2e/run.sh
# Refuses to run while another lane's stack (apex-dev-*, apex-collect / apex-otel-collector)
# is up: the e2e runner brings dev up itself and a stale dev image is a known trap.
set -uo pipefail
cd "$(dirname "$0")/.."
ROOT="$(cd .. && pwd)"

FAIL=0
ok()   { printf '  \033[32mPASS\033[0m %s\n' "$1"; }
bad()  { printf '  \033[31mFAIL\033[0m %s\n' "$1"; FAIL=1; }
step() { printf '\n\033[1m== %s ==\033[0m\n' "$1"; }
die()  { printf '\033[31mABORT:\033[0m %s\n' "$1"; exit 2; }

step "0/9 preconditions"
command -v docker >/dev/null || die "docker is required"
[ -f .env ] || die "infra/.env missing — cp .env.example .env and set the four credentials"
case "${WIPE:-}" in
  1) ok "WIPE=1: the infra volumes will be deleted (fresh path)" ;;
  0) ok "WIPE=0: volumes kept (converge path)" ;;
  *) die "WIPE must be set explicitly: WIPE=1 (delete the store, fresh path) or WIPE=0 (keep it, converge path)" ;;
esac
[ -n "${APEX_CLUSTER_SLOTS:-}" ] || die "APEX_CLUSTER_SLOTS is required (dev lab = 8); the skew verdict never guesses a width"
busy=$(docker ps --format '{{.Names}}' | grep -E '^(apex-dev-|apex-collect|apex-otel-collector|apex-queue-init|apex-clickhouse)' || true)
[ -z "$busy" ] || die "another lane's stack is running ($(echo "$busy" | tr '\n' ' ')) — stop it first; the e2e runner brings dev up itself"
ok "no foreign apex stack running"

step "1/9 volumes"
if [ "$WIPE" = "1" ]; then
  docker compose down -v --remove-orphans >/dev/null 2>&1 || true
  left=$(docker volume ls --format '{{.Name}}' | grep '^apex-infra_' || true)
  [ -z "$left" ] && ok "infra volumes removed" || bad "volumes still present: $left"
else
  docker compose down --remove-orphans >/dev/null 2>&1 || true
  ok "stack stopped, volumes kept: $(docker volume ls --format '{{.Name}}' | grep '^apex-infra_' | tr '\n' ' ')"
fi

step "2/9 make up (preflight -> compose up --wait -> HyperDX bootstrap)"
if make up; then ok "make up"; else die "make up failed — nothing below is meaningful"; fi
for c in apex-infra-clickhouse apex-infra-mongodb apex-infra-hyperdx apex-infra-otel-collector; do
  st=$(docker inspect -f '{{.State.Status}}' "$c" 2>/dev/null || echo missing)
  [ "$st" = "running" ] && ok "$c running" || bad "$c is $st"
done
mig=$(docker inspect -f '{{.State.Status}}/{{.State.ExitCode}}' apex-infra-ddl-migrate 2>/dev/null || echo missing)
[ "$mig" = "exited/0" ] && ok "ddl-migrate completed (exit 0)" || bad "ddl-migrate: $mig"

step "3/9 seed + verify.sh (APEX_CLUSTER_SLOTS=$APEX_CLUSTER_SLOTS)"
./scripts/seed.sh >/dev/null 2>&1 && ok "seed.sh" || bad "seed.sh"
if ./scripts/verify.sh >/tmp/apex-gate-verify.$$ 2>&1; then ok "verify.sh (exit criterion + tail-bound stage)"; else bad "verify.sh: $(tail -3 /tmp/apex-gate-verify.$$ | tr '\n' ' ')"; fi
rm -f /tmp/apex-gate-verify.$$

step "4/9 make verify-ddl (every object, clause by clause)"
if out=$(make verify-ddl 2>&1); then ok "verify-ddl: $(echo "$out" | tail -1)"; else bad "verify-ddl: $(echo "$out" | grep '❌' | head -3 | tr '\n' ' ')"; fi

step "5/9 no admin password in any container environment; every port on loopback"
admin=$(cat secrets/clickhouse_password)
leak=0
for c in $(docker ps -a --format '{{.Names}}' | grep '^apex-infra-'); do
  if docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' "$c" | grep -qF -- "$admin"; then bad "$c carries the admin password in its environment"; leak=1; fi
done
[ "$leak" = 0 ] && ok "docker inspect: admin password in no apex-infra-* environment"
bind="${BIND_HOST:-127.0.0.1}"
exposed=$(docker ps --format '{{.Names}}' | grep '^apex-infra-' | while read -r c; do docker inspect -f '{{range $p, $b := .NetworkSettings.Ports}}{{range $b}}{{.HostIp}} {{end}}{{end}}' "$c"; done | tr ' ' '\n' | grep -v '^$' | grep -v "^${bind}$" || true)
[ -z "$exposed" ] && ok "every published port is bound to ${bind}" || bad "ports bound elsewhere: $(echo "$exposed" | sort -u | tr '\n' ' ')"

step "6/9 HyperDX seeded through the API as the read-only user"
api="http://127.0.0.1:$(grep -E '^HYPERDX_API_HOST_PORT=' .env | cut -d= -f2 | tail -1)"
[ "$(curl -sf -m 10 "$api/installation" 2>/dev/null)" = '{"isTeamExisting":true}' ] && ok "GET /installation: team exists" || bad "no HyperDX team after bootstrap"
conn=$(docker exec apex-infra-mongodb mongosh --quiet hyperdx --eval 'print(db.connections.findOne({}).username)' 2>/dev/null)
[ "$conn" = "apex_hdx" ] && ok "HyperDX connection user: $conn" || bad "HyperDX connection user is '${conn:-<none>}', expected apex_hdx"
src=$(docker exec apex-infra-mongodb mongosh --quiet hyperdx --eval 'print(db.sources.countDocuments({name:"Spark Events"}))' 2>/dev/null)
[ "${src:-0}" -ge 1 ] && ok "Spark Events source seeded" || bad "Spark Events source missing"

step "7/9 collector restart during a ClickHouse outage loses nothing"
otlp="http://127.0.0.1:$(grep -E '^OTLP_HTTP_HOST_PORT=' .env | cut -d= -f2 | tail -1)/v1/traces"
job="gate-$(date -u +%Y%m%dT%H%M%SZ)"
now_ms=$(python3 -c 'import time; print(int(time.time()*1000))')
payload=$(python3 - "$job" "$now_ms" <<'PY'
import json, sys
job, now_ms = sys.argv[1], int(sys.argv[2])
attrs = {"job_id": job, "app_id": "gate", "app_name": "gate", "stage_id": "1", "stage_attempt": "0", "ts": str(now_ms),
         "task_count": "8", "task_duration_p50_ms": "100", "task_duration_p99_ms": "200", "plan_fingerprint": "f" * 64, "plan_json": "{}"}
span = {"traceId": "%032x" % now_ms, "spanId": "%016x" % (now_ms % 10**15), "name": "apex.stage", "kind": 2,
        "startTimeUnixNano": str(now_ms * 10**6), "endTimeUnixNano": str(now_ms * 10**6),
        "attributes": [{"key": k, "value": {"stringValue": v}} for k, v in attrs.items()]}
print(json.dumps({"resourceSpans": [{"resource": {"attributes": [{"key": "service.name", "value": {"stringValue": "apex-gate"}}]},
                                     "scopeSpans": [{"scope": {"name": "apex.gate"}, "spans": [span]}]}]}))
PY
)
docker stop apex-infra-clickhouse >/dev/null && ok "clickhouse stopped"
code=$(curl -s -m 10 -o /dev/null -w '%{http_code}' -X POST -H 'Content-Type: application/json' --data "$payload" "$otlp")
[ "$code" = "200" ] && ok "span accepted by the collector while ClickHouse is down (HTTP $code)" || bad "collector answered HTTP $code"
docker restart apex-infra-otel-collector >/dev/null && ok "collector restarted (queue must come back from file_storage)"
docker start apex-infra-clickhouse >/dev/null && ok "clickhouse started"
landed=0
for _ in $(seq 1 36); do
  n=$(docker exec apex-infra-clickhouse clickhouse-client --user "${CLICKHOUSE_USER:-apex}" --password "$admin" \
        --query "SELECT count() FROM apex.spark_events WHERE job_id = '$job'" 2>/dev/null || echo 0)
  [ "${n:-0}" -ge 1 ] && { landed=1; break; }
  sleep 5
done
[ "$landed" = 1 ] && ok "the span landed in spark_events after the restart (job_id $job)" || bad "span $job never landed after the collector restart"

step "8/9 tests/e2e/run.sh (dev -> jar -> collector -> ClickHouse -> HyperDX)"
if [ "${SKIP_E2E:-0}" = "1" ]; then
  echo "  SKIP (SKIP_E2E=1)"
else
  # TEARDOWN=1: the runner takes the dev lane down again afterwards (and stops infra, keeping
  # its volumes), so a second gate run is not refused by the stack this one left behind.
  if ( cd "$ROOT" && APEX_CLUSTER_SLOTS="$APEX_CLUSTER_SLOTS" TEARDOWN=1 tests/e2e/run.sh ); then ok "e2e runner green"; else bad "e2e runner failed (see its FAIL lines above)"; fi
fi

step "9/9 result"
if [ "$FAIL" = 0 ]; then
  printf '\033[32m✔ INFRA GATE GREEN\033[0m — WIPE=%s, slots=%s, %s\n' "$WIPE" "$APEX_CLUSTER_SLOTS" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
else
  printf '\033[31m✘ INFRA GATE FAILED\033[0m — see FAIL lines above\n'
fi
exit $FAIL
