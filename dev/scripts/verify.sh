#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Apex dev-env DOCTOR — the one command that proves fresh-clone reproducibility.
# Fresh clone → `cp .env.example .env && make verify` must pass on any host.
#
# Steps: (1) .env quartet consistent · (2) all 4 JARs reachable · (3) clean build+up
#        waiting for every healthcheck green · (4) smoke Delta write/read on MinIO ·
#        (5) event log landed in MinIO · (6) app visible in the History Server · teardown.
#
# Env: KEEP_UP=1 skips the final teardown (for debugging a failed run).
# ─────────────────────────────────────────────────────────────────────────────
set -uo pipefail
cd "$(dirname "$0")/.."   # → dev/

COMPOSE="docker compose"
FAIL=0
ok()   { printf '  \033[32mPASS\033[0m %s\n' "$1"; }
bad()  { printf '  \033[31mFAIL\033[0m %s\n' "$1"; FAIL=1; }
step() { printf '\n\033[1m══ %s ══\033[0m\n' "$1"; }

[ -f .env ] || { echo "no .env — run: cp .env.example .env"; exit 2; }
set -a; . ./.env; set +a

KEEP_UP="${KEEP_UP:-0}"
teardown() { [ "$KEEP_UP" = "1" ] || { echo; echo "tearing down…"; $COMPOSE down -v --remove-orphans >/dev/null 2>&1; }; }
trap teardown EXIT

# ── 1: version quartet is internally consistent ─────────────────────────────
step "1/6  .env version quartet"
if [ -n "${SPARK_IMAGE:-}" ] && [ -n "${HADOOP_AWS_VERSION:-}" ] && [ -n "${DELTA_VERSION:-}" ] \
   && [ -n "${SCALA_BIN:-}" ] && [ -n "${AWS_SDK_BUNDLE_VERSION:-}" ]; then
  ok "quartet present — spark=$SPARK_IMAGE · hadoop-aws=$HADOOP_AWS_VERSION · delta=$DELTA_VERSION · scala=$SCALA_BIN · sdk=$AWS_SDK_BUNDLE_VERSION"
else
  bad "quartet incomplete in .env"
fi
case "$SPARK_IMAGE" in
  *scala${SCALA_BIN}*) ok "SCALA_BIN=$SCALA_BIN matches image tag" ;;
  *) bad "SCALA_BIN=$SCALA_BIN not present in image tag ($SPARK_IMAGE)" ;;
esac

# ── 2: all four Maven JARs reachable (the exact ones baked into the image) ───
step "2/6  Maven JAR reachability"
M=https://repo1.maven.org/maven2
for u in \
  "$M/org/apache/hadoop/hadoop-aws/$HADOOP_AWS_VERSION/hadoop-aws-$HADOOP_AWS_VERSION.jar" \
  "$M/software/amazon/awssdk/bundle/$AWS_SDK_BUNDLE_VERSION/bundle-$AWS_SDK_BUNDLE_VERSION.jar" \
  "$M/io/delta/delta-spark_$SCALA_BIN/$DELTA_VERSION/delta-spark_$SCALA_BIN-$DELTA_VERSION.jar" \
  "$M/io/delta/delta-storage/$DELTA_VERSION/delta-storage-$DELTA_VERSION.jar"; do
  c=$(curl -s -o /dev/null -w '%{http_code}' -I "$u")
  [ "$c" = 200 ] && ok "200  ${u##*/}" || bad "$c  ${u##*/}"
done

# ── 3: clean start → build → up, waiting for all healthchecks green ──────────
step "3/6  clean build + readiness-gated startup"
$COMPOSE down -v --remove-orphans >/dev/null 2>&1
if $COMPOSE up -d --build --wait --wait-timeout 300 >/dev/null 2>&1; then
  ok "all services reached healthy (compose --wait, dependency-ordered)"
else
  bad "compose up --wait did not reach healthy within 300s"
fi
$COMPOSE ps --format '  {{.Service}}\t{{.State}}\t{{.Status}}'

# ── 4: smoke Delta write/read on MinIO ──────────────────────────────────────
step "4/6  smoke Delta write/read"
$COMPOSE exec -T spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 --deploy-mode client \
  /opt/apex/scripts/smoke_delta.py >out/smoke.log 2>&1
if grep -q "APEX_SMOKE ok" out/smoke.log; then
  ok "Delta round-trip ok ($(grep -o 'delta_roundtrip_count=[0-9]*' out/smoke.log | head -1))"
else
  bad "smoke job did not report success (see out/smoke.log)"; tail -5 out/smoke.log | sed 's/^/      /'
fi

# ── 5: event log object actually landed in MinIO ────────────────────────────
step "5/6  event log in MinIO (s3a://$LOGS_BUCKET/events/)"
LOGS=$($COMPOSE exec -T minio sh -c "mc alias set local http://localhost:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD >/dev/null 2>&1; mc ls --recursive local/$LOGS_BUCKET/events/ 2>/dev/null" | grep -v '\.keep' || true)
if [ -n "$LOGS" ]; then
  ok "event log present:"; echo "$LOGS" | sed 's/^/      /'
else
  bad "no event log object under events/ (only the .keep marker)"
fi

# ── 6: app shows up in the History Server REST API ──────────────────────────
step "6/6  History Server lists the app"
HP=${SPARK_HISTORY_PORT:-18080}
found=""
for _ in $(seq 1 20); do
  j=$(curl -s "http://localhost:$HP/api/v1/applications" 2>/dev/null)
  if echo "$j" | grep -q '"id"'; then found="$j"; break; fi
  sleep 3
done
if [ -n "$found" ]; then
  ok "History Server lists: $(echo "$found" | grep -oE '"name" *: *"[^"]*"' | head -3 | tr '\n' ' ')"
else
  bad "no application in History Server after ~60s"
fi

# ── verdict ─────────────────────────────────────────────────────────────────
echo
if [ "$FAIL" = 0 ]; then
  printf '\033[1;32m✔ VERIFY PASSED — dev environment is reproducible end-to-end\033[0m\n'
else
  printf '\033[1;31mx VERIFY FAILED — see failures above\033[0m\n'
fi
exit $FAIL
