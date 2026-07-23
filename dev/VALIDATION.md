# Validação da Raia DEV - Spark 4.1.2

## Escopo

Este PR entrega o ambiente reproduzível de desenvolvimento: imagem Spark,
Delta/S3A, MinIO, History Server, jobs de patologia e o gate canônico de quatro
cenários. O adaptador JSONL legado foi removido; a telemetria oficial segue o
plugin Scala da raia JAR.

## Configuração local

```bash
cd dev
make env-spark41
make build
make up
```

`make env-spark41` combina `.env.example` com `.env.spark41.example` sem
sobrescrever um `.env` já existente.

## Gates executados nesta branch

```powershell
python -m pytest tests/test_canonical_e2e_assert.py -q
docker compose --env-file .env.example --env-file .env.spark41.example config --quiet
```

Resultado em 2026-07-23:

- `7 passed in 0.20s` para as asserções dos quatro cenários;
- Compose Spark 4.1.2 validado sem avisos quando baseline e overlay são usados
  juntos.

## Evidência de referência e limite

A execução anterior com Spark 4.1.2, Delta/S3A, worker real, eventos OTLP e
transições AQE está resumida em
`docs/convergence/C5-SPARK-4.1.2-VALIDATION-2026-07-22.md` na branch de
convergência. O gate completo com Collector e ClickHouse será repetido no PR7,
depois que JAR, COLLECT e INFRA estiverem integrados.

## Rollback

Reverter este PR remove somente o ambiente e os jobs DEV. O contrato v0.2 e as
outras raias não são alterados.
