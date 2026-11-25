# Railway wrapper: ClickHouse with the repo DDL baked in (Railway has no bind mounts).
# initdb scripts run only on an EMPTY data volume; later migrations need a separate apply.
FROM clickhouse/clickhouse-server:24.8
COPY infra/sql/ /docker-entrypoint-initdb.d/
