# Validação da Raia INFRA - ClickStack Canônico

## Escopo

Este PR adiciona a tabela OTLP `apex.otel_logs` ao ClickStack canônico. Ela é
necessária para a compatibilidade com o pipeline COLLECT, que declara exportação
de traces e logs, mesmo quando o plugin Spark atual emite apenas spans.

## Contrato

- ClickHouse permanece o store canônico para telemetria e findings;
- `otel_traces` e `otel_logs` são schemas de aterrissagem do exporter;
- materialized views transformam spans em `spark_events` e
  `plan_transitions`;
- todos os dados continuam correlacionados por `job_id`.

## Gates executados nesta branch

```powershell
docker compose --env-file .env.example config --quiet

$schema = Get-Content -Raw sql\012_otel_logs.sql
$statement = "CREATE DATABASE apex;`n$schema"
docker run --rm clickhouse/clickhouse-server:24.8 `
  clickhouse-local --multiquery --query $statement
```

Resultado em 2026-07-23: Compose renderizado sem erro e DDL aceito pelo
ClickHouse em execução descartável.

## Limite e rollback

O smoke completo de ingestão COLLECT → INFRA será repetido no PR7. Reverter
este PR remove somente a tabela exporter-owned `apex.otel_logs`; não altera as
tabelas contratuais nem os dados de negócio.
