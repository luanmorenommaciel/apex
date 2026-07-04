# Apex — Arquitetura

**Versão:** 0.3.0 · **Status:** Tier 1 implementado, Tiers 2–4 planejados

---

## Visão geral

O Apex diagnostica performance de jobs Spark de forma **não-intrusiva**:

```
Event Log (MinIO)
      │
      ▼
┌─────────────────────────────────────────────────────┐
│  Tier 1 · Watchers  (determinístico, zero LLM)      │
│  skew_watcher.py → Finding estruturado              │
└─────────────┬───────────────────────────────────────┘
              │  Finding {watcher, severity, confidence, evidence, root_cause}
              ▼
┌─────────────────────────────────────────────────────┐
│  Tier 2 · Classifier  (LLM leve)                   │
│  Classifica o Finding e decide se escala            │
└─────────────┬───────────────────────────────────────┘
              │  confidence < threshold → escala
              ▼
┌─────────────────────────────────────────────────────┐
│  Tier 3 · Coordinator  (Sonnet)                    │
│  Orquestra múltiplos Watchers + contexto completo   │
└─────────────┬───────────────────────────────────────┘
              │  confidence < 0.6 → escala
              ▼
┌─────────────────────────────────────────────────────┐
│  Tier 4 · Judge  (Opus)                            │
│  Segunda opinião em casos de baixa confiança        │
└─────────────────────────────────────────────────────┘
```

**Princípio:** zero JAR no cluster, zero SparkSession modificado. Tudo via event logs.

---

## Fluxo completo (Tier 1)

```
scenario.yaml  ──────────────────────────────────────┐
      │                                               │
      ▼                                               ▼
code_generator.py                         plan_generator.py
      │                                               │
      ▼                                               ▼
  job.py                              event-log.ndjson (sintético)
  (PySpark)                                           │
      │                                               │
      │  (opcional: rodar no plat-v0)                 │
      ▼                                               │
event-log real ──────── oracle/compare.py ────────────┘
      │                  (valida fidelidade)
      │
      ▼
skew_watcher.py
      │
      ├── apexlib.read_events()       → carrega e descomprime
      ├── apexlib.join_operator()     → plano final pós-AQE
      ├── apexlib.hottest_reduce_stage() → stage de reduce do join
      └── apexlib.skew_metrics()     → hot/median/ratio/collapsed
      │
      ▼
Finding { severity, confidence, evidence, root_cause, recommendations }
      │
      ▼
check_acceptance(finding, scenario)
      │
   GATE VERDE / GATE VERMELHO
```

---

## scenario.yaml — o contrato

Desacopla code_generator e plan_generator (ADR-004). Ambos leem o mesmo contrato de forma independente.

```yaml
scenario_id: skew_on_join_30x
version: 3
status: prototype          # prototype | validated

anti_pattern:
  class: data_skew_on_join_key
  severity: high

code_generator:
  language: pyspark
  emits: job.py
  data:
    orders:    { rows: 200000, distinct_keys: 100, hot_key: 7, hot_share: 0.80 }
    customers: { rows: 100, distinct_keys: 100 }
  spark_config:
    spark.sql.adaptive.enabled: "false"

plan_generator:
  emits: event-log.ndjson
  strategy: synthesize
  expected_signals:
    join_operator: SortMergeJoin
    hot_stage: 4
    skew_ratio_min: 10

oracle:
  enabled: true
  cadence: weekly
  tolerance: { skew_ratio: 0.30, records: 0.25 }
  on_divergence: fail_and_open_issue

acceptance:
  root_cause_includes: ["data skew", "customer_id", "SortMergeJoin"]
  min_recommendations: 1
```

---

## apexlib.py — funções principais

| Função | O que faz | Corrige |
|---|---|---|
| `read_events(path)` | Lê NDJSON. Auto-detecta e descomprime zstd. Tolera linhas corrompidas. | Resiliência |
| `validate_schema(events)` | Avisa se estrutura não é Spark esperado | Resiliência |
| `join_operator(events)` | Retorna operador do plano **final** pós-AQE | Plano errado em v2 |
| `hottest_reduce_stage(events)` | Isola stage de reduce (shuffle > 0) | Mistura scan+reduce em v2 |
| `skew_metrics(records)` | hot / median_cold / ratio / collapsed | Divisão por zero em v2 |

---

## Plataforma de execução (plat-v0)

```
docker compose (dataship-spark-plat-v0)
├── Spark Master + Worker (4.1.2)    ← submete jobs
├── MinIO                            ← event logs em spark-logs/events/
│                                       formato: <app-id> (zstd comprimido)
└── ClickHouse                       ← métricas de execução
```

O Apex lê os logs do MinIO via REST. O plat-v0 é ambiente de execução — o código do Apex vive neste repo.

---

## Próxima fase — Tiers 2–4

**Tier 2 (Classifier):**
- Input: Finding do Watcher
- Output: classificação + decisão de escalar
- LLM candidatos: DeepSeek, Kimi, Gemini (ver `docs/llm-evals/`)

**Tier 3 (Coordinator — Sonnet):**
- Input: múltiplos Findings de múltiplos Watchers
- Output: diagnóstico consolidado com root cause + plano de ação

**Tier 4 (Judge — Opus):**
- Acionado quando confidence < 0.6
- Segunda opinião independente

---

## ADRs

- [ADR-001](adr/ADR-001-go-otel.md) — Go como linguagem para OTel Collector
- [ADR-002](adr/ADR-002-shadow-repo.md) — Governança do shadow repo plat-v0
- [ADR-003](adr/ADR-003-deprioritization.md) — Estratégia de deprioritização intencional
- [ADR-004](adr/ADR-004-scenario-contract.md) — Desacoplamento generators via scenario.yaml
