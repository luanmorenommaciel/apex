# Railway wrapper: OTel collector with infra's config baked in (was a bind mount in compose).
# CLICKHOUSE_ENDPOINT / CLICKHOUSE_USER / CLICKHOUSE_PASSWORD / REDACTION_SECRET_KEY come from Railway vars.
FROM otel/opentelemetry-collector-contrib:0.156.0
COPY infra/otel-collector-config.yaml /etc/otelcol-contrib/config.yaml
CMD ["--config", "/etc/otelcol-contrib/config.yaml"]
