# DataFlint × Apex — Capability Matrix

> Gerado em: 2026-07-01  
> Fonte DataFlint: OSS v0.9.9 (Apache-2.0), SaaS (pago), GitBook docs validado 2026-06-22  
> Fonte Apex: v4 (branch `gustocezar/feature/desacoplamento-geradores`)

---

## Como ler este documento

| Símbolo | Significado |
|---------|-------------|
| ✅ | Apex já faz isso |
| 🔶 | Apex pode fazer com trabalho incremental (scenario.yaml novo) |
| 🔴 | Gap real — requer arquitetura nova ou escolha estratégica |
| ⭐ | Apex supera DataFlint nessa dimensão |
| 🚫 | Fora de escopo (decisão consciente) |

---

## Parte 1 — Tudo o que o DataFlint pode fazer

### A. 14 Alertas de Performance (OSS — entregues)

| # | Alerta DataFlint | O que detecta | Fonte do dado |
|---|-----------------|----------------|---------------|
| 1 | Reading Small Files | Leituras escandeam muitos arquivos tiny → overhead de IO | Stage input metrics |
| 2 | Writing Small Files | Sink emite muitos outputs tiny | Stage output metrics |
| 3 | Iceberg – inefficient replace | Overwrite Iceberg reescreve muito mais data do que precisa | Iceberg write metrics |
| 4 | Partition Skew | Uma partition/task ≫ as demais → stage stall | Task duration + shuffle read |
| 5 | Large Number Of Small Tasks | Tasks demais e minúsculas → scheduler overhead | Task count |
| 6 | Memory Over-Provisioning | Executors hold muito mais memória do que usam → desperdício | Executor memory used vs allocated |
| 7 | Memory Under-Provisioning | Memória insuficiente → spill/GC/OOM risk | SpillMetrics + GC time |
| 8 | High Wasted Cores Rate | Cores alocados ociosos relativamente ao trabalho feito | CPU time vs wall time |
| 9 | Large Data Broadcast | Broadcast table é grande → pressão de memória no driver/executor | Broadcast size |
| 10 | Broadcast small table in SMJ | Tabela pequena foi para SMJ em vez de ser broadcast | Plan type + table size |
| 11 | Large Cross Join Scan | Cross join escaneia input grande → blow-up | Cross join + scan size |
| 12 | Large Partition Size | Partições individuais oversized → spill/skew risk | Partition bytes |
| 13 | Long Filter Conditions | Predicado de filter é longo/truncado no plano | SQL plan string length |
| 14 | Query Failures | Query falhou; extrai JVM stack trace e aponta o nó no plano lógico | SparkListenerTaskEnd + exception |

### B. 5 Alertas no Roadmap (NÃO entregues ainda)

| # | Alerta Roadmap | O que detectará |
|---|----------------|-----------------|
| 15 | High task error rate | Taxa de erros de tasks acima do threshold |
| 16 | High executors error rate | Executors falhando com frequência |
| 17 | High disk spill | Spill em disco alto relativo ao tamanho do input |
| 18 | Repartition before write (low cardinality) | repartition() antes do write com baixa cardinalidade → arquivos gigantes ou tiny |
| 19 | Executor memory overhead too low | Container OOM antes do executor OOM |

### C. UI e Visualização

| Funcionalidade | Escopo | Descrição |
|----------------|--------|-----------|
| Performance heat map por query | Live + History | Visualização de custo por nó do plano físico |
| Application run summary | Live + History | Resumo de duração, tasks, stages por app |
| Real-time query e cluster status | Live (:4040) | View ao vivo durante execução |
| SQL node duration breakdown | Live + History (opt-in) | Duração de cada nó físico (Filter, Join, Aggregate...) |
| Alert dashboard | Live + History | Lista de alertas disparados com severidade |
| Spark AI Assistant | UI button | Chat-based (sem detalhes públicos de implementação OSS) |

### D. Instrumentação Opcional (Experimental — opt-in via config)

| Config | O que habilita |
|--------|---------------|
| `spark.dataflint.instrumentation.sql=true` | Mede duração de cada nó do plano físico |
| `spark.dataflint.instrumentation.udfs=true` | Mede duração de UDFs, pandas_udf, mapInPandas |
| `spark.dataflint.instrumentation.windows=true` | Mede duração de window functions |
| Delta Lake integration (auto) | Detecta Z-Order, liquid clustering |
| Iceberg auto-catalog (auto) | Rastreia write metrics para Iceberg tables |

