# Apex — Geradores, Watcher & Oráculo (v3)

Slice vertical do diagnóstico de performance Spark: um **contrato** (`scenario.yaml`) dirige
dois geradores desacoplados; o **Watcher** detecta o anti-pattern; o **Oráculo** valida que o
sintético é fiel ao Spark real. Provado de ponta a ponta no plat-v0 (Spark 4.1.2).

## Estrutura

```
apex/apexlib.py            # lib compartilhada: leitura resiliente, schema, plano-final, distribuicao
generators/code_generator.py  # contrato -> job.py (sentinela + manifesto, sem linha hardcoded)
generators/plan_generator.py  # contrato -> event log sintetico fiel ao Spark
watchers/skew_watcher.py      # detecta skew no stage de reduce do join
oracle/compare.py             # compara sintetico vs real, reporta colapso honestamente
tests/test_slice.py           # 13 testes (spread, colapso, zstd, plano-AQE, oraculo)
scenarios/skew_on_join_30x.yaml
.github/workflows/scenario-gate.yml  # roda testes + slice a cada PR
```

## Como rodar

```bash
pip install -r requirements.txt
bash run_slice.sh          # gera, detecta, valida acceptance -> 🟢
pytest tests/ -v           # 13 testes
```

Contra um log real (do MinIO/plat-v0, comprimido em zstd — a lib descomprime sozinha):

```bash
python3 watchers/skew_watcher.py scenarios/skew_on_join_30x.yaml real_log.zstd
python3 oracle/compare.py scenarios/skew_on_join_30x.yaml synthetic_log.ndjson real_log.zstd
```

## O que mudou da v2 para a v3 (band-aids → causa raiz)

| v2 (band-aid) | v3 (causa raiz) |
|---|---|
| `cold = [...] or [1]` para evitar /0 | `hottest_reduce_stage` isola o stage do join; `skew_metrics` trata 1 task como **colapso** explícito |
| `if False:` desligando a comparação de ratio | o oráculo **detecta e avisa** quando um lado colapsou (AQE/1-core), em vez de fingir |
| tolerância de records 0→25% sem explicação | tolerância documentada; o volume da task quente vem do `expected_signal` do contrato |
| `sed` na linha a cada mudança de config | sentinela `# APEX::ANTIPATTERN` → linha é **output derivado** no manifesto |
| `zstd -d` + download manual no browser | `read_events` auto-descomprime zstd e tolera linhas corrompidas |
| ler `physicalPlanDescription` inicial | `join_operator` lê o **plano final pós-AQE** quando existe |
| nenhum teste | 13 testes cobrindo spread, colapso, zstd, plano-AQE, falso-positivo, oráculo |

## Limite honesto

No plat-v0 de 1 core, o SortMergeJoin colapsa em 1 task de reduce (o AQE/particionamento
concentra tudo). O Watcher e o Oráculo tratam isso explicitamente e **pedem um run multi-core**
para validar a cauda completa da distribuição. O sinal de skew é detectado de qualquer forma
(operador + concentração), mas o ratio numérico só é comparável com spread real.
