# TODO(hardening): digest-pin CLICKHOUSE_BASE_IMAGE (FROM clickhouse@sha256:...)
# once a Docker daemon/registry is available to resolve the current digest.
ARG CLICKHOUSE_BASE_IMAGE=clickhouse:26.5.1-jammy
FROM ${CLICKHOUSE_BASE_IMAGE}

LABEL org.opencontainers.image.title="apex-v01-clickhouse"
LABEL org.opencontainers.image.description="Project-local ClickHouse image wrapper for Spark Platform v0."
