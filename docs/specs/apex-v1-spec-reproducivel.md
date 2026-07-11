# Apex V1 — Spec Reproduzível

> **Propósito:** documento AUTOCONTIDO para entregar a qualquer LLM/equipe e pedir:
> *"recrie (ou compare-se com) este sistema"*. É o insumo da rodada 2 do campeonato
> (framework `docs/architecture/llm-solution-validation-framework-2026-07-09.md`):
> mesma spec para todas as soluções, aceitação pelos mesmos gates.
> **Versão:** 1.0 · 2026-07-10 · derivada do estado validado da branch cowork (`c0a5469`)

---

## 1. Missão

Diagnóstico agêntico de performance Spark: detectar anti-patterns em jobs,
explicar a causa raiz com evidência quantitativa e **aplicar o fix no código do
engenheiro via MCP no IDE** — com custo de LLM próximo de zero no caminho comum.

Diferencial vs DataFlint (benchmark de mercado): o DataFlint alerta (~14 detectores,
UI madura) e a ação é do humano; o Apex fecha o loop — detectar → diagnosticar →
aplicar → provar. On-premise, extensível, sem vendor lock-in.

## 2. Premissas do Commander (invioláveis)

| # | Premissa |
|---|---|
| L1 | Pipeline: Spark Envy (Docker gera jobs) → SparkListener → ClickHouse → Crew.ai → MCP |
| L2 | `docker compose up` sobe tudo sem configuração manual |
| L3 | Listener via `spark.extraListeners`, fail-safe (exception não mata o job) |
| L4 | ClickHouse com schema definido, query por `app_id`/`job_id` |
| L5 | Diagnóstico agêntico (Crew.ai) explica o problema |
| L6 | Fix entregue via MCP no IDE + "aplica nossa sugestão" edita o código do cliente |
| L7 | Decisões de arquitetura registradas em ADR |
| L8 | Não focar Databricks/serverless agora — Spark puro primeiro |
| L9 | Mínimo viável de CADA componente antes de expandir qualquer um |

## 3. Arquitetura de referência (composição validada — ADR-006)

```
Spark job ──event log──► Ingest ──► ClickHouse (schema apex.*, contrato v1)
                                        │
                              EvidenceValidator (7 regras)
                                        │  invalid → BLOQUEIA diagnóstico
                                        ▼
                              T1 determinístico (<1s, sem LLM)
                                 skew · spill/shuffle · gc · oom · parallelism
                                        │  confidence < 0.6
                                        ▼
                              T2 Crew.ai (2 agentes, anti-alucinação Pydantic)
                                        │  confidence < 0.6 → T4 Judge
                                        ▼
                              apex.findings ──► MCP server (stdio) ──► IDE
                                 tools: get_findings · get_stage_metrics ·
                                        list_slow_apps · trigger_diagnosis ·
                                        apply_fix (backup + diff revisável)
```

## 4. Contratos (copiar fielmente — são a interoperabilidade)

### 4.1 Identidade (`apex.telemetry.v1`)
`job_id` := `app_id` se existir → senão `spark-job-<Job ID>` → senão `local-job`.
Toda linha de toda tabela carrega `job_id` e `app_id`.

### 4.2 Schema ClickHouse
DDL canônico em `docs/specs/apex_telemetry_v1.sql`. Regras não-negociáveis:
dedup por chave natural `(app_id, stage_id, stage_attempt_id, task_id, task_attempt)`
com ReplacingMergeTree + consultas FINAL; task falhada fora dos agregados de
sucesso; planos inicial E adaptativos (AQE) armazenados; **`shuffle_records` por
task é obrigatório** (ver lição 6.2).

### 4.3 Cenários (`scenario.yaml`)
Contrato que desacopla geradores: `code_generator` (emite job PySpark com o
anti-pattern na linha marcada `# APEX::ANTIPATTERN`) e `plan_generator` (emite
event log sintético com provenance hash sha256 do contrato) leem o MESMO yaml sem
se chamarem. `acceptance` define o critério binário do gate. Classes v1:
`data_skew_on_join_key`, `gc_pressure`, `shuffle_spill`, `oom_task_failure`,
`cartesian_product`, `none` (baseline negativo — obrigatório).