### E. Compatibilidade de Plataforma

AWS EMR, Google Dataproc, Kubernetes (Spark on K8s), Standalone, Local/dev, Databricks, Spark History Server (offline/post-mortem).

Ativação: dois configs + JAR via `spark.jars.packages`.

### F. Características Operacionais

- **Diagnose-only**: nunca altera query plans
- **Fail-safe**: exception → logged, job continua normalmente
- **Zero new ports**: usa :4040 existente
- **Clean removal**: delete 2 configs, reboot driver
- **Telemetry opt-out**: `spark.dataflint.telemetry.enabled=false`

### G. SaaS Product (pago — não OSS)

| Agente | O que faz |
|--------|-----------|
| Agentic Spark Copilot | Chat-based — responde perguntas sobre o job em linguagem natural |
| Cluster Agent | Fleet-level — monitora múltiplos clusters |
| Review Agent | Revisa código/config antes de rodar |
| Fleet Observability | Multi-job, multi-cluster, histórico agregado |

---

## Parte 2 — Como o Apex é diferente (por capacidade)

### Diferença fundamental de arquitetura

```
DataFlint:  Job → [JAR+Plugin in-process] → Event Stream → 14 Fixed Alerts → Human decides
Apex:       Event Log → [Zero JAR] → Watcher → Classifier → Coordinator → Judge → Diagnosis
```

O DataFlint é um **detector estático** com regras fixas. O Apex é um **pipeline de raciocínio** com tiers de confiança.

### Por capacidade

#### Alertas de Performance (A1–A14)

| Alerta DataFlint | Apex hoje | Diferença Apex |
|-----------------|-----------|----------------|
| Partition Skew (A4) | ✅ SkewWatcher v4 — AQE-aware, stage-isolated, root_cause com hot key | ⭐ Apex identifica `customer_id=7` causou 30x skew no join da linha 38. DataFlint só diz "Partition Skew detected." |
| Reading Small Files (A1) | 🔶 Dados disponíveis em `SparkListenerTaskMetrics.inputMetrics` | Apex pode adicionar cenário `small_files_read.yaml` sem mudar arquitetura |
| Writing Small Files (A2) | 🔶 Dados em `outputMetrics` | Idem — scenario.yaml novo |
| Memory Over-Provisioning (A6) | 🔶 `SparkListenerExecutorAdded` + task memory used | Apex pode calcular wasted ratio sem JAR |
| Memory Under-Provisioning (A7) | 🔶 SpillMetrics no event log | Dados existem no log — scenario novo |
| High Wasted Cores (A8) | 🔶 CPU time vs wall time em `TaskMetrics` | Dados existem — scenario novo |
| Large Data Broadcast (A9) | 🔶 Plano físico tem `BroadcastExchangeExec` com tamanho | AQE-aware + plan_generator para synthetic |
| Broadcast small table in SMJ (A10) | 🔶 Detectável via plan comparison: SMJ quando tabela < threshold broadcast | Scenario compara tamanho da tabela vs plano escolhido |
| Large Cross Join Scan (A11) | 🔶 `CrossJoin` no plano + scan metrics | Scenario novo |
| Large Partition Size (A12) | 🔶 Partition bytes em stage metrics | Scenario novo |
| Large Number Of Small Tasks (A5) | 🔶 Task count por stage | Scenario novo |
| Long Filter Conditions (A13) | 🔶 Parse do SQL plan string | Simples — string length check no plan |
| Query Failures (A14) | 🔶 `SparkListenerTaskEnd.taskInfo.failed=true` + reason | ⭐ Apex pode fazer LLM reasoning sobre a falha, não só extrair stack trace |
| Iceberg inefficient replace (A3) | 🔴 Requer Iceberg write metrics — não estão no event log padrão | Gap real — precisaria de integração com Iceberg catalog |

**Resumo**: 13 dos 14 alertas são detectáveis sem JAR a partir do event log. Apenas o Iceberg específico é um gap real.

#### UI e Visualização

| DataFlint | Apex | Análise |
|-----------|------|---------|
| Performance heat map (visual) | 🔴 Sem UI própria hoje | Gap intencional — Apex é API/CLI primeiro |
| Live monitoring (:4040) | 🔴 Post-hoc only | Gap arquitetural — evento log é escrito quando stage termina |
| Alert dashboard | 🔴 Sem UI | Gap intencional |
| Spark AI Assistant (chat) | ✅ Tier 3 Coordinator (Sonnet) | ⭐ Apex tem pipeline estruturado com confiança graduada; DataFlint SaaS tem chat. |

