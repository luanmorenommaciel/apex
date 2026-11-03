#!/usr/bin/env bash
# Apex infra · backup — one consistent snapshot of the canonical store, on the host.
#
#   ClickHouse  BACKUP DATABASE apex TO Disk('backups', '<stamp>.zip')  (config.d/backups.xml)
#               then docker cp of the archive -> $BACKUP_DIR/<stamp>-clickhouse.zip
#   MongoDB     mongodump --archive of the hyperdx db (dashboards, sources, users)
#               -> $BACKUP_DIR/<stamp>-mongo.archive
#
# Usage:  make backup                      (or ./scripts/backup.sh)
#   BACKUP_DIR            host directory, default ./backups (gitignored)
#   SKIP_MONGO=1          ClickHouse only (tests, or a stack without HyperDX)
#   INFRA_CLICKHOUSE_CONTAINER / INFRA_MONGO_CONTAINER   container overrides
set -euo pipefail
cd "$(dirname "$0")/.."
ENV_FILE="${INFRA_ENV_FILE:-.env}"
set -a; [ -f "$ENV_FILE" ] && . "$ENV_FILE"; set +a

CONTAINER="${INFRA_CLICKHOUSE_CONTAINER:-apex-infra-clickhouse}"
MONGO="${INFRA_MONGO_CONTAINER:-apex-infra-mongodb}"
CH_USER="${CLICKHOUSE_USER:-apex}"
CH_PASS="${CLICKHOUSE_PASSWORD:-$(cat "${INFRA_SECRETS_DIR:-secrets}/clickhouse_password" 2>/dev/null || true)}"
[ -n "$CH_PASS" ] || { echo "❌ CLICKHOUSE_PASSWORD is required (set it in infra/.env and run scripts/preflight.sh; there is no default)"; exit 1; }
BACKUP_DIR="${BACKUP_DIR:-backups}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$BACKUP_DIR"

chq() { docker exec -i "$CONTAINER" clickhouse-client --user "$CH_USER" --password "$CH_PASS" "$@"; }

echo "── ClickHouse: BACKUP DATABASE apex -> Disk('backups', '${STAMP}.zip')"
chq --query "BACKUP DATABASE apex TO Disk('backups', '${STAMP}.zip')" >/dev/null
docker cp "$CONTAINER:/var/lib/clickhouse/backups/${STAMP}.zip" "$BACKUP_DIR/${STAMP}-clickhouse.zip"
chq --query "SYSTEM UNFREEZE" >/dev/null 2>&1 || true
echo "   -> $BACKUP_DIR/${STAMP}-clickhouse.zip ($(du -h "$BACKUP_DIR/${STAMP}-clickhouse.zip" | cut -f1))"

if [ "${SKIP_MONGO:-0}" != "1" ]; then
  echo "── MongoDB: mongodump --archive (db hyperdx: dashboards, sources, users)"
  docker exec "$MONGO" mongodump --quiet --archive --db hyperdx > "$BACKUP_DIR/${STAMP}-mongo.archive"
  echo "   -> $BACKUP_DIR/${STAMP}-mongo.archive ($(du -h "$BACKUP_DIR/${STAMP}-mongo.archive" | cut -f1))"
fi
echo "✅ backup ${STAMP} complete in $BACKUP_DIR/"
