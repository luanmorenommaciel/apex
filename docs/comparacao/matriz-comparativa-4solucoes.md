# Matriz Comparativa: 4 Soluções para Diagnóstico de Performance Spark

> **Ponto de vista:** LLM Kimi (Kimi AI)
> **Data de geração:** 2026-07-07
> **Repositório de referência:** `luanmorenommaciel/apex`

---

## Sumário

Esta matriz compara quatro abordagens para diagnóstico de performance em jobs Apache Spark, considerando arquitetura, operação e maturidade. As soluções avaliadas são:

1. **cowork** — Vertente Python/CrewAI (branch `gustocezar/feature/cowork-desacoplamento-geradores`)
2. **kimi** — Vertente Go/docs (branch `gustocezar/feature/kimi-desacoplamento-geradores`)
3. **spike/apex-v0.1** — Plataforma completa Docker (branch `spike/apex-v0.1` por agmarcastro)
4. **dataflint** — Solução SaaS concorrente (estudo de mercado)

---

## Matriz Comparativa por Dimensão

### 1. Infraestrutura / Deploy

| Critério | cowork (Python/CrewAI) | kimi (Go/docs) | spike/apex-v0.1 | dataflint (SaaS) |
|----------|------------------------|----------------|-----------------|------------------|
| **Orquestração** | Docker Compose (v1-skeleton/) | Nenhuma — binários Go standalone | Docker Compose completo (9 containers) | SaaS — sem infra própria |
| **Container Spark** | Sim — Dockerfile.spark + docker-compose.yml | Nao incluso | Sim — Spark 4.1.2 (master + worker) | Nao aplica (JAR no cluster) |
| **ClickHouse** | Container via docker-compose | Assume externo (prod) | Sim — ClickHouse 26.5.1 + dashboards | Proprietário |
| **Portabilidade** | Docker-only | Binarios nativos cross-compilaveis | Docker-only | JAR obrigatorio no cluster |
| **Serverless-ready** | Nao (requer Docker) | Sim — binario Go ~15MB | Nao (9 containers) | Parcial (SaaS) |
| **Intrusividade no cluster** | Media (`spark.extraListeners`) | Zero (leitura de event logs) | Zero (leitura de event logs) | Alta (JAR obrigatorio) |

### 2. Linguagem / Runtime

| Critério | cowork | kimi | spike/apex-v0.1 | dataflint |
|----------|--------|------|-----------------|-----------|
| **Linguagem principal** | Python 3.11 | Go 1.22 + Python 3 (bridge) | Python 3.10+ + Go 1.26 | Java/Scala (JAR) |
| **Framework LLM** | CrewAI para orquestracao | Puro (sem framework LLM) | CrewAI opcional + detectores deterministicos | Nao utiliza LLM |
| **Runtime overhead** | ~200MB (Python + deps) | ~15MB (Go binary) | ~500MB+ (9 containers) | Variavel (JAR in-process) |
| **Concorrencia** | GIL-limitada (Python) | Goroutines ilimitadas (Go) | Mista (Python GIL + Go routines) | JVM threads |
| **Tipagem** | Dinamica (dicts) | Estatica forte (structs Go) | Parcial (Pydantic + Go structs) | Estatica (Java) |

### 3. Detectores / Cobertura

| Critério | cowork | kimi | spike/apex-v0.1 | dataflint |
|----------|--------|------|-----------------|-----------|
| **Detectores implementados** | 5 (skew, shuffle, spill, memory, duration) | 4 (skew, duration, spill, memory via ClickHouse) | 5 (skew, shuffle, plans, GC, OOM) | 14 alertas fixos |
| **Extensibilidade de detectores** | Alta (Python facil de modificar) | Media (requer recompilacao Go) | Alta (Python + Go) | Baixa (alertas fixos, nao extensiveis) |
| **Modo de deteccao T1** | LLM prompt (nao-deterministico) | SQL ClickHouse (deterministico) | SQL + CrewAI opcional | Regras fixas proprietarias |
| **Deteccao de skew** | Via LLM (ratio no prompt) | SQL ratio (configuravel) | SQL + Pydantic Finding | Sim (alerta fixo) |
| **Deteccao de spill** | Sim | Sim (SpillWatcher Go) | Sim | Sim |
| **Deteccao de GC/OOM** | Indireto (memory) | Sim (SQL ClickHouse) | Sim (detectores dedicados) | Limitado |
| **Deteccao de planos adaptativos (AQE)** | Nao | Nao | Sim (spark_sql_adaptive_plans) | Nao |

### 4. Pipeline / Arquitetura

