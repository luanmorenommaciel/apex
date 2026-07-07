#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"
set -a
source .env.example
source .env
set +a
COMPOSE=(docker compose --env-file .env -f build/docker-compose.yml)

query="SELECT * FROM (SELECT 'raw' AS table_name, count() AS rows FROM spark_raw_events UNION ALL SELECT 'sql', count() FROM spark_sql_executions UNION ALL SELECT 'stages', count() FROM spark_stages UNION ALL SELECT 'tasks', count() FROM spark_tasks) ORDER BY table_name"
counts="$("${COMPOSE[@]}" exec -T clickhouse clickhouse-client --user "$CLICKHOUSE_USER" --password "$CLICKHOUSE_PASSWORD" --database "$CLICKHOUSE_DB" --query "$query")"
echo "$counts"

for table_name in raw sql stages tasks; do
  rows="$(awk -v table="$table_name" '$1 == table {print $2}' <<<"$counts")"
  if [[ -z "$rows" || "$rows" == "0" ]]; then
    echo "ClickHouse table $table_name has no rows" >&2
    exit 1
  fi
done

echo "ClickHouse validation passed"
