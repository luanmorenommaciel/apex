# Apex v4 Corrigido - Linhagem das Melhorias

> **Fonte canônica:** `gustocezar/feature/desacoplamento-geradores`  
> Documento completo na branch: `docs/apex-v4-lineage.md`

Data: 2026-06-08  
Fork de evidência: https://github.com/gustocezar/dataship-spark-plat-v0  
Projeto destino: https://github.com/luanmorenommaciel/apex

## Resumo das correções v4

| Componente | O que corrigiu |
|---|---|
| `apex/apexlib.py` | `iter_events` streaming; zstd sem materializar; rolling logs; executionId; compute_scenario_hash |
| `generators/plan_generator.py` | Distribuição de `hot_records = rows * hot_share` — ratio 15392x → 27.9x |
| `generators/code_generator.py` | scenario_hash no manifesto; sentinela derivada, não hardcoded |
| `watchers/skew_watcher.py` | Valida provenance; passa `join_op`; root_cause com `customer_id = 7 (SortMergeJoin)` |
| `oracle/compare.py` | Comparação real: join op, task quente, ratio; audit trail com scenario_hash |
| `scenarios/skew_on_join_30x.yaml` | version 4; remove `hot_partition.single_task_shuffle_read_records`; tolerance correta |
| `tests/test_slice.py` | Streaming, rolling, executionId, ratio realista, hash, stale, provenance |

## Evidência (Ubuntu/WSL)

```text
s.................... [100%]
synthetic ratio: 27.9x
real ratio:      29.5x
watcher:         GATE VERDE
oracle:          sintetico fiel ao Spark real dentro da tolerancia
```

## Relação com issues do Apex

| Issue | Evidência |
|---|---|
| #9 — Data Generator | Contrato declarativo + validação contra log real |
| #16 — Spark History Parser | Parser com zstd, rolling logs, stage metrics, join operator |
| #17 — Watcher | Watcher deterministico com finding, root cause, evidence |
| #19 — plat-v0 Bootstrap | dataship-spark-plat-v0 como ambiente reproduzível |
| #21 — CI Integration | scenario-gate.yml para testes e slice no PR |
| #23 — Shadow Repo Governance | Fork como repo de evidência reproduzível |
| #25 — Commander Attention | Dado concreto para decisão de governança |