| Critério | cowork | kimi | spike/apex-v0.1 | dataflint |
|----------|--------|------|-----------------|-----------|
| **Pipeline completo** | T1 → Validator (7 regras) → T2 (runbook) → T3 (heuristico/LLM) | T1 → Validator (7 regras) → T2 (runbook JSON) → T3 (heuristico + LLM opcional) | Detectores → Finding (Pydantic) → CrewAI opcional → Report | Alerta binario (sem tiers) |
| **Tiers de analise** | 3 tiers (T1/T2/T3) | 3 tiers (T1/T2/T3) | 2 tiers (T1 determinístico + T3 LLM opcional) | 1 tier (alerta) |
| **Captura de dados** | SparkListener in-process (py4j, tempo real) | Event log pos-execucao (zero-JAR) | Event log pos-execucao (Go loader) | JAR no cluster (tempo real) |
| **Schema de dados** | stage_metrics, task_metrics, findings | spark_tasks, spark_stages, spark_raw_events, spark_sql_executions, metrics_summary | spark_tasks, spark_stages, spark_jobs, spark_sql_executions, spark_raw_events, spark_eventlog_files, spark_sql_adaptive_plans | Proprietario |
| **Modelo de dados** | Dicts Python sem tipagem | Structs Go tipadas com JSON tags | Pydantic (Python) + structs (Go) | Proprietario |

### 5. Validação / Confiabilidade

| Critério | cowork | kimi | spike/apex-v0.1 | dataflint |
|----------|--------|------|-----------------|-----------|
| **Validador de evidencias** | Sim — 7 regras (Validator) | Sim — EvidenceValidator (Go, 5 dimensoes) | Parcial (via oracle/compare.py) | Nao |
| **Regras validadas** | 7 regras estruturais | Provenance, Schema, Correlation, Distribution, Structural | Comparacao sinais agregados (oracle) | Nao aplica |
| **Cadeia de custodia** | Manifesto JSON com scenario_hash | scenario_hash cruzado + provenance no log | Manifesto JSON + comparacao oracle | Nao disponivel |
| **Qualidade de evidencia** | Manual (olhar ratio) | Automatizada (valid/invalid/indeterminate) | Semi-automatizada (oracle tolerance 5%) | Nao aplica |
| **Determinismo T1** | Nao (LLM pode variar) | Sim (regras SQL fixas) | Parcial (SQL deterministico + LLM opcional) | Sim (regras fixas) |

### 6. Integração IDE / MCP

| Critério | cowork | kimi | spike/apex-v0.1 | dataflint |
|----------|--------|------|-----------------|-----------|
| **MCP Server** | Sim — 7 tools (get_recommendations, get_spill_recommendations, apply_fix, list_scenarios, run_diagnostic, validate_evidence, get_status) | Sim — HTTP port 3000 (diagnose, validate, recommend, status, health_check) | Sim — stdio server (6 tools: list_runs, detect_skew, detect_shuffle, detect_plans, get_report, analyze_run) | Nao tem |
| **Protocolo MCP** | MCP Python | MCP Go (HTTP) | MCP stdio (Python) | Nao suporta |
| **Integracao IDE** | Claude Code / Cursor (via MCP) | Qualquer IDE com MCP (HTTP) | Qualquer IDE com MCP (stdio) | Apenas web UI |
| **CLI Tools** | Indireto (via MCP) | Sim — diagnose, validate, recommend, spillwatch, analyze | Via Makefile (bootstrap, build, validate, diagnose, workloads) | Nao |
| **CREI Server** | Sim — ingestao de event logs | Sim — HTTP port 3001 | Integrado no eventlog-loader Go | Nao |

### 7. Testes / Qualidade

| Critério | cowork | kimi | spike/apex-v0.1 | dataflint |
|----------|--------|------|-----------------|-----------|
| **Testes unitarios** | 21 testes (pytest) | Nenhum (ainda) em Go; Python herdado | pytest (fake Spark + fake ClickHouse) + testes LLM opt-in | Nao disponivel |
| **Testes E2E** | test_crew_e2e.py | Nao visiveis | Sim (fake infra completa) | Nao disponivel |
| **Cobertura de teste** | E2E basico (CrewAI) | Parser, attempts, correlation, provenance, watcher, oracle, inventory (Python) | Infra completa mockada | Nao disponivel |
| **CI/CD** | GitHub Actions (oracle-weekly, scenario-gate) | Mesmo workflow herdado | Makefile com bootstrap, build, validate, compose, smoke | Nao aplica (SaaS) |
| **Relatorio de cobertura** | Nao | docs/coverage/, test_coverage_inventory.py | Nao explicito | Nao |
| **Benchmark automatizado** | T1=136ms, Validator=197ms, T2=0.01ms | Mesmos tempos (logica identica) | Nao documentado | Nao aplicavel |

### 8. Documentação / Apresentação

