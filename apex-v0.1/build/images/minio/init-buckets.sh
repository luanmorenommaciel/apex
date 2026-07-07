#!/usr/bin/env sh
set -eu

: "${MINIO_ROOT_USER:?MINIO_ROOT_USER is required}"
: "${MINIO_ROOT_PASSWORD:?MINIO_ROOT_PASSWORD is required}"
: "${MINIO_LAKEHOUSE_BUCKET:?MINIO_LAKEHOUSE_BUCKET is required}"
: "${MINIO_LOG_BUCKET:?MINIO_LOG_BUCKET is required}"

for attempt in $(seq 1 60); do
  if mc alias set local http://minio:9000 "${MINIO_ROOT_USER}" "${MINIO_ROOT_PASSWORD}" >/dev/null 2>&1; then
    break
  fi
  if [ "${attempt}" = "60" ]; then
    echo "MinIO did not become ready after 60 seconds" >&2
    exit 1
  fi
  sleep 1
done

mc mb --ignore-existing "local/${MINIO_LAKEHOUSE_BUCKET}"
mc mb --ignore-existing "local/${MINIO_LOG_BUCKET}"

for layer in landing bronze silver gold; do
  printf '' | mc pipe "local/${MINIO_LAKEHOUSE_BUCKET}/${layer}/.keep"
  printf '' | mc pipe "local/${MINIO_LAKEHOUSE_BUCKET}/${layer}/customer/.keep"
done
printf '' | mc pipe "local/${MINIO_LOG_BUCKET}/events/.keep"
mc ls local
