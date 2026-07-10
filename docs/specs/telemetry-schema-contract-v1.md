# Contrato de Telemetria e Schema — Apex V1

> **Versão:** `apex.telemetry.v1` · **Data:** 2026-07-09 · **Status:** proposta para revisão do Commander
>
> Unifica as 3 implementações que hoje escrevem schemas diferentes no ClickHouse:
> o loader Go do spike (`spark_tasks`...), o ingest Python do cowork (`apex.*`) e o
> fork do Gabriel usado pelo kimi. **Uma tabela canônica, três produtores.**

---

## 1. Por que existe

Cada branch inventou seu schema e os detectores ficaram acoplados à fonte errada:
o detector do spike lê `spark_tasks`, o do cowork lê event log, o do kimi lê o fork.
O merge (framework §6) exige que **detectores leiam um contrato, não uma implementação**.

Origem das peças:
- **Envelope `job_id`** → codex (`apex/commander/telemetry.py`, `apex.commander.telemetry.v1`)
- **Colunas de task + dedup por chave natural** → spike (`spark_tasks`, lição do `.compact`)
- **Namespace `apex.*` + findings** → cowork (`v1-skeleton/schema/init.sql`)

## 2. O envelope (identidade)

| Campo | Regra |
|---|---|
| `schema_version` | literal `apex.telemetry.v1` |
| `job_id` | **chave da experiência do Luan** ("debuga esse job ID"). Resolução: `app_id` se existir → senão `spark-job-<Job ID>` → senão `local-job` (contrato codex) |
| `app_id` | `App ID` do `SparkListenerApplicationStart`; pode ser null em harness local |

Toda linha de toda tabela carrega `app_id`. O MCP e o Crew.ai consultam por `job_id`/`app_id`.

## 3. Tabelas canônicas (DDL: `docs/specs/apex_telemetry_v1.sql`)

| Tabela | Grão | Fonte primária | Consumidor |
|---|---|---|---|
| `apex.task_metrics` | task attempt | TaskEnd (listener ou event log) | detectores skew/gc/shuffle/oom |
| `apex.stage_metrics` | stage attempt | StageCompleted + agregação de tasks | detectores + MCP `get_stage_metrics` |
| `apex.sql_plans` | plano por execução (inicial E cada update AQE) | SQLExecutionStart + AdaptiveExecutionUpdate | detector plans (CartesianProduct etc.) |
| `apex.findings` | finding | detectores + Crew.ai | MCP `get_findings` / `apply_fix` |

## 4. Regras não-negociáveis (lições pagas)

1. **Dedup por chave natural** — `ReplacingMergeTree` ordenado por
   `(app_id, stage_id, stage_attempt_id, task_id, task_attempt)`. Lição do spike:
   ordenar por uid posicional duplica a MESMA task re-ingerida de log `.compact`
   e infla toda agregação (spill/GC fantasmas). Consultas usam `FINAL`.
2. **Task falhada não entra em agregado de sucesso** — `successful = 0` fica fora
   de somas de GC/shuffle; falhas alimentam só o detector de OOM (regra já no
   `apex/detectors.py`).
3. **Plano inicial E planos AQE são armazenados** — detector de padrão varre os
   dois; só o inicial gera falso negativo pós-AQE (lição do plans.py do spike +
   nosso P1-6).
4. **Detector lê o contrato, não a fonte** — a mesma regra roda sobre event log
   (Mundo A, `apex/detectors.py`) e sobre estas tabelas (Mundo B). Divergência
   entre os dois caminhos = bug, coberto pelo oráculo.
5. **Thresholds fora do código** — `apex/diagnostics.yaml` versionado (ISSUE-A07).

## 5. Migração por branch

| Branch | O que muda |
|---|---|
| spike | Loader Go passa a escrever em `apex.task_metrics` (rename + 2 colunas de envelope). Vira o produtor oficial (ISSUE-A02) |
| cowork | `event_log_ingest.py` adota colunas do spike que faltam (cpu, peak memory, input/output) e `ReplacingMergeTree` |
| kimi | go-apex consulta as tabelas canônicas em vez do fork do Gabriel |
| codex | `build_telemetry()` já é o envelope; harness local permanece válido como referência do contrato |

## 6. Fora do v1 (registrado)

Executor-level metrics, streaming em tempo real (depende do JAR Scala — ADR-005/Sprint 3),
retenção/TTL e RBAC — decidir com o Luan no spec (#22).