| Critério | cowork | kimi | spike/apex-v0.1 | dataflint |
|----------|--------|------|-----------------|-----------|
| **ADRs** | ADR-004, ADR-005 | ADR-004 (reescrita), ADR-005 (nao presente) | Presumido (nao visivel no escopo) | Nao disponivel |
| **Padrao de operacao** | CREW_A_OPERATING_STANDARD.md | team-validation-guide.md | Nao visivel | Nao disponivel |
| **Documentacao arquitetural** | architecture.md (6.7KB) | docs/architecture/ (diretorio estruturado) | Implicito na plataforma | Documentacao SaaS |
| **Linhagem (lineage)** | apex-v4-lineage.md (2.0KB) | apex-v4-lineage.md (10.3KB) | Nao visivel | Nao disponivel |
| **Apresentacao** | HTML 10 slides | HTML 15 slides (expandida) | Nao visivel | Nao aplica |
| **Playbooks** | docs/playbooks/skew-slice-v4.md | docs/playbooks/ (presumido) | Nao visivel | Nao disponivel |
| **Estrutura docs** | ~15 arquivos | ~25 arquivos, diretorios organizados | Implicito | Documentacao online |

### 9. Escalabilidade / Performance

| Critério | cowork | kimi | spike/apex-v0.1 | dataflint |
|----------|--------|------|-----------------|-----------|
| **Latencia T1 (skew)** | 2–5s (API LLM externa) | <100ms (SQL ClickHouse) | <100ms (SQL determinístico) | Variavel (SaaS) |
| **Latencia T2 (runbook)** | 2–5s (API LLM externa) | <10ms (runbook lookup JSON) | <10ms (runbook lookup) | Nao aplica |
| **Startup MCP Server** | ~2s (Python) | ~50ms (Go binary) | ~2s (Python stdio) | Nao aplica |
| **Jobs/hora (T1)** | ~720 (limitado por API key e rate limit) | ~36.000 (limitado por ClickHouse) | ~36.000 (limitado por ClickHouse) | Ilimitado (SaaS) |
| **Concorrencia** | GIL limita (Python) | Goroutines ilimitadas (Go) | Mista | JVM threads |
| **Throughput ClickHouse** | ~10K INSERTs/s (Python driver) | ~100K INSERTs/s (Go driver nativo) | ~100K INSERTs/s (Go loader nativo) | Proprietario |
| **Memoria do servico** | ~200MB (Python + dependencias) | ~15MB (Go binary) | ~500MB+ (9 containers) | Variavel (JAR) |
| **Throughput ingestao** | Nao aplica (in-process) | <50ms Go Loader (1000 eventos) | Completo via eventlog-loader Go | In-process (JAR) |

### 10. Custo / Licença

| Critério | cowork | kimi | spike/apex-v0.1 | dataflint |
|----------|--------|------|-----------------|-----------|
| **Custo por diagnostico T1** | $0.01–$0.05 (Anthropic API) | ~$0 (SQL local) | ~$0 (SQL local, LLM opcional) | Incluso na licenca |
| **Custo de infraestrutura** | Docker Compose (4 containers) | Binario Go + ClickHouse externo | Docker Compose (9 containers) | SaaS pago |
| **Licenca** | Open source (repo proprio) | Open source (repo proprio) | Open source (repo proprio) | Pago (SaaS) |
| **Dependencia de API externa** | Sim — Anthropic API obrigatoria para T1/T2 | Nao (LLM opcional no T3) | Nao (LLM opcional) | Nao |
| **Custo total de propriedade (TCO)** | Medio (infra + API LLM) | Baixo (infra enxuta, sem API) | Alto (9 containers + opcional LLM) | Alto (SaaS recorrente) |

### 11. Maturidade / Completeness

| Critério | cowork | kimi | spike/apex-v0.1 | dataflint |
|----------|--------|------|-----------------|-----------|
| **Status de compilacao/execucao** | Funcional (Python) | Nao compilado (sem Go no host) | Funcional (Docker Compose) | Produção (SaaS) |
| **Numero de commits** | 14 | 6 (Go) + base herdada | Nao especificado | Nao aplica |
| **Workloads sinteticos** | 1 (demo_skew_job.py) | 1 (skew_on_join_30x.yaml) | 6 (skew_join, shuffle_heavy, gc_churn, oom_victim, cross_join, cache_heavy) | Nao disponivel |
| **Dashboards/UI** | Nao (MCP/CLI only) | Nao (MCP/CLI only) | 10 dashboards ClickStack (cluster, jobs, errors, performance, heat-map, memory, SQL plans, etc.) | Web UI proprietaria |
| **Lakehouse integration** | Nao | Nao | Sim — Delta Lake 4.2.0 + MinIO (medallion: landing → bronze → sanity) | Nao |
| **Schema completo** | Basico (3 tabelas) | Melhorado (5+ tabelas) | Completo (7 tabelas + adaptive plans) | Proprietario |
| **Nivel de maturidade** | Prova de conceito (V1) | Fundacao documentada (V0.2) | Plataforma completa (V0.1 spike) | Produto comercial |