#### Instrumentação

| DataFlint (opt-in) | Apex | Análise |
|---------------------|------|---------|
| SQL node duration (requires JAR) | ✅ Lê plan do event log (sem medir duração por nó) | DataFlint mede runtime de cada nó. Apex lê o plano final pós-AQE mas não cronometra por nó. |
| UDF/Pandas duration (requires JAR) | 🔴 Sem acesso a duração interna de UDFs | Gap real — UDF timing não está no event log |
| Delta Lake / Iceberg (requires JAR) | 🔴 Parcial | Gap real — metadados de tabela não estão no Spark event log |

#### SaaS Features

| DataFlint SaaS | Apex equivalente |
|----------------|-----------------|
| Agentic Spark Copilot (chat) | ⭐ Tier 3 Coordinator (Sonnet) — proativo, não reativo |
| Cluster Agent (fleet) | 🔶 MinIO lista múltiplos app-ids → análise de frota possível |
| Review Agent (pre-run) | 🔶 code_generator + callSite correlation (em desenvolvimento) |
| Fleet Observability | 🔶 Iterable sobre event logs no MinIO |

---

## Parte 3 — Onde podemos melhorar e superar

### 3.1 Cobertura de cenários (maior alavancagem imediata)

**DataFlint tem 14 alertas. Apex tem 1 (skew).**

Prioridade sugerida com base em impacto vs esforço para novos `scenario.yaml`:

| Prioridade | Cenário | Por que | Esforço |
|-----------|---------|---------|---------|
| P0 | `memory_under_provisioning` | SpillMetrics estão no log — dados prontos | Baixo |
| P0 | `small_files_read` | inputMetrics disponível | Baixo |
| P1 | `broadcast_too_large` | Plan extração já existe em apexlib | Médio |
| P1 | `smj_vs_broadcast_missed` | Plan comparison — tabela pequena no SMJ | Médio |
| P2 | `high_wasted_cores` | CPU vs wall time em TaskMetrics | Médio |
| P2 | `memory_over_provisioning` | executor memory used vs allocated | Médio |
| P3 | `cross_join_large_scan` | Plan + scan size | Alto |
| P3 | `query_failure_lm_analysis` | TaskEnd.failed + LLM reasoning | Alto |

**Roadmap DataFlint que Apex pode entregar primeiro** (são todos detectáveis sem JAR):
- High disk spill (SpillMetrics no log)
- Repartition before write (plan + partition count)
- Executor memory overhead too low (SparkListenerExecutorAdded + container size)

### 3.2 Raciocínio vs Detecção (superação estratégica)

**DataFlint: alerta binário → humano decide**  
**Apex: pipeline com confiança graduada + LLM reasoning**

O que o Apex pode entregar que o DataFlint nunca vai entregar:

```
DataFlint output:
  "Partition Skew detected."

Apex output (Tier 2+3):
  Finding: SKEW_ON_JOIN_KEY
  Root cause: customer_id=7 concentra 31.4x tasks no BroadcastHashJoin
  Hot key: 7 (ratio: 31.4x, threshold: 10x)
  Recomendação: salting com prefixo de 8 buckets no customer_id
  Confiança: 0.87 (Tier 3 Coordinator)
  Evidência: stage 4 → task durations: [0.3s, 0.3s, 0.3s, ..., 9.4s]
  Código correlacionado: job.py:38 (via callSite)
```

### 3.3 Oracle Validation (único no mercado)

**DataFlint não tem nada equivalente ao oracle.py.**

O oracle valida que o log sintético que geramos para CI é fiel ao real. Isso significa:

- Apex tem rastreabilidade: cada diagnóstico está atrelado a um hash de cenário validado
- DataFlint pode ter falsos positivos sem forma de auditar
- **Proposta de valor único**: "Diagnóstico com cadeia de custódia verificável"

### 3.4 Correlação com Código (gap transformador)

**Nem DataFlint nem qualquer ferramenta OSS faz isso hoje.**

```
callSite.short: "job.py:38"  → no SparkListenerJobStart (zero JAR)
+ git log --follow -L 38,38:job.py  → qual commit introduziu aquela linha
= Apex aponta: "Este anti-pattern foi introduzido no commit abc123 por Augusto em 15 Jun"
```

Isso transforma o Apex de "ferramenta de observabilidade" em "ferramenta de accountability".

DataFlint SaaS Review Agent revisa código pré-run — mas sem correlação histórica.

