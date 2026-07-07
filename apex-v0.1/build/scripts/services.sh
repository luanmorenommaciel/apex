#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"
if [[ ! -f .env ]]; then
  echo "Missing .env. Run: make bootstrap"
  exit 1
fi
set -a
source .env.example
source .env
set +a

cat <<INFO
Spark Platform v0 services

MinIO Console
  URL:      http://127.0.0.1:${MINIO_CONSOLE_PORT}
  User:     ${MINIO_ROOT_USER}
  Password: ${MINIO_ROOT_PASSWORD}
  Data:     bucket ${MINIO_LAKEHOUSE_BUCKET}, paths landing/customer/, bronze/customer/, silver/customer/, gold/customer/
  Logs:     bucket ${MINIO_LOG_BUCKET}, path events/

Spark History
  URL: http://127.0.0.1:${SPARK_HISTORY_UI_PORT}
  Use the completed app list to inspect SQL executions, stages, and tasks.

Spark Master
  URL: http://127.0.0.1:${SPARK_MASTER_UI_PORT}

ClickHouse
  HTTP URL:  http://127.0.0.1:${CLICKHOUSE_HTTP_PORT}
  Native:    127.0.0.1:${CLICKHOUSE_NATIVE_PORT}
  Database:  ${CLICKHOUSE_DB}
  User:      ${CLICKHOUSE_USER}
  Password:  ${CLICKHOUSE_PASSWORD}
  Browser test:
    http://127.0.0.1:${CLICKHOUSE_HTTP_PORT}/?user=${CLICKHOUSE_USER}&password=${CLICKHOUSE_PASSWORD}&database=${CLICKHOUSE_DB}&query=SELECT%201

ClickStack (HyperDX)
  URL:      http://127.0.0.1:${HYPERDX_UI_PORT}
  User:     ${HYPERDX_SEED_EMAIL}
  Password: ${HYPERDX_SEED_PASSWORD}
  Seeded by make compose: connection "Spark ClickHouse", sources (Spark Diagnostic
  Reports, Spark Raw Events, Spark Tasks) and the "Spark Diagnostics" dashboard.
  Details: docs/logs-info/clickstack-dashboards.md

Local project images
  Spark runtime: ${SPARK_RUNTIME_IMAGE}
  Spark history: ${SPARK_HISTORY_IMAGE}
  MinIO: ${MINIO_IMAGE}
  MinIO client: ${MINIO_MC_IMAGE}
  ClickHouse: ${CLICKHOUSE_IMAGE}
  Event log loader: ${LOADER_IMAGE}
  HyperDX: ${HYPERDX_IMAGE}
  MongoDB (HyperDX state): ${MONGO_IMAGE}

Useful commands
  make ingest-landing  Persist sample customer JSON into the landing layer.
  make bronze          Run the customer landing-to-bronze Delta job.
  make sanity          Check landing and bronze customer data.
  make smoke           Run ingest-landing, bronze, sanity, and smoke validation.
  make spark-logs      Load Spark event logs from MinIO into ClickHouse.
  make down            Stop the stack without deleting local data.
INFO
