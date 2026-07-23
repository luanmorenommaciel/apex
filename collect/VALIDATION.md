# Validação da Raia COLLECT

## Escopo

Este PR entrega o OpenTelemetry Collector configurado para receber spans OTLP,
aplicar a segunda barreira de sanitização e enviá-los ao ClickHouse. O Collector
aterrissa no schema OTLP; materialized views da raia INFRA convertem os spans em
tabelas contratuais.

## Contrato

- entrada: `apex.stage` e `apex.plan_transition` por OTLP/HTTP em `:4318`;
- dados preservados: `job_id`, métricas tipadas, fingerprint e transições AQE;
- sanitização: remove campos sensíveis e mascara conteúdo residual;
- saída: exporter ClickHouse por TCP interno, com fila persistente.

## Gates executados nesta branch

```powershell
docker compose --env-file .env.example config --quiet
docker compose -f docker-compose.yml -f docker-compose.c3-infra.yml `
  --env-file .env.example --env-file .env.c3-infra.example config --quiet
docker run --rm `
  -e 'REDACTION_SECRET_KEY=local-c3-smoke-only-not-a-production-secret-0123456789abcdef' `
  -e 'CLICKHOUSE_USER=apex' -e 'CLICKHOUSE_PASSWORD=apex_local_dev' `
  -e 'CLICKHOUSE_ENDPOINT=tcp://clickhouse:9000?compress=lz4&async_insert=1' `
  -v "${PWD}/config.yaml:/c.yaml:ro" `
  otel/opentelemetry-collector-contrib:0.156.0 validate --config /c.yaml
```

Resultado em 2026-07-23: os dois Compose renderizaram e o Collector validou a
configuração sem erro.

## Evidência de referência e limite

O tracer bullet integrado que materializou spans em ClickHouse está resumido
em `docs/convergence/C3-JAR-VALIDATION-2026-07-22.md` na branch de
convergência. A repetição cruzando COLLECT e INFRA canônicos pertence ao PR7,
após os merges das raias fundamentais.

## Rollback

Reverter o PR remove apenas o Collector e seus overlays. A raia JAR continua
fail-safe quando nenhum endpoint Collector estiver disponível.