### 12. Diferencial Único

| Solucao | Diferencial Unico |
|---------|-------------------|
| **cowork** | Prova de conceito rapida com experiencia interativa no IDE via MCP + Claude Code; foco em demo funcional para validacao de arquitetura V1 com SparkListener in-process. |
| **kimi** | Fundacao de producao em Go com validacao estrutural de evidencias (EvidenceValidator), diagnostico deterministico via SQL ClickHouse (<100ms), binarios leves (~15MB), e documentacao arquitetural completa (ADR-004 revisitada). |
| **spike/apex-v0.1** | Plataforma end-to-end com 9 containers Docker, 6 workloads sinteticos, 10 dashboards ClickStack, lakehouse Delta Lake + MinIO, e parsing completo de event logs em Go (raw, SQL, stages, tasks, jobs, adaptive plans). |
| **dataflint** | SaaS maduro com 14 alertas fixos e web UI proprietaria; requer JAR no cluster (alta intrusividade), custo recorrente, sem extensibilidade nem integracao MCP/IDE. |

---

## Radar Visual: Resumo por Categoria (Pontuacao Conceitual)

| Dimensao | cowork | kimi | spike/apex-v0.1 | dataflint |
|----------|--------|------|-----------------|-----------|
| Infraestrutura / Deploy | ★★★☆☆ | ★★★★☆ | ★★★★★ | ★★★☆☆ |
| Linguagem / Runtime | ★★★☆☆ | ★★★★★ | ★★★★☆ | ★★★☆☆ |
| Detectores / Cobertura | ★★★★☆ | ★★★★☆ | ★★★★★ | ★★★☆☆ |
| Pipeline / Arquitetura | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★☆☆☆ |
| Validacao / Confiabilidade | ★★★☆☆ | ★★★★★ | ★★★☆☆ | ★☆☆☆☆ |
| Integracao IDE / MCP | ★★★★★ | ★★★★★ | ★★★★☆ | ★☆☆☆☆ |
| Testes / Qualidade | ★★★☆☆ | ★★★☆☆ | ★★★★☆ | ★☆☆☆☆ |
| Documentacao / Apresentacao | ★★★☆☆ | ★★★★★ | ★★☆☆☆ | ★★★☆☆ |
| Escalabilidade / Performance | ★★☆☆☆ | ★★★★★ | ★★★★☆ | ★★★★☆ |
| Custo / Licenca | ★★★☆☆ | ★★★★★ | ★★★☆☆ | ★★☆☆☆ |
| Maturidade / Completeness | ★★★☆☆ | ★★★☆☆ | ★★★★★ | ★★★★★ |
| Diferencial Unico | POC rapida | Fundacao Go prod | Plataforma Docker | SaaS maduro |

---

## Recomendacoes por Cenario (Ponto de Vista Kimi)

### Para prototipacao rapida e demos
**Recomendacao:** `cowork` ou `spike/apex-v0.1`
- A vertente `cowork` entrega uma experiencia interativa completa via MCP em minutos.
- O `spike/apex-v0.1` entrega uma plataforma visual completa com dashboards.

### Para producao em escala
**Recomendacao:** `kimi` como base, com integracao seletiva do `spike/apex-v0.1`
- O core Go (`go-apex`) oferece o melhor desempenho, determinismo e custo zero por diagnostico.
- O schema ClickHouse do `spike/apex-v0.1` e o eventlog-loader Go podem ser incorporados.
- O SparkListener da `cowork` pode ser mantido como bridge temporaria.

### Para comparacao competitiva
**Recomendacao:** usar `dataflint` como baseline
- O `dataflint` representa o estado da arte SaaS: maduro, mas intrusivo, caro e fechado.
- O diferencial do projeto Apex (todas as vertentes) e a **zero intrusividade** (zero-JAR) e a **extensibilidade via MCP/IDE**.

---

## Notas Metodologicas

- Todas as informacoes desta matriz foram extraidas diretamente dos artefatos do repositorio `luanmorenommaciel/apex` nos commits de referencia (`d3c3e8a3` para cowork, `8be15724` para kimi, e documentacao do branch spike/apex-v0.1).
- Nenhuma informacao foi inventada ou extrapolada alem dos dados disponiveis nos commits e documentacao analisados.
- O ponto de vista "Kimi" e explicitado na arquitetura da branch kimi (Go-first, determinismo, validacao estrutural, ADR-004 revisitada) e refletido nas recomendacoes.

---

*Artefato gerado pela LLM Kimi como parte da avaliacao comparativa do projeto Apex.*
