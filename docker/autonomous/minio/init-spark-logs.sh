#!/bin/sh
set -eu

ALIAS_NAME="apex"
MINIO_ENDPOINT="http://minio:9000"
LOG_BUCKET="${MINIO_LOG_BUCKET:-spark-logs}"

mc alias set "${ALIAS_NAME}" "${MINIO_ENDPOINT}" "${MINIO_ROOT_USER}" "${MINIO_ROOT_PASSWORD}"
mc mb --ignore-existing "${ALIAS_NAME}/${LOG_BUCKET}"

# S3 has no real folders. This marker makes the events prefix explicit and
# visible to humans/tools before Spark writes its first event log.
printf '' | mc pipe "${ALIAS_NAME}/${LOG_BUCKET}/events/.keep"

mc ls "${ALIAS_NAME}/${LOG_BUCKET}"
