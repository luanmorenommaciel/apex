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

## Evidência canônica integrada

Em 2026-07-24, com Spark 4.1.2, Delta/S3A, plugin Scala, Collector e
ClickHouse reais, os quatro cenários canônicos passaram: skew (`47.07x`), spill
(`104076355` bytes), bad shuffle (estágio de duas tasks com shuffle grande) e
OOM (16 estágios pré-falha persistidos). O gate entre as seis raias também
passou para `app-20260724014653-0000`: 17 eventos/fingerprints, 3 findings
determinísticos e MCP read-only.

Consulte [`../docs/e2e/CANONICAL_GATE.md`](../docs/e2e/CANONICAL_GATE.md) para
os `job_id`s, comandos de reprodução e limites da evidência.

## Rollback

Reverter este PR remove somente o ambiente e os jobs DEV. O contrato v0.2 e as
outras raias não são alterados.
