#!/usr/bin/env bash
# Apex infra · apply-ddl — apply every file in sql/, in filename order, against the
# RUNNING ClickHouse.
#
# Why this exists: ClickHouse only runs /docker-entrypoint-initdb.d on FIRST boot. On a
# pre-existing volume, any DDL file added to sql/ later is SILENTLY skipped — the database
# looks "applied" while new columns/tables are missing (the spark-conf lane hit exactly
# this with 013_/021_). This script closes the gap without a volume wipe.
#
# Two modes, same logic:
#   host (default)       docker exec into $INFRA_CLICKHOUSE_CONTAINER — `make apply-ddl`
#   container            APPLY_DDL_MODE=container: run clickhouse-client directly against
#                        $CLICKHOUSE_HOST. This is what the compose `ddl-migrate` one-shot
#                        service does on EVERY `docker compose up`, after clickhouse is
#                        healthy and before hyperdx/otel-collector start, so a running
#                        store converges on sql/ without anyone remembering to.
#
# Idempotency lives in the SQL files themselves: CREATE ... IF NOT EXISTS for new objects,
# ALTER ... ADD COLUMN IF NOT EXISTS for columns added to pre-existing tables. Re-running
# is always safe and a no-op once the schema is current.
#
# Usage:  make apply-ddl   (or ./scripts/apply_ddl.sh)
set -euo pipefail
cd "$(dirname "$0")/.."
ENV_FILE="${INFRA_ENV_FILE:-.env}"
set -a; [ -f "$ENV_FILE" ] && . "$ENV_FILE"; set +a

MODE="${APPLY_DDL_MODE:-host}"
SQL_DIR="${SQL_DIR:-sql}"
CONTAINER="${INFRA_CLICKHOUSE_CONTAINER:-apex-infra-clickhouse}"
CH_HOST="${CLICKHOUSE_HOST:-apex-infra-clickhouse}"
CH_USER="${CLICKHOUSE_USER:-apex}"
CH_PASS="${CLICKHOUSE_PASSWORD:-$(cat "${INFRA_SECRETS_DIR:-secrets}/clickhouse_password" 2>/dev/null || true)}"
[ -n "$CH_PASS" ] || { echo "❌ CLICKHOUSE_PASSWORD is required (set it in infra/.env and run scripts/preflight.sh; there is no default)"; exit 1; }

# chq [client args...] — clickhouse-client in whichever mode, stdin passed through.
if [ "$MODE" = "container" ]; then
  chq() { clickhouse-client --host "$CH_HOST" --user "$CH_USER" --password "$CH_PASS" "$@"; }
  for _ in $(seq 1 30); do chq --query "SELECT 1" >/dev/null 2>&1 && break; sleep 2; done
  chq --query "SELECT 1" >/dev/null || { echo "❌ ClickHouse at $CH_HOST is not answering"; exit 1; }
else
  chq() { docker exec -i "$CONTAINER" clickhouse-client --user "$CH_USER" --password "$CH_PASS" "$@"; }
  st=$(docker inspect -f '{{.State.Status}}' "$CONTAINER" 2>/dev/null || echo missing)
  [ "$st" = "running" ] || { echo "❌ $CONTAINER is not running — 'docker compose up -d' first"; exit 1; }
fi

for f in "$SQL_DIR"/*.sql; do
  printf '   applying %-32s' "$(basename "$f")"
  if chq --multiquery < "$f" >/dev/null; then
    echo "ok"
  else
    echo "FAILED"
    echo "❌ apply-ddl stopped at $f — fix the DDL and re-run (earlier files are idempotent)"
    exit 1
  fi

  # Defense-in-depth (apex #72): `CREATE MATERIALIZED VIEW ... TO <table>` succeeds
  # even when <table> doesn't exist yet — ClickHouse gives no error at DDL time. Left
  # unchecked, the gap surfaces later as a total, silent-at-bootstrap INSERT failure on
  # the MV's source table. Verify every target table this file declared actually exists,
  # right after applying it, so a broken ordering fails loudly here instead of on the
  # first real span. The file is flattened first (comments stripped, newlines -> spaces)
  # because `CREATE MATERIALIZED VIEW <name>` and `TO <target>` may sit on separate lines
  # (010_otel_traces.sql does), which a line-by-line grep never matches.
  for target in $(sed 's/--.*$//' "$f" | tr '\n' ' ' \
                    | grep -oiE 'MATERIALIZED[[:space:]]+VIEW[[:space:]]+(IF[[:space:]]+NOT[[:space:]]+EXISTS[[:space:]]+)?[A-Za-z0-9_.]+[[:space:]]+TO[[:space:]]+[A-Za-z0-9_.]+' \
                    | grep -oE '[A-Za-z0-9_.]+$'); do
    exists=$(chq --query "EXISTS TABLE $target" 2>/dev/null </dev/null | tr -d '[:space:]')
    if [ "$exists" != "1" ]; then
      echo "❌ apply-ddl: $f creates a MATERIALIZED VIEW targeting '$target', but that table does not exist"
      echo "   Every insert into the view's source table will now fail until '$target' exists."
      echo "   Fix: make sure the migration creating '$target' sorts before $f, then re-run."
      exit 1
    fi
  done
done
echo "✅ apply-ddl complete — $SQL_DIR/ fully applied ($MODE mode)"
