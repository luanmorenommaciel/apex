#!/usr/bin/env bash
# Apex infra · apply-ddl — apply every file in sql/, in filename order, against the
# RUNNING ClickHouse container.
#
# Why this exists: ClickHouse only runs /docker-entrypoint-initdb.d on FIRST boot. On a
# pre-existing volume, any DDL file added to sql/ later is SILENTLY skipped — the database
# looks "applied" while new columns/tables are missing (the spark-conf lane hit exactly
# this with 013_/021_). This script closes the gap without a volume wipe.
#
# Idempotency lives in the SQL files themselves: CREATE ... IF NOT EXISTS for new objects,
# ALTER ... ADD COLUMN IF NOT EXISTS for columns added to pre-existing tables. Re-running
# is always safe and a no-op once the schema is current.
#
# Usage:  make apply-ddl   (or ./scripts/apply_ddl.sh)
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; [ -f .env ] && . ./.env; set +a

CONTAINER="${INFRA_CLICKHOUSE_CONTAINER:-apex-infra-clickhouse}"
CH_USER="${CLICKHOUSE_USER:-apex}"
CH_PASS="${CLICKHOUSE_PASSWORD:-apex_local_dev}"

st=$(docker inspect -f '{{.State.Status}}' "$CONTAINER" 2>/dev/null || echo missing)
[ "$st" = "running" ] || { echo "❌ $CONTAINER is not running — 'docker compose up -d' first"; exit 1; }

for f in sql/*.sql; do
  printf '   applying %-32s' "$(basename "$f")"
  if docker exec -i "$CONTAINER" clickhouse-client \
      --user "$CH_USER" --password "$CH_PASS" --multiquery < "$f" >/dev/null; then
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
  # first real span.
  for target in $(grep -oiE 'MATERIALIZED VIEW[^;]*\bTO\b[[:space:]]+[A-Za-z0-9_.]+' "$f" \
                    | grep -oE '[A-Za-z0-9_.]+$'); do
    exists=$(docker exec -i "$CONTAINER" clickhouse-client \
        --user "$CH_USER" --password "$CH_PASS" \
        --query "EXISTS TABLE $target" 2>/dev/null | tr -d '[:space:]')
    if [ "$exists" != "1" ]; then
      echo "❌ apply-ddl: $f creates a MATERIALIZED VIEW targeting '$target', but that table does not exist"
      echo "   Every insert into the view's source table will now fail until '$target' exists."
      echo "   Fix: make sure the migration creating '$target' sorts before $f, then re-run."
      exit 1
    fi
  done
done
echo "✅ apply-ddl complete — sql/ fully applied to $CONTAINER"
