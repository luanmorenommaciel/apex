#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# T13 — dev lane E2E exit proof. Builds + starts the cluster, generates the
# deterministic skewed data, runs ALL FOUR pathologies, and asserts each expected
# signal actually appears in the listener's spark_events.jsonl:
#   skew_join   → some stage p99/p50 > 10
#   spill       → total spill_disk_bytes > 0
#   bad_shuffle → a shuffle-read stage with exactly 2 (huge) tasks
#   driver_oom  → the driver OOMs (non-zero exit) AND pre-collect telemetry survived
# Then tears down. KEEP_UP=1 keeps the cluster for inspection.
# ─────────────────────────────────────────────────────────────────────────────
set -uo pipefail
cd "$(dirname "$0")/.."   # → dev/

COMPOSE="docker compose"
MASTER="spark://spark-master:7077"
FAIL=0
ok()   { printf '  \033[32mPASS\033[0m %s\n' "$1"; }
bad()  { printf '  \033[31mFAIL\033[0m %s\n' "$1"; FAIL=1; }
step() { printf '\n\033[1m══ %s ══\033[0m\n' "$1"; }

[ -f .env ] || { echo "no .env — run: cp .env.example .env"; exit 2; }

KEEP_UP="${KEEP_UP:-0}"
teardown() { [ "$KEEP_UP" = "1" ] || { echo; echo "tearing down…"; $COMPOSE down -v --remove-orphans >/dev/null 2>&1; }; }
trap teardown EXIT

submit() {  # jobfile  [extra `docker compose exec` args ...]
  local job="$1"; shift
  $COMPOSE exec -T "$@" spark-master /opt/spark/bin/spark-submit --master "$MASTER" "/opt/apex/jobs/$job"
}

# assert_signal <jsonl> <python-bool-expr over `rows`>
assert_rows() {
  python3 - "$1" <<PY
import json, sys
rows=[json.loads(l) for l in open(sys.argv[1])] if __import__('os').path.exists(sys.argv[1]) else []
sys.exit(0 if ($2) else 1)
PY
}

step "1/6  build + start cluster (wait for health)"
$COMPOSE down -v --remove-orphans >/dev/null 2>&1
$COMPOSE up -d --build --wait --wait-timeout 300 >/dev/null 2>&1 && ok "cluster healthy" || bad "cluster did not come up"

step "2/6  generate deterministic skewed data (~50% hot key)"
$COMPOSE exec -T spark-master /opt/spark/bin/spark-submit --master "$MASTER" \
  /opt/apex/jobs/generate_data.py >out/e2e_gen.log 2>&1
grep -q 'hot_key_~50pct=PASS' out/e2e_gen.log && ok "$(grep -o 'hot_frac=[0-9.]*' out/e2e_gen.log | head -1) hot key" || bad "gen-data hot-key check"

step "3/6  skew_join → p99/p50 > 10"
rm -f out/spark_events.jsonl
submit skew_join.py -e APEX_AQE=off >out/e2e_skew_join.log 2>&1
if assert_rows out/spark_events.jsonl "any(r['task_duration_p50_ms'] and r['task_duration_p99_ms']/r['task_duration_p50_ms']>10 for r in rows)"; then
  mx=$(python3 -c "import json;rs=[json.loads(l) for l in open('out/spark_events.jsonl')];print(round(max((r['task_duration_p99_ms']/r['task_duration_p50_ms']) for r in rs if r['task_duration_p50_ms']),1))")
  ok "skew present (max p99/p50 = ${mx}x)"
else bad "no stage with p99/p50 > 10"; fi

step "4/6  spill → spill_disk_bytes > 0"
rm -f out/spark_events.jsonl
submit spill.py -e APEX_FIX=off >out/e2e_spill.log 2>&1
if assert_rows out/spark_events.jsonl "sum(r['spill_disk_bytes'] for r in rows) > 0"; then
  sp=$(python3 -c "import json;rs=[json.loads(l) for l in open('out/spark_events.jsonl')];print(sum(r['spill_disk_bytes'] for r in rs))")
  ok "spill present (spill_disk_bytes = ${sp})"
else bad "spill_disk_bytes == 0"; fi

step "5/6  bad_shuffle → a shuffle-read stage with exactly 2 huge tasks"
rm -f out/spark_events.jsonl
submit bad_shuffle.py -e APEX_FIX=off >out/e2e_bad_shuffle.log 2>&1
if assert_rows out/spark_events.jsonl "any(r['task_count']==2 and r['shuffle_read_bytes']>1_000_000 for r in rows)"; then
  ok "bad shuffle present (2 tasks over a large shuffle read)"
else bad "no 2-task large-shuffle reduce stage"; fi

step "6/6  driver_oom → OOM + pre-collect telemetry survives"
rm -f out/spark_events.jsonl
$COMPOSE exec -T -e APEX_SAFE=off spark-master /opt/spark/bin/spark-submit --master "$MASTER" \
  --driver-memory 512m /opt/apex/jobs/driver_oom.py >out/e2e_driver_oom.log 2>&1
rc=$?
[ "$rc" -ne 0 ] && ok "driver process failed as expected (exit $rc)" || bad "driver did NOT fail (exit 0)"
grep -qiE 'OutOfMemoryError|Java heap space|GC overhead' out/e2e_driver_oom.log \
  && ok "OutOfMemoryError observed in driver log" \
  || echo "  note: OOM not textually in log (exit $rc); pre-collect record check below is the real proof"
if [ -s out/spark_events.jsonl ]; then
  ok "pre-collect telemetry survived the OOM ($(wc -l <out/spark_events.jsonl | tr -d ' ') records on disk)"
else bad "no pre-collect records survived"; fi

echo
if [ "$FAIL" = 0 ]; then
  printf '\033[1;32m✔ E2E PASSED — all 4 pathologies produce their expected signals\033[0m\n'
else
  printf '\033[1;31mx E2E FAILED — see failures above\033[0m\n'
fi
exit $FAIL
