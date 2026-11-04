# Railway wrapper: OTel collector with infra's config baked in (was a bind mount in compose).
# CLICKHOUSE_ENDPOINT / CLICKHOUSE_USER / CLICKHOUSE_PASSWORD / REDACTION_SECRET_KEY come from Railway vars.
# infra's config hardcodes the compose alias apex-infra-clickhouse; Railway has no such host, so the
# exporter endpoint is rewritten to ${env:CLICKHOUSE_ENDPOINT} (clickhouse.railway.internal, set by deploy.sh).
# The collector image is distroless (no shell), so the rewrite runs in a small build stage.
FROM alpine:3.20 AS cfg
COPY infra/otel-collector-config.yaml /cfg/config.yaml
RUN set -eu; \
    sed -i -E 's#^([[:space:]]*endpoint:[[:space:]]*)tcp://apex-infra-clickhouse:[^[:space:]]*#\1${env:CLICKHOUSE_ENDPOINT}#' /cfg/config.yaml; \
    grep -q 'endpoint: ${env:CLICKHOUSE_ENDPOINT}' /cfg/config.yaml; \
    ! grep -nE '^[^#]*(apex-infra-|apex-otel-collector|minio|host\.docker\.internal)' /cfg/config.yaml

FROM otel/opentelemetry-collector-contrib:0.156.0
COPY --from=cfg /cfg/config.yaml /etc/otelcol-contrib/config.yaml
CMD ["--config", "/etc/otelcol-contrib/config.yaml"]
