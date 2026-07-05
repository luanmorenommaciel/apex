# Apex — Contexto para Claude Code

> Diagnóstico agêntico de performance Spark & Databricks.
> Detecta o que code reviews perdem. Corrige o que produção revela.

---

## O que é o Apex?

Sistema de diagnóstico agêntico de performance Spark — detecta anti-patterns, gera root cause e recomendações entregues via MCP ao IDE do engenheiro.

**Duas arquiteturas em paralelo:**

### Mundo A — Zero-JAR (v3, estável)
- Zero JAR injetado no cluster
- Zero modificação de SparkSession
- Leitura de event logs via MinIO REST (pós-job)
- Tiers: Watcher → Classifier → Coordinator → Judge

### Mundo B — V1 SparkListener (em construção, ADR-005)
- SparkListener in-process via `spark.extraListeners`
- Captura métricas em tempo real → ClickHouse
- Diagnóstico via Crew.ai → entregue via MCP
- Fluxo: `Spark Envy → SparkListener → ClickHouse → Crew.ai → MCP`

> **Decisão arquitetural (ADR-005):** V1 segue Mundo B (SparkListener).  
> Mundo A permanece válido para ambientes sem acesso ao Spark config.  
> Ver `docs/adr/ADR-005-sparklistener-vs-zero-jar.md`.

**Tiers originais (Mundo A):**
```
Tier 1 · Watchers      → determinístico, sem LLM — detecta anti-patterns
Tier 2 · Classifier    → LLM classifica o Finding emitido pelo Watcher
Tier 3 · Coordinator   → Sonnet orquestra o diagnóstico completo
Tier 4 · Judge         → Opus quando confiança < 0.6
```

Tier 1 implementado (v3). V1 (Mundo B) em construção.

---

## Estado atual

**Versão:** v3 (Mundo A) + v1-skeleton (Mundo B em construção)  
**Commit baseline:** `bc747c1` (apex-workspace, branch cowork)  
**Status:** prototype — Mundo A verde (40 testes). Mundo B: SparkListener + ClickHouse + MCP skeleton prontos, Crew.ai pendente.  
**Testes:** 40 passando (plat-v0)

### O que funciona
- `apexlib.py` — parse centralizado de event logs
- Stage-aware skew — isola reduce stage (shuffle > 0)
- AQE-aware — lê plano FINAL pós-`SparkListenerSQLAdaptiveExecutionUpdate`
- Auto-zstd — detecta magic bytes `\x28\xb5\x2f\xfd`
- Sentinela de linha — guard de CI valida `anti_pattern_line` do contrato

### O que ainda não foi validado
- Distribuição real de 8 tasks (worker 2+ cores nunca rodou)
- Ratio real do oráculo em multi-core
- Cenário único — loop multi-cenário nunca divergiu

---

## Estrutura do repositório

```
apex/
├── .claude/                    # Claude Code integration
│   ├── agents/apex/            # Apex diagnostic agent
│   └── commands/               # /review, /status, /sync-context
├── .github/workflows/
│   ├── scenario-gate.yml       # gate por PR — gera fixture, roda watcher
│   └── oracle-weekly.yml       # oráculo semanal (P2-12)
├── apex/
│   └── apexlib.py              # lib compartilhada (read_events, join_operator, etc.)
├── docs/
│   ├── architecture.md         # 4 tiers + fluxo scenario.yaml
│   ├── adr/                    # ADR-001 a ADR-004
│   └── llm-evals/              # comparações de LLMs para Tier 2/3/4
├── generators/
│   ├── code_generator.py       # scenario.yaml → job PySpark
│   └── plan_generator.py       # scenario.yaml → event log sintético
├── oracle/
│   └── compare.py              # valida sintético vs real
├── scenarios/
│   └── skew_on_join_30x.yaml   # contrato do cenário (scenario_id, acceptance, etc.)
├── tasks/
│   └── backlog.md              # 10 pontos de falha + próximos passos
├── tests/
│   └── test_slice.py           # 13 testes unitários
├── watchers/
│   └── skew_watcher.py         # Skew Watcher v3
├── CHANGELOG.md                # v1 → v2 → v3 + próximas versões
├── CLAUDE.md                   # este arquivo
├── CONTRIBUTING.md             # como contribuir
├── requirements.txt
└── README.md
```

---

## Conceito central: scenario.yaml

O contrato que desacopla os geradores (ADR-004):

```yaml
scenario_id: skew_on_join_30x
version: 3
status: prototype   # prototype | validated

code_generator:     # → job.py (PySpark com o anti-pattern)
plan_generator:     # → event-log.ndjson (log sintético)
oracle:             # valida sintético vs real periodicamente
acceptance:         # critérios que o Watcher deve satisfazer
```

`code_generator` e `plan_generator` leem o mesmo contrato independentemente — nenhum chama o outro.

---

## Como rodar localmente

### Pré-requisitos
```bash
pip install -r requirements.txt
# plat-v0 rodando (docker compose up) para testes com Spark real
```

### Testes unitários
```bash
pytest tests/ -v
```

### Gate de cenário manual
```bash
python generators/code_generator.py scenarios/skew_on_join_30x.yaml job.py
python generators/plan_generator.py scenarios/skew_on_join_30x.yaml log.ndjson
python watchers/skew_watcher.py scenarios/skew_on_join_30x.yaml log.ndjson
```

### Com log real (plat-v0)
```bash
# 1. Subir o plat-v0 (ver repo dataship-spark-plat-v0)
# 2. Submeter o job gerado ao cluster
# 3. Capturar o event log do MinIO: spark-logs/events/<app-id>
# 4. python watchers/skew_watcher.py scenarios/skew_on_join_30x.yaml <log-path>
```

---

## Padrão de trabalho (CREW_A_OPERATING_STANDARD)

**"Done local ≠ Done"** — trabalho só conta quando visível nas issues.

- Cada commit → comentário de progresso na issue correspondente
- Cada sync → Captain's Report (4 blocos: Avançou / Bloqueado / Precisa do Commander / Honestidade)
- Cada decisão de arquitetura → ADR como issue `[ADR-NNN]`
- Cada blocker → issue `type:blocker` no mesmo dia

**Issues ativas:**
- `#17` — Watcher/Classifier/Judger Pipeline
- `#18` — OTel Collector Stage 02 (Go)
- `#19` — plat-v0 Bootstrap
- `#20` — Recommendation Engine
- `#21` — CI Integration

---

## Plataforma de execução (plat-v0)

O plat-v0 (`dataship-spark-plat-v0`) é o ambiente de execução — docker compose com:
- Spark 4.1.2
- MinIO (event logs em `spark-logs/events/`, zstd comprimido)
- ClickHouse (métricas)

O código do Apex vive **neste repo**. O plat-v0 é só onde roda.

---

## LLM Evals (Tiers 2–4)

Testes comparativos de LLMs para o pipeline de diagnóstico:
- Resultados em `docs/llm-evals/`
- Modelos testados: Claude, Gemini, DeepSeek, Kimi, ChatGPT, Codex
- Critérios: precisão do diagnóstico, latência, custo por chamada, raciocínio sobre event logs

---

## Versão

- **Versão:** 0.3.0 (v3 Mundo A) / 0.1.0-skeleton (V1 Mundo B)
- **Status:** prototype
- **Última atualização:** 04 jul 2026
- **Crew:** A · Captain: Augusto · Commander: Luan
