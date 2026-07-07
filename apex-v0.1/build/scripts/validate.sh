#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

build/scripts/validate-bootstrap.sh

set -a
source .env.example
source .env
set +a

for tool in docker make curl; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Missing required tool: $tool" >&2
    exit 1
  fi
done

# Port-in-use check needs at least one of ss (Linux/iproute2), lsof, or netstat.
# ss is Linux-only; macOS ships lsof/netstat instead.
if ! command -v ss >/dev/null 2>&1 \
  && ! command -v lsof >/dev/null 2>&1 \
  && ! command -v netstat >/dev/null 2>&1; then
  echo "Missing required tool: need one of ss, lsof, or netstat for port checks" >&2
  exit 1
fi

# Portable listener check: returns 0 if a TCP port is already bound (LISTEN).
port_in_use() {
  local port="$1"
  if command -v ss >/dev/null 2>&1; then
    ss -ltnH 2>/dev/null | awk '{print $4}' | grep -Eq "(^|:)${port}$"
  elif command -v lsof >/dev/null 2>&1; then
    lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
  else
    netstat -an 2>/dev/null | grep -E "[.:]${port}[[:space:]]" | grep -qi 'listen'
  fi
}

docker compose version >/dev/null

for image in "$SPARK_RUNTIME_IMAGE" "$SPARK_HISTORY_IMAGE" "$LOADER_IMAGE" "$MINIO_IMAGE" "$MINIO_MC_IMAGE" "$CLICKHOUSE_IMAGE"; do
  if ! docker image inspect "$image" >/dev/null 2>&1; then
    echo "Missing required local image: $image" >&2
    echo "Run: make bootstrap && make build" >&2
    exit 1
  fi
done

known_containers=(spv0-minio spv0-clickhouse spv0-spark-master spv0-spark-history)
known_running=false
for container in "${known_containers[@]}"; do
  if docker inspect -f '{{.State.Running}}' "$container" >/dev/null 2>&1; then
    if [[ "$(docker inspect -f '{{.State.Running}}' "$container")" == "true" ]]; then
      known_running=true
      break
    fi
  fi
done

if [[ "$known_running" == "false" ]]; then
  for port in "$MINIO_API_PORT" "$MINIO_CONSOLE_PORT" "$SPARK_MASTER_UI_PORT" "$SPARK_HISTORY_UI_PORT" "$CLICKHOUSE_HTTP_PORT" "$CLICKHOUSE_NATIVE_PORT"; do
    if port_in_use "$port"; then
      echo "Port $port is already in use" >&2
      exit 1
    fi
  done
fi

echo "Validation passed"