### 3.5 Extensibilidade por Cenário (vantagem estrutural)

DataFlint: para adicionar um novo alert, precisa de PR no repositório DataFlint, JAR novo, deploy.

Apex: para adicionar um novo anti-pattern:
1. Escrever `scenarios/novo_cenario.yaml` (contrato)
2. `code_generator` gera o job PySpark com o anti-pattern
3. `plan_generator` gera o log sintético para CI
4. `oracle.py` valida contra run real
5. `skew_watcher.py` (ou novo watcher) detecta

**Apex pode ter N cenários customizados por cliente. DataFlint tem 14 fixos.**

### 3.6 Fleet Analysis sem JAR (oportunidade incremental)

DataFlint SaaS Cluster Agent requer infraestrutura paga.

Apex pode iterar sobre `s3://spark-logs/events/` no MinIO e processar múltiplos app-ids em paralelo. Hoje o Apex roda por app-id. Uma extensão de frota seria:

```python
def analyze_fleet(minio_prefix, scenario_path, last_n=50):
    for log_path in list_recent_logs(minio_prefix, n=last_n):
        yield run_watcher(scenario_path, log_path)
```

Isso entrega fleet observability sem JAR e sem SaaS.

### 3.7 Real-time (o único gap que importa)

DataFlint monitora ao vivo via `:4040` enquanto o job roda.  
Apex lê o event log depois que o job termina.

**Isso é uma decisão arquitetural, não um bug.** O Apex nasceu não-intrusivo.

Opção para o futuro:
- **Polling de rolling logs**: event logs podem ser sufixados numericamente (`event.log.1`, `.2`...) e escritos incrementalmente. Apex pode seguir esses arquivos enquanto o job roda.
- **MinIO Event Notifications**: MinIO emite S3 notifications quando um objeto é atualizado. Apex poderia escutar e processar incrementalmente.
- **Escolha estratégica recomendada**: focar em post-mortem profundo + code correlation, onde DataFlint é fraco, em vez de competir em real-time UI onde o custo de implementação é alto.

---

## Sumário Executivo

| Dimensão | DataFlint OSS | DataFlint SaaS | Apex hoje (v4) | Apex potencial |
|----------|--------------|----------------|----------------|----------------|
| Intrusividade | JAR obrigatório | JAR obrigatório | Zero JAR | Zero JAR |
| Alertas cobertos | 14 fixos | 14 fixos | 1 (skew) | 14+ extensíveis |
| Raciocínio sobre causa | ❌ alerta binário | ✅ chat (LLM) | ⭐ 4 tiers + confiança | ⭐ 4 tiers |
| Correlação com código | ❌ | ❌ | 🔶 callSite → git (em dev) | ⭐ único no mercado |
| Validação oracle | ❌ | ❌ | ⭐ oracle.py + chain of custody | ⭐ único no mercado |
| Extensibilidade | ❌ fixo | ❌ fixo | ⭐ scenario.yaml | ⭐ N cenários |
| Fleet analysis | ❌ OSS | ✅ pago | 🔶 incremental | ✅ via MinIO |
| Real-time | ✅ :4040 live | ✅ :4040 live | ❌ post-hoc | 🔶 rolling log polling |
| UI visual | ✅ heat map | ✅ dashboard | ❌ CLI/API | 🚫 decisão consciente |
| Histórico de código | ❌ | ❌ | 🔶 git sidecar | ⭐ accountability layer |
| Custo operacional | Free (JAR) | Pago (SaaS) | Free (MinIO) | Free |

### Os 3 lugares onde Apex supera sem precisar mudar arquitetura

1. **Raciocínio profundo** — root cause com nome da coluna, ratio, hot key, recomendação específica. DataFlint para em "Partition Skew detected."
2. **Oracle + chain of custody** — único sistema que valida que o diagnóstico está calibrado contra dados reais.
3. **Extensibilidade** — qualquer time pode adicionar um cenário customizado sem tocar no DataFlint.

### Os 3 lugares onde temos trabalho para superar

1. **Cobertura de cenários** — de 1 para 14+. Cada scenario.yaml novo é 1–2 dias de trabalho.
2. **Code correlation** — callSite está no event log, falta o git sidecar. ADR-005 pendente.
3. **Fleet observability** — iterar sobre MinIO para análise de frota. Trabalho de uma sprint.

---

*Referências: `docs/competitive/dataflint/alerts-catalog.md`, `plugin-architecture.md`, `what-is-dataflint.md`, `dataflint-specialist.md`*