### 4.4 Thresholds (versionados, nunca hardcoded)
```yaml
skew:     {ratio_min: 10, min_tasks: 4}          # max/mediana, records OU duração
shuffle:  {warning: 256MiB, critical: 1GiB, guard_min: 16MiB}
gc:       {warning_ratio: 0.10, critical_ratio: 0.20, min_stage_duration_ms: 5000}
plans:    {info_replan_count: 3}                  # + CartesianProduct/BNLJ = critical/warning
parallelism: {min_tasks: 4, min_input_bytes: 1GiB}
oom:      qualquer OOM/executor perdido = critical
```
Confiança T1: critical=0.9, high=0.8, warning=0.7; <0.6 escala p/ LLM/Judge.

## 5. Critérios de aceitação — os gates (binários)

| Gate | Verde quando | Referência do resultado real |
|---|---|---|
| G0 | build + testes num ambiente limpo | 52 testes |
| G1 | baseline `none`: ZERO finding ≥ warning em job saudável | ratio 1.0x limpo |
| G2 | cada detector pega seu cenário sintético | 5/5 verdes |
| G3 | sintético ≈ real no cluster (tolerância 40% ratio) + ≥8 tasks reais | 27.9x vs 29.4x |
| G4 | T1 < 1s sem LLM; LLM só confidence < 0.6 | skew real em 333ms, 0 tokens |
| G5 | ciclo no IDE: finding → apply_fix (backup+diff) → job re-executado limpo | shuffle 1.16MB→0, 0 findings |
| G6 | oráculo agendado comparando sintético vs real (drift) | pendente de infra |

**Regra de ouro: claim sem gate verde não conta.** Validação só com evidência
executada (testes rodados, runs reais), nunca por autoavaliação.

## 6. Lições pagas (não repetir — custaram dias)

1. **NTFS/Windows bind mount quebra ClickHouse**: todo insert MergeTree falha com
   "rename: Permission denied". Use named volume.
2. **Skew de registros ≠ skew de duração**: 29.4x em records = 1.01x em duração
   num dataset pequeno. Detectar por `shuffle_records` por task, não só duração.
3. **Ratio de skew**: hot = rows×hot_share; NUNCA derivar cold de subtração ingênua
   (bug histórico do 15392x). Baseline negativo pega essa classe de erro.
4. **AQE**: o padrão perigoso pode existir só no plano adaptativo — armazenar e
   varrer planos inicial E updates, associados por `executionId`.
5. **Windows cp1252**: subprocessos que imprimem unicode precisam de
   `PYTHONUTF8=1`/`PYTHONIOENCODING=utf-8`.
6. **LLM sem sinal alucina menos do que se pensa, mas custa**: com contrato
   Pydantic + validator, o LLM reportou honestamente "sem dados" — mas gastou
   ~2.8k tokens para isso. T1 primeiro sempre.
7. **apply_fix precisa de diff revisável**: o fix gerado teve 2 bugs pegos na
   revisão (import fora de ordem; coluna duplicada). Backup + diff não é opcional.

## 7. Fora do escopo V1 (registrado, não fazer agora)

JAR Scala do listener real-time (bridge por polling de event log vale — ADR-005) ·
UI de DAGs/replay · camada agêntica profunda (memória/RAG/multi-agent) ·
Databricks/serverless · on-premise LLM.

## 8. Como submeter uma solução à comparação

1. Implementar a partir DESTA spec (sem olhar as branches existentes, se o
   objetivo é comparação justa).
2. Rodar os gates G0–G5 e anexar os outputs (não prints editados — logs crus).
3. Preencher o scorecard do framework (C1–C6) com evidência por célula.
4. Abrir branch + Captain's Report no padrão CREW A ("done local ≠ done").
