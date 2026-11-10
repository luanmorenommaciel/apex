# Validação da Raia DEV - Spark 4.1.2

## Escopo

Esta raia entrega o ambiente reproduzível de desenvolvimento: imagem Spark
(construída uma vez a partir de `spark-master`, com a suíte de testes da célula
do jar executada antes do `assembly`), Delta/S3A, MinIO (`bitnamilegacy`
pinado por digest, decisão D-1), History Server, os jobs de patologia e o gate
canônico. O adaptador JSONL legado foi removido; a telemetria oficial segue o
plugin Scala da raia JAR.

## Configuração local

```bash
cd dev
make env-spark41                                   # mescla .env.example + .env.spark41.example (cada chave uma vez)
printf 'minioadmin' > secrets/apex_s3_access_key   # credenciais S3 só existem aqui (secrets/README.md)
printf 'minioadmin' > secrets/apex_s3_secret_key
make build
make up
```

`make env-spark41` combina `.env.example` com `.env.spark41.example` sem
sobrescrever um `.env` já existente; chaves do overlay substituem as da base.

## Gates offline

```bash
uv run --extra dev pytest -q          # host, sem Docker
docker compose --env-file .env.example config --quiet
```

Resultado em 2026-10-19: `106 passed` cobrindo as asserções canônicas dos
cinco cenários (skew com amostra retry-safe, tail_outlier, spill, bad_shuffle,
driver_oom), `ensure_env.py`, `calibrate.py` (SQL com parâmetro vinculado),
`verify_s3_runtime_evidence.py` (versão e provider derivados do event log),
`r9d_overhead_ab.py`, os runners canônicos (.sh/.ps1 em paridade), `verify.sh`,
`soak_driver_listener.sh`, `common/paths.py` e `common/drain.py`.

## Gates vivos

```bash
VERIFY_FRESH=1 ./scripts/verify.sh                      # build → up → smoke Delta → event log → History Server
APEX_CANONICAL_CH_PASSWORD=... ./scripts/e2e_canonical.sh   # Spark → OTLP → collect → ClickHouse
make fp-crosscheck                                      # fingerprint dev == jar (jar da própria imagem)
```

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

Reverter esta raia remove somente o ambiente e os jobs DEV. O contrato
(`CONTRACT.md`, hoje **v0.6**) e as outras raias não são alterados.
