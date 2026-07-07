#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"
set -a
source .env.example
source .env
set +a
COMPOSE=(docker compose --env-file .env -f build/docker-compose.yml)

wait_for() {
  local name="$1"
  shift
  for attempt in $(seq 1 60); do
    if "$@" >/dev/null 2>&1; then
      echo "$name is ready"
      return 0
    fi
    sleep 2
  done
  echo "Timed out waiting for $name" >&2
  return 1
}

wait_for "ClickHouse" "${COMPOSE[@]}" exec -T clickhouse clickhouse-client --user "$CLICKHOUSE_USER" --password "$CLICKHOUSE_PASSWORD" --query "SELECT 1"
wait_for "Spark Master" curl -fsS "http://127.0.0.1:${SPARK_MASTER_UI_PORT}"
wait_for "Spark History" curl -fsS "http://127.0.0.1:${SPARK_HISTORY_UI_PORT}/api/v1/applications"
wait_for "MinIO Console" curl -fsS "http://127.0.0.1:${MINIO_CONSOLE_PORT}"
