#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"
set -a
source .env.example
source .env
set +a
COMPOSE=(docker compose --env-file .env -f build/docker-compose.yml)

app_names=(
  "spark-plat-v0-sample-customer-landing"
  "spark-plat-v0-smoke-customer-bronze"
  "spark-plat-v0-sanity-customer-lakehouse"
)
apps_json="[]"
for attempt in $(seq 1 60); do
  apps_json="$(curl -fsS "http://127.0.0.1:${SPARK_HISTORY_UI_PORT}/api/v1/applications")"
  missing_apps=()
  for app_name in "${app_names[@]}"; do
    if [[ "$apps_json" != *"$app_name"* ]]; then
      missing_apps+=("$app_name")
    fi
  done
  if [[ "${#missing_apps[@]}" == "0" ]]; then
    break
  fi
  if [[ "$attempt" == "60" ]]; then
    echo "Smoke apps were not found in Spark History: ${missing_apps[*]}" >&2
    echo "$apps_json" >&2
    exit 1
  fi
  sleep 2
done

minio_ls() {
  local target="$1"
  "${COMPOSE[@]}" run --rm --no-deps --entrypoint /bin/sh minio-init -lc \
    "mc alias set local http://minio:9000 '$MINIO_ROOT_USER' '$MINIO_ROOT_PASSWORD' >/dev/null && mc ls --recursive \"$target\""
}

landing_listing="$(minio_ls "local/$MINIO_LAKEHOUSE_BUCKET/landing/customer")"
if [[ "$landing_listing" != *".json"* ]]; then
  echo "Landing JSON data was not found in MinIO lakehouse bucket" >&2
  echo "$landing_listing" >&2
  exit 1
fi

bronze_listing="$(minio_ls "local/$MINIO_LAKEHOUSE_BUCKET/bronze/customer")"
if [[ "$bronze_listing" != *"_delta_log"* || "$bronze_listing" != *".parquet"* ]]; then
  echo "Delta data was not found in MinIO lakehouse bucket" >&2
  echo "$bronze_listing" >&2
  exit 1
fi

log_listing="$(minio_ls "local/$MINIO_LOG_BUCKET/events")"
if [[ "$log_listing" != *"eventlog_v2_"* ]]; then
  echo "Spark event logs were not found in MinIO log bucket" >&2
  echo "$log_listing" >&2
  exit 1
fi

echo "Smoke validation passed"
