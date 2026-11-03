#!/usr/bin/env bash
# Apex infra · restore — bring a scripts/backup.sh snapshot back.
#
# Usage:  make restore FILE=backups/<stamp>-clickhouse.zip [INTO=<database>] [MONGO=backups/<stamp>-mongo.archive]
#         ./scripts/restore.sh <stamp>-clickhouse.zip [--into DATABASE] [--mongo ARCHIVE] [--force]
#
#   default        restores the archive AS a new database you name with --into (nothing
#                  running is touched — inspect, then swap or copy what you need)
#   --force        restores OVER apex (and OVER the hyperdx Mongo db when --mongo is given);
#                  refused without the flag because it replaces live data
set -euo pipefail
cd "$(dirname "$0")/.."
ENV_FILE="${INFRA_ENV_FILE:-.env}"
set -a; [ -f "$ENV_FILE" ] && . "$ENV_FILE"; set +a

fail() { echo "❌ restore: $1"; exit 1; }
[ $# -ge 1 ] || fail "usage: restore.sh <backup-clickhouse.zip> [--into DATABASE] [--mongo ARCHIVE] [--force]"
ARCHIVE="$1"; shift
INTO=""; MONGO_ARCHIVE=""; FORCE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --into)  INTO="$2"; shift 2 ;;
    --mongo) MONGO_ARCHIVE="$2"; shift 2 ;;
    --force) FORCE=1; shift ;;
    *) fail "unknown argument $1" ;;
  esac
done
[ -f "$ARCHIVE" ] || fail "$ARCHIVE does not exist"
[ -n "$INTO" ] || [ "$FORCE" = "1" ] || fail "restoring OVER apex replaces live data: pass --into <new database> to restore beside it, or --force to overwrite"

CONTAINER="${INFRA_CLICKHOUSE_CONTAINER:-apex-infra-clickhouse}"
MONGO="${INFRA_MONGO_CONTAINER:-apex-infra-mongodb}"
CH_USER="${CLICKHOUSE_USER:-apex}"
CH_PASS="${CLICKHOUSE_PASSWORD:-$(cat "${INFRA_SECRETS_DIR:-secrets}/clickhouse_password" 2>/dev/null || true)}"
[ -n "$CH_PASS" ] || fail "CLICKHOUSE_PASSWORD is required (set it in infra/.env and run scripts/preflight.sh; there is no default)"
chq() { docker exec -i "$CONTAINER" clickhouse-client --user "$CH_USER" --password "$CH_PASS" "$@"; }

name="restore-$(date -u +%Y%m%dT%H%M%SZ).zip"
docker cp "$ARCHIVE" "$CONTAINER:/var/lib/clickhouse/backups/$name"
# docker cp lands the file as root; the server runs as clickhouse and must be able to read it.
docker exec -u root "$CONTAINER" chown clickhouse:clickhouse "/var/lib/clickhouse/backups/$name"
if [ -n "$INTO" ]; then
  echo "── ClickHouse: RESTORE DATABASE apex AS $INTO FROM Disk('backups', '$name')"
  chq --query "RESTORE DATABASE apex AS $INTO FROM Disk('backups', '$name')" >/dev/null
else
  echo "── ClickHouse: RESTORE DATABASE apex FROM Disk('backups', '$name') (--force: overwriting)"
  chq --query "RESTORE DATABASE apex FROM Disk('backups', '$name') SETTINGS allow_non_empty_tables = 1" >/dev/null
fi
docker exec "$CONTAINER" rm -f "/var/lib/clickhouse/backups/$name"

if [ -n "$MONGO_ARCHIVE" ]; then
  [ -f "$MONGO_ARCHIVE" ] || fail "$MONGO_ARCHIVE does not exist"
  [ "$FORCE" = "1" ] || fail "restoring the hyperdx Mongo db replaces dashboards/sources/users: pass --force"
  echo "── MongoDB: mongorestore --archive --drop (db hyperdx)"
  docker exec -i "$MONGO" mongorestore --quiet --archive --drop --nsInclude 'hyperdx.*' < "$MONGO_ARCHIVE"
fi
echo "✅ restore complete${INTO:+ into $INTO}"
