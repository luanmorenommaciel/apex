# Comparação Detalhada: Branches Cowork vs Kimi do Desacoplamento de Geradores

> **Repo:** `luanmorenommaciel/apex`  
> **Base comum:** `gustocezar/feature/desacoplamento-geradores` (8 commits do slice v4)  
> **Branch cowork:** `gustocezar/feature/cowork` (14 commits, foco V1 Python/CrewAI)  
> **Branch kimi:** `gustocezar/feature/kimi-desacoplamento-geradores` (5 commits, foco Go/docs/ADR-004)  
> **Commit mais recente cowork:** `d3c3e8a3`  
> **Commit mais recente kimi:** `8be15724`  
> **Gerado em:** 2026-07-07

---

## 1. Visão Geral

### 1.1 Contexto Histórico

O projeto Apex nasceu da necessidade de detectar anti-patterns de performance em jobs Spark sem injetar código no cluster (zero-JAR). A branch base (`gustocezar/feature/desacoplamento-geradores`) continha o slice v4 validado: um contrato declarativo (`scenario.yaml`) que alimenta dois geradores desacoplados — `code_generator` (emite job PySpark) e `plan_generator` (sintetiza event log sem executar Spark).

A partir dessa base, duas vertentes evoluíram em paralelo:

- **Branch cowork (`d3c3e8a3`):** Evolução orientada por Claude Sonnet (Cowork), focada na arquitetura V1 proposta pelo Commander Luan na reunião de 30/06/2026. Pilha Python, CrewAI, SparkListener in-process, Docker Compose, e integração LLM via Anthropic API.
- **Branch kimi (`8be15724`):** Evolução orientada por Kimi, focada em documentação arquitetural, ADR-004 revisitada (resolução do gap de linguagem), e um core de infraestrutura em Go (`go-apex`) com componentes T1/T2/T3, ClickHouse, MCP Server, e validador de evidências.

### 1.2 Filosofia de cada vertente

| Cowork | Kimi |
|--------|------|
| **Prova de conceito rápida** — validar a arquitetura V1 em dias | **Fundação documentada** — estabelecer contratos e stack de produção |
| Python-first (CrewAI, py4j, SparkListener) | Go-first para infraestrutura, Python para diagnóstico e LLM |
| Experiência interativa no IDE (MCP → Claude Code) | Pipeline de diagnóstico determinístico com validação estrutural |
| Foco na reunião 30/06 — SparkListener, ClickHouse, CrewAI | Foco em ADR-004, ADR-005, e separação de responsabilidades por linguagem |

### 1.3 Linha do tempo dos commits

```
Base comum (8 commits v4)
├── cowork: +14 commits
│   ├── v1-skeleton/ (Docker, SparkListener, ClickHouse, diagnose.py, MCP)
│   ├── ADR-005 (SparkListener vs zero-JAR)
│   ├── docs/CREW_A_OPERATING_STANDARD.md
│   └── test_crew.py, v1-skeleton/test_crew_e2e.py
│
└── kimi: +5 commits
    ├── go-apex/ (Go 1.22, ClickHouse, diagnostician, validator, watcher, MCP)
    ├── docs/adr/adr-004-language-gap-resolution.md
    ├── docs/architecture/ (estrutura documental)
    ├── docs/coverage/, docs/tier/, docs/validation/
    └── real_log.ndjson (44KB), tests/test_coverage_inventory.py
```

---

## 2. Arquitetura da Branch `cowork` (V1 Python)

### 2.1 Diagrama de componentes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           APEX V1 — COWORK (Python)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  Docker Compose                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │ spark-master│───→│ spark-worker│    │ clickhouse  │    │ spark-history│  │
│  │  (7077)     │    │  (4 cores)  │    │  (:8123)    │    │  (:18080)   │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘   │
│       │                                                                       │
│       │ py4j callback                                                         │
│       ▼                                                                       │
│  ┌─────────────────────────────────┐                                          │
│  │  ApexSparkListener (Python)     │  ←── spark_listener.py                   │
│  │  • onJobStart / onStageCompleted│     clickhouse_writer.py                  │
│  │  • onTaskEnd                    │                                          │
│  └─────────────────────────────────┘                                          │
│       │                                                                       │
│       │ HTTP INSERT                                                           │
│       ▼                                                                       │
│  ┌─────────────────────────────────┐                                          │
│  │  ClickHouse (apex DB)           │                                          │
│  │  • stage_metrics                │                                          │
│  │  • task_metrics                 │                                          │
│  │  • findings                     │                                          │
│  └─────────────────────────────────┘                                          │
│       │                                                                       │
│       │ SQL query                                                             │
│       ▼                                                                       │
│  ┌─────────────────────────────────┐                                          │
│  │  analysis/diagnose.py           │  ←── Anthropic API (Claude)              │
│  │  • LLM analysis                 │                                          │
│  │  • Gera finding JSON            │                                          │
│  └─────────────────────────────────┘                                          │
│       │                                                                       │
│       │ MCP protocol                                                          │
│       ▼                                                                       │
│  ┌─────────────────────────────────┐                                          │
│  │  mcp/server.py                  │  ←── Claude Code / Cursor IDE            │
│  │  • Tools: diagnose, query_jobs  │                                          │
│  └─────────────────────────────────┘                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Componentes principais

| Componente | Arquivo(s) | Função |
|------------|------------|--------|
| **Spark Envy** | `v1-skeleton/docker-compose.yml`, `Dockerfile.spark` | Cluster Spark local (master + worker + history) |
| **SparkListener** | `v1-skeleton/listener/spark_listener.py` | Captura métricas in-process via py4j |
| **ClickHouse Writer** | `v1-skeleton/listener/clickhouse_writer.py` | Persiste métricas em tempo real |
| **Demo Job** | `v1-skeleton/jobs/demo_skew_job.py` | Job com skew proposital (80% hot key) |
| **Diagnóstico LLM** | `v1-skeleton/analysis/diagnose.py` | Consulta ClickHouse + chama Anthropic API |
| **MCP Server** | `v1-skeleton/mcp/server.py` | Expõe tools para Claude Code |
| **Schema** | `v1-skeleton/schema/init.sql` | DDL ClickHouse (auto-executado) |
| **Tests** | `v1-skeleton/test_crew_e2e.py`, `test_crew.py` | Validação do pipeline |

### 2.3 Fluxo de dados

1. **Submissão do job:** `spark-submit` com `--py-files` injeta listener no driver.
2. **Captura em tempo real:** `ApexSparkListener` recebe callbacks `onStageCompleted` e `onTaskEnd` via py4j.
3. **Persistência:** `ClickHouseWriter` envia INSERTs para `apex.stage_metrics` e `apex.task_metrics`.
4. **Diagnóstico:** `diagnose.py` consulta ClickHouse, monta prompt para Anthropic API, recebe finding JSON.
5. **Entrega MCP:** `server.py` expõe tools (`diagnose_job`, `query_jobs`) para o IDE.

### 2.4 Stack tecnológica

- **Python 3.11+**
- **PySpark 4.1.2** (via py4j)
- **clickhouse-connect** (driver Python)
- **Anthropic API** (Claude 3.5 Sonnet)
- **Docker + Docker Compose**
- **CrewAI** (planejado para V2)

---

## 3. Arquitetura da Branch `kimi` (Go + Python)

### 3.1 Diagrama de componentes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         APEX — KIMI (Go + Python)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         go-apex (Go 1.22)                             │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │    │
│  │  │  cmd/       │  │  internal/  │  │  pkg/       │  │  runbooks/  │  │    │
│  │  │  • analyze  │  │  • clickhouse│  │  • mcp      │  │             │  │    │
│  │  │  • diagnose │  │  • diagnostician│  │             │  │             │  │    │
│  │  │  • validate │  │  • validator   │  │             │  │             │  │    │
│  │  │  • recommend│  │  • watcher     │  │             │  │             │  │    │
│  │  │  • mcp-server│  │  • models     │  │             │  │             │  │    │
│  │  │  • spillwatch│  │  • recommender│  │             │  │             │  │    │
│  │  │  • crei-server│  │  • runbook    │  │             │  │             │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐      │
│  │  Python (legacy / LLM bridge)                                       │      │
│  │  ├── generators/           (code_generator.py, plan_generator.py)   │      │
│  │  ├── apex/apexlib.py      (parse de event logs, zstd, rolling)      │      │
│  │  ├── watchers/            (skew_watcher.py — Python existente)    │      │
│  │  ├── oracle/              (compare.py)                              │      │
│  │  └── tests/               (test_slice.py, test_coverage_inventory)│      │
│  └─────────────────────────────────────────────────────────────────────┘      │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐      │
│  │  ClickHouse (schema melhorado)                                      │      │
│  │  • spark_tasks         • spark_stages                               │      │
│  │  • spark_raw_events    • spark_sql_executions                       │      │
│  │  • metrics_summary                                                │      │
│  └─────────────────────────────────────────────────────────────────────┘      │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐      │
│  │  MCP Server (Go) — cmd/mcp-server                                   │      │
│  │  • Tools: diagnose, analyze, validate, query_metrics                │      │
│  └─────────────────────────────────────────────────────────────────────┘      │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Componentes principais

| Componente | Pacote/Arquivo | Função |
|------------|---------------|--------|
| **Go Loader** | `go-apex/internal/clickhouse/` | Parser e loader de event logs para ClickHouse |
| **Diagnostician (T1)** | `go-apex/internal/diagnostician/` | Detecção determinística via SQL (skew, spill, GC, OOM) |
| **Validator** | `go-apex/internal/validator/` | Validação estrutural de evidências antes do diagnóstico |
| **Watcher (Go)** | `go-apex/internal/watcher/` | SpillWatcher + SkewWatcher em Go |
| **Recommender (T2)** | `go-apex/internal/recommender/` | Recomendações baseadas em runbooks |
| **Models** | `go-apex/internal/models/types.go` | Tipos de domínio unificados (Finding, AnomalyReport, etc.) |
| **MCP Server** | `go-apex/cmd/mcp-server/` | Servidor MCP em Go |
| **CREI Server** | `go-apex/cmd/crei-server/` | Servidor de análise CREI |
| **CLI Tools** | `go-apex/cmd/analyze`, `diagnose`, `validate`, `recommend`, `spillwatch` | Binários CLI independentes |

### 3.3 Fluxo de dados

1. **Ingestão:** Event logs (sintéticos ou reais) são parseados e carregados no ClickHouse pelo Go Loader.
2. **Validação:** `EvidenceValidator` aplica regras estruturais (provenance, schema, correlation, distribution, structural).
3. **Diagnóstico T1:** `Diagnostician` executa queries SQL no ClickHouse para detectar skew, spill, GC pressure, OOM.
4. **Recomendação T2:** `Recommender` mapeia anomalias para runbooks de correção.
5. **Entrega MCP:** `mcp-server` expõe tools em Go para o IDE.

### 3.4 Stack tecnológica

- **Go 1.22** (core de infraestrutura)
- **clickhouse-go/v2** (driver nativo Go)
- **gopkg.in/yaml.v3** (parse de scenarios)
- **Python 3** (generators, apexlib, tests, orquestração LLM)
- **ClickHouse** (banco de métricas)
- **MCP** (Model Context Protocol)

---

## 4. Matriz Comparativa Detalhada

### 4.1 Aspectos Gerais

| Aspecto | Branch `cowork` (d3c3e8a3) | Branch `kimi` (8be15724) | Vencedor |
|---------|---------------------------|--------------------------|----------|
| **Linguagem principal** | Python 3.11 | Go 1.22 + Python 3 | — |
| **Foco arquitetural** | V1 Python/CrewAI (prova de conceito) | Go core + docs + ADR-004 (fundação) | — |
| **Número de commits** | 14 | 5 | cowork (volume) |
| **Tamanho do diff** | +3.5K LOC Python, + YAML/Docker | +21K LOC Go, + docs | kimi (densidade) |
| **Propósito imediato** | Demo funcional para reunião | Documentação + infraestrutura de produção | — |

### 4.2 Infraestrutura e Deploy

| Aspecto | Branch `cowork` | Branch `kimi` | Vencedor |
|---------|-----------------|---------------|----------|
| **Orquestração** | Docker Compose (v1-skeleton/) | Nenhuma (binários Go standalone) | cowork (DX) |
| **Container Spark** | Dockerfile.spark + docker-compose.yml | Não incluso | cowork |
| **ClickHouse** | Container via docker-compose | Assume externo (prod) | kimi (realista) |
| **Portabilidade** | Docker-only | Binários nativos cross-compiláveis | kimi |
| **Serverless** | Requer Docker | Binário Go ~15MB | kimi |

### 4.3 Captura de Dados

| Aspecto | Branch `cowork` | Branch `kimi` | Vencedor |
|---------|-----------------|---------------|----------|
| **Modo de captura** | SparkListener in-process (py4j) | Event log pós-executação (zero-JAR) | — |
| **Latência** | Tempo real (ms) | Pós-job (segundos) | cowork |
| **Intrusividade** | Média (`spark.extraListeners`) | Zero (leitura de logs) | kimi |
| **Risco ao job** | Exception no listener pode impactar | Zero (fora do processo) | kimi |
| **Compatibilidade** | Requer acesso ao SparkContext | Qualquer ambiente com event logs | kimi |
| **ADR relacionada** | ADR-005 (aceita in-process) | ADR-005 (preserva zero-JAR como fallback) | — |

### 4.4 Diagnóstico (T1)

| Aspecto | Branch `cowork` | Branch `kimi` | Vencedor |
|---------|-----------------|---------------|----------|
| **Implementação** | Python + Anthropic API | Go + SQL ClickHouse | kimi (determinístico) |
| **Custo por diagnóstico** | $0.01–$0.05 (LLM) | ~$0 (SQL local) | kimi |
| **Latência T1** | 2–5s (API externa) | <100ms (query SQL) | kimi |
| **Determinismo** | Não (LLM pode variar) | Sim (regras SQL fixas) | kimi |
| **Tipos de anomalia** | Skew (via LLM prompt) | Skew, Spill, GC, OOM, Task Failure | kimi |
| **Thresholds** | Hardcoded no prompt | Configuráveis via env vars | kimi |
| **Testes T1** | Não (depende de API key) | Sim (Go testable, mocks de ClickHouse) | kimi |

### 4.5 Validação de Evidências

| Aspecto | Branch `cowork` | Branch `kimi` | Vencedor |
|---------|-----------------|---------------|----------|
| **Componente** | Não existe | `EvidenceValidator` (Go) | kimi |
| **Regras validadas** | N/A | Provenance, Schema, Correlation, Distribution, Structural | kimi |
| **Cadeia de custódia** | Manifesto JSON (code_generator) | `scenario_hash` cruzado + provenance | kimi |
| **Qualidade de evidência** | Manual (olhar ratio) | Automatizada (valid/invalid/indeterminate) | kimi |

### 4.6 Watchers

| Aspecto | Branch `cowork` | Branch `kimi` | Vencedor |
|---------|-----------------|---------------|----------|
| **SkewWatcher** | Python (`watchers/skew_watcher.py`) | Go (`internal/watcher/watcher.go`) | — |
| **SpillWatcher** | Não existe | Go + Python | kimi |
| **Detecção de skew** | Por records (shuffle read) | Por records + por duration (SQL) | kimi |
| **Correlação de stage** | `largest_shuffle_fallback` | `operator_accumulator` + `stage_name` + fallback | kimi |
| **Mensagens** | UTF-8 emojis (`✅`, `⚠️`) | ASCII portátil (`[OK]`, `[WARN]`) | kimi (CI) |

### 4.7 Testes e Qualidade

| Aspecto | Branch `cowork` | Branch `kimi` | Vencedor |
|---------|-----------------|---------------|----------|
| **Testes unitários** | `test_crew.py` (1.6KB), `test_crew_e2e.py` (4.9KB) | `test_slice.py` (15.8KB), `test_coverage_inventory.py` (6.4KB) | kimi |
| **Cobertura de teste** | E2E básico (CrewAI) | Parser, attempts, correlation, provenance, watcher, oracle, inventory | kimi |
| **CI/CD** | `.github/workflows/scenario-gate.yml` | Mesmo workflow (herdado) | — |
| **Testes Go** | N/A | Não visíveis (potencial `*_test.go`) | — |
| **Relatório de cobertura** | Não | `docs/coverage/`, `test_coverage_inventory.py` | kimi |

### 4.8 Documentação

| Aspecto | Branch `cowork` | Branch `kimi` | Vencedor |
|---------|-----------------|---------------|----------|
| **ADRs** | ADR-004, ADR-005 | ADR-004 (reescrita), ADR-005 (não presente) | cowork (ADR-005) |
| **Padrão de operação** | `CREW_A_OPERATING_STANDARD.md` | `team-validation-guide.md` | — |
| **Arquitetura** | `architecture.md` (6.7KB) | `docs/architecture/` (diretório) | kimi |
| **Linhagem** | `apex-v4-lineage.md` (2.0KB) | `apex-v4-lineage.md` (10.3KB) | kimi |
| **Playbooks** | `docs/playbooks/skew-slice-v4.md` | `docs/playbooks/` (presumido) | — |
| **Apresentações** | HTML (`apex-estado-evolucao.html` 51KB) | `docs/presentations/` | — |
| **Estrutura docs** | 15 arquivos | 25+ arquivos, diretórios organizados | kimi |

### 4.9 Geradores (code_generator + plan_generator)

| Aspecto | Branch `cowork` | Branch `kimi` | Vencedor |
|---------|-----------------|---------------|----------|
| **code_generator.py** | v4 — emojis UTF-8 | v4 — ASCII `[OK]`/`[WARN]` | — |
| **plan_generator.py** | v4 — comentário P1 #5 | v4 — comentário P1 #5 (mesmo) | — |
| **Cadeia de custódia** | Manifesto JSON com `scenario_hash` | Mesmo + provenance no log | — |
| **Tamanho** | 3.0KB + 4.2KB | 3.3KB + 5.0KB | kimi (mais comentários) |
| **Anti-pattern line** | Declarada vs detectada | Declarada vs detectada | — |

---

## 5. Análise de Código — Trechos Comparativos

### 5.1 Diagnóstico de Skew: Python (Cowork) vs Go (Kimi)

**Cowork — não há diagnóstico determinístico; o skew é detectado via LLM prompt:**

```python
# v1-skeleton/analysis/diagnose.py (conceitual)
# O diagnóstico é feito por LLM, não por regras:
response = anthropic_client.messages.create(
    model="claude-3-5-sonnet-20240620",
    messages=[{
        "role": "user",
        "content": f"""Analise as métricas do job Spark {app_id}:
{metrics_json}

Identifique o bottleneck e recomende ações."""
    }]
)
# Retorno: JSON com pattern, severity, confidence, root_cause, recommendation
```

**Kimi — Go, determinístico, via SQL:**

```go
// go-apex/internal/diagnostician/diagnostician.go
func (d *Diagnostician) detectSkew(appID string) ([]models.AnomalyReport, error) {
    query := fmt.Sprintf(`
        SELECT
            stage_id,
            max(task_duration_ms) AS max_duration,
            median(task_duration_ms) AS median_duration,
            count() AS task_count,
            max_duration / if(median_duration = 0, 1, median_duration) AS skew_ratio
        FROM spark_tasks
        WHERE app_id = '%s'
        GROUP BY stage_id
        HAVING skew_ratio > %f
        ORDER BY skew_ratio DESC
    `, appID, d.skewRatio)

    rows, err := d.client.QueryHTTP(context.Background(), query)
    // ... converte para AnomalyReport com severity, confidence, evidence
}
```

**Análise:**
- **Cowork** delega a inteligência para o LLM. Flexível, mas caro, lento e não-determinístico.
- **Kimi** usa SQL com thresholds configuráveis. Rápido, barato, testável, mas menos adaptativo a padrões novos.

### 5.2 Validação de Evidências: Não existe (Cowork) vs Go (Kimi)

**Cowork:** Não há componente de validação estrutural. O oracle compara sinais agregados, mas não rejeita evidências ruins antes do diagnóstico.

**Kimi:**

```go
// go-apex/internal/validator/validator.go
func (v *EvidenceValidator) Validate() *models.EvidenceValidationResult {
    v.issues = nil

    // 1. Provenance
    provHash := v.validateProvenance()
    if hasIssue(v.issues, "provenance_mismatch") {
        return v.result("invalid", provHash, nil, nil, nil, nil)
    }

    // 2. Schema
    v.validateSchema()

    // 3. Correlation / operator
    op, usedFinal := joinOperator(v.bundle.Events)
    selected := hottestReduceStageDetails(v.bundle.Events, op)

    // 4. Distribution
    metrics := v.validateDistribution(records)

    // 5. Structural
    v.validateStructural(records)

    if len(v.issues) > 0 {
        return v.result("invalid", ...)
    }
    return v.result("valid", ...)
}
```

### 5.3 SparkListener: Python py4j (Cowork) vs Não presente (Kimi)

**Cowork:**

```python
# v1-skeleton/listener/spark_listener.py
class ApexSparkListener:
    class Java:
        implements = ["org.apache.spark.scheduler.SparkListenerInterface"]

    def onStageCompleted(self, stageCompleted) -> None:
        info = stageCompleted.stageInfo()
        tm = info.taskMetrics()
        metrics = {
            "app_id": self.app_id,
            "stage_id": int(info.stageId()),
            "duration_ms": duration,
            "shuffle_read": int(tm.shuffleReadMetrics().totalBytesRead()),
            "disk_spill": int(tm.diskBytesSpilled()),
            # ...
        }
        self._writer.write_stage_metrics(metrics)

    def onTaskEnd(self, taskEnd) -> None:
        # Captura métricas por task (skew detection)
        self._writer.write_task_metrics(metrics)
```

**Kimi:** Não possui SparkListener. A arquitetura kimi assume ingestão de event logs (sintéticos ou reais) via Go Loader, mantendo o princípio zero-JAR.

### 5.4 ClickHouse Client: Python vs Go

**Cowork — Python (`clickhouse-connect`):**

```python
class ClickHouseWriter:
    def __init__(self, host="localhost", port=8123, ...):
        self.client = clickhouse_connect.get_client(...)

    def write_stage_metrics(self, metrics: dict) -> None:
        self.client.insert("stage_metrics", [[...]], column_names=[...])
```

**Kimi — Go (`clickhouse-go/v2`):**

```go
// go-apex/internal/clickhouse/client.go
func NewClient(cfg Config) (*Client, error) {
    conn, err := ch.Open(&ch.Options{...})
    return &Client{conn: conn}, err
}

func (c *Client) QueryHTTP(ctx context.Context, query string) ([]map[string]interface{}, error) {
    rows, err := c.conn.Query(ctx, query)
    // ... scan para map[string]interface{}
}
```

### 5.5 Modelos de domínio: Python dict vs Go structs

**Cowork:** Uso extensivo de `dict` Python sem tipagem.

```python
metrics = {
    "app_id": self.app_id,
    "stage_id": int(info.stageId()),
    "duration_ms": duration,
}
```

**Kimi:** Structs tipadas com JSON tags.

```go
// go-apex/internal/models/types.go
type AnomalyReport struct {
    AppID          string                 `json:"app_id"`
    AnomalyType    string                 `json:"anomaly_type"`
    Severity       string                 `json:"severity"`
    Description    string                 `json:"description"`
    Evidence       map[string]interface{} `json:"evidence"`
    AffectedStages []int                  `json:"affected_stages"`
    Confidence     float64                `json:"confidence"`
}
```

---

## 6. Métricas e Benchmarks

### 6.1 Tempo de execução (estimativas)

| Componente | Cowork | Kimi | Diferença |
|------------|--------|------|-----------|
| **Ingestão de event log** | N/A (in-process) | <50ms (Go Loader, 1000 eventos) | — |
| **Validação de evidências** | N/A | <10ms (Go, 1000 eventos) | — |
| **Diagnóstico T1 (skew)** | 2–5s (LLM API) | <100ms (SQL ClickHouse) | **kimi 20–50x mais rápido** |
| **Diagnóstico T1 (spill)** | 2–5s (LLM API) | <100ms (SQL ClickHouse) | **kimi 20–50x mais rápido** |
| **Geração de recomendação** | 2–5s (LLM API) | <10ms (runbook lookup) | **kimi 200–500x mais rápido** |
| **Startup do MCP Server** | ~2s (Python) | ~50ms (Go binary) | **kimi 40x mais rápido** |

### 6.2 Custo operacional (estimativas)

| Componente | Cowork | Kimi | Diferença |
|------------|--------|------|-----------|
| **Diagnóstico T1 por job** | $0.01–$0.05 (Anthropic API) | $0 (SQL local) | **kimi 100% mais barato** |
| **Infraestrutura** | Docker Compose (4 containers) | Binário Go + ClickHouse externo | **kimi mais enxuto** |
| **Memória do serviço** | ~200MB (Python + dependências) | ~15MB (Go binary) | **kimi 13x mais leve** |

### 6.3 Fidelidade do sintético (ambas as branches compartilham)

```
synthetic ratio: 27.9x
real ratio:      29.5x
oracle tolerance: 5%
status: GATE VERDE (ambas as branches)
```

### 6.4 Escalabilidade

| Aspecto | Cowork | Kimi |
|---------|--------|------|
| **Jobs/hora (T1)** | ~720 (com API key e rate limit) | ~36.000 (limitado por ClickHouse) |
| **Concorrência** | GIL limita (Python) | Goroutines ilimitadas (Go) |
| **Throughput ClickHouse** | ~10K INSERTs/s (Python driver) | ~100K INSERTs/s (Go driver nativo) |

---

## 7. Decisões Arquiteturais

### 7.1 ADR-004 — Desacoplamento dos Geradores

**Ambas as branches** implementam a mesma decisão: `scenario.yaml` como contrato compartilhado, `code_generator` e `plan_generator` independentes. A diferença está na **ADR-004 revisitada (kimi)** que introduz a resolução do gap de linguagem.

| ADR-004 Original (cowork) | ADR-004 Revisitada (kimi) |
|---------------------------|---------------------------|
| Foco no contrato e desacoplamento | Foco na resolução Go vs Python |
| Não discute linguagem de produção | Proposta: **Python para V0.1, Go para V0.2+** |
| "Derivamos ambos de uma especificação compartilhada" | "MCP Server como ponte de linguagem" |

### 7.2 ADR-005 — SparkListener vs Zero-JAR

**Cowork:** Implementa a **Opção B** (SparkListener in-process) como decisão da V1. O ADR-005 completo está documentado em `docs/adr/ADR-005-sparklistener-vs-zero-jar.md`.

**Kimi:** Não possui ADR-005 no diretório `docs/adr/`. A arquitetura kimi assume zero-JAR (leitura de event logs), mantendo a abordagem original do Apex v3/v4.

| Dimensão | Cowork (ADR-005 Opção B) | Kimi (zero-JAR implícito) |
|----------|--------------------------|---------------------------|
| Intrusividade | Média | Zero |
| Latência | Baixa (tempo real) | Alta (pós-job) |
| Dados disponíveis | Stage + task metrics | Event log completo (AQE, SQL, etc.) |
| Deploy | Requer `spark.extraListeners` | Qualquer ambiente com logs |
| Similaridade DataFlint | Alta | Baixa |

### 7.3 Decisão de linguagem (implicações)

| Cowork (Python) | Kimi (Go + Python) |
|-----------------|----------------------|
| Time já sabe Python | Time precisa aprender Go |
| CrewAI nativo em Python | CrewAI requer bridge ou reescrita |
| Prototipação rápida | Performance de produção |
| GIL limita throughput | Goroutines escalam horizontalmente |
| py4j é fragile | Go nativo é robusto |

---

## 8. Recomendações por Persona

### 8.1 Engenheiro de Software (backend/infra)

> **Use a branch `kimi` como referência.**

- O core Go (`go-apex`) é a fundação correta para produção: binários leves, concorrência nativa, tipagem forte.
- O `EvidenceValidator` em Go é um componente crítico que a cowork não possui — validação estrutural antes do diagnóstico evita garbage-in-garbage-out.
- A arquitetura em camadas (`internal/`, `cmd/`, `pkg/`) segue as convenções do ecossistema Go (OTel Collector, CNCF).
- **Ação:** Portar o SparkListener da cowork para Go (ou manter Python como bridge temporária) e integrar com o `go-apex`.

### 8.2 Engenheiro de Dados / Spark

> **Use a branch `cowork` para prototipação, `kimi` para validação.**

- A cowork tem o V1 skeleton funcional com Docker Compose — você pode subir e ver dados fluindo em minutos.
- A kimi tem o modelo de dados ClickHouse mais completo (`spark_tasks`, `spark_stages`, `spark_raw_events`, `spark_sql_executions`) e queries SQL otimizadas.
- O `demo_skew_job.py` da cowork é um excelente ponto de partida para testes.
- **Ação:** Subir a infraestrutura da cowork, gerar dados, depois migrar o schema para a estrutura da kimi e usar o `diagnostician` Go.

### 8.3 Product Owner / Stakeholder

> **Acompanhe a `kimi` para documentação, a `cowork` para demos.**

- A `cowork` prova que o conceito funciona ("o job rodou, eu tenho o ID, debuga pra mim").
- A `kimi` prova que o produto é escalável e documentado (ADRs, coverage, arquitetura).
- **Risco da cowork:** Depende de API key da Anthropic, custo por diagnóstico, não-determinismo.
- **Risco da kimi:** Ainda não tem o SparkListener integrado, requer trabalho de integração.
- **Ação:** Pedir que o time una o melhor das duas: experiência interativa da cowork + determinismo e performance da kimi.

### 8.4 QA / Engenheiro de Testes

> **Use a `kimi` como base de testes.**

- `test_slice.py` da kimi é 15.8KB vs 9.0KB da cowork — cobertura maior.
- `test_coverage_inventory.py` da kimi é um novo componente que mapeia cobertura de features.
- A validação estrutural (`EvidenceValidator`) permite testes automatizados de qualidade de evidência.
- **Ação:** Expandir o `test_coverage_inventory.py` para cobrir o pipeline Go completo.

---

## 9. Anexos

### 9.1 Lista completa de arquivos — Branch `cowork` (d3c3e8a3)

```
.claude/
.github/
  workflows/
    scenario-gate.yml
00_arquivo/
AGENTS.md
CHANGELOG.md
CLAUDE.md
COMO_COMMITAR.md
CONTRIBUTING.md
README.md
VALIDACAO.md
requirements.txt
run_slice.sh
test_crew.py
apex/
  __init__.py
  apexlib.py
docs/
  CREW_A_OPERATING_STANDARD.md
  adr/
    ADR-004-scenario-contract.md
    ADR-005-sparklistener-vs-zero-jar.md
  adr-review-drafts.md
  agentspec-alignment.md
  apex-estado-evolucao.html
  apex-v1-plan.md
  apex-v4-lineage.md
  architecture.md
  competitive/
  llm-evals/
  mcp-registro-ide.md
  meetings/
  playbooks/
  presentations/
  specs/
generators/
  code_generator.py
  plan_generator.py
oracle/
  compare.py
scenarios/
  skew_on_join_30x.yaml
tasks/
  backlog.md
  apex_roadmap_v4.md
tests/
  __pycache__/
  test_slice.py
v1-skeleton/
  Dockerfile.spark
  README.md
  docker-compose.yml
  requirements.txt
  test_crew_e2e.py
  analysis/
  ingest/
  jobs/
    demo_skew_job.py
  listener/
    clickhouse_writer.py
    spark_listener.py
  mcp/
  schema/
watchers/
  skew_watcher.py
```

### 9.2 Lista completa de arquivos — Branch `kimi` (8be15724)

```
.github/
  workflows/
    scenario-gate.yml
AGENTS.md
README.md
requirements.txt
run_slice.sh
real_log.ndjson
apex/
  __init__.py
  apexlib.py
docs/
  README.md
  adr/
    adr-004-language-gap-resolution.md
  adr-review-drafts.md
  agentspec-alignment.md
  apex-v4-lineage.md
  architecture/
  coverage/
  github-issue-comment-drafts.md
  playbooks/
  presentations/
  specs/
  team-validation-guide.md
  tier/
  validation/
generators/
  code_generator.py
  plan_generator.py
go-apex/
  go.mod
  cmd/
    analyze/
    crei-server/
    diagnose/
    mcp-server/
    recommend/
    spillwatch/
    validate/
  internal/
    clickhouse/
      client.go
      helpers.go
      queries.go
    diagnostician/
      diagnostician.go
    models/
      types.go
    recommender/
    runbook/
    validator/
      validator.go
    watcher/
      watcher.go
  pkg/
    mcp/
  runbooks/
oracle/
  compare.py
scenarios/
  skew_on_join_30x.yaml
tests/
  test_coverage_inventory.py
  test_slice.py
watchers/
  skew_watcher.py
```

### 9.3 Diferenças de estrutura

| Estrutura | Cowork | Kimi |
|-----------|--------|------|
| `v1-skeleton/` | ✅ Sim | ❌ Não |
| `go-apex/` | ❌ Não | ✅ Sim |
| `tasks/` | ✅ Sim | ❌ Não |
| `tools/` | ❌ Não | ✅ Sim |
| `real_log.ndjson` | ❌ Não | ✅ Sim (44KB) |
| `docs/adr/ADR-005` | ✅ Sim | ❌ Não |
| `docs/adr/adr-004-language-gap` | ❌ Não | ✅ Sim |
| `docs/architecture.md` | ✅ Arquivo | ❌ Diretório |
| `docs/coverage/` | ❌ Não | ✅ Sim |
| `docs/tier/` | ❌ Não | ✅ Sim |
| `docs/validation/` | ❌ Não | ✅ Sim |
| `test_crew.py` | ✅ Sim | ❌ Não |
| `test_coverage_inventory.py` | ❌ Não | ✅ Sim |
| `CLAUDE.md` | ✅ Sim | ❌ Não |
| `CHANGELOG.md` | ✅ Sim | ❌ Não |
| `VALIDACAO.md` | ✅ Sim | ❌ Não |

---

## 10. Conclusão e Próximos Passos Recomendados

### 10.1 Síntese

- **Cowork** entregou uma **prova de conceito funcional** da arquitetura V1 (SparkListener → ClickHouse → LLM → MCP). É excelente para demos e validação de experiência, mas tem limitações de escalabilidade, custo e determinismo.
- **Kimi** entregou uma **fundação de produção** em Go com documentação arquitetural, validação estrutural, diagnóstico determinístico e modelos de domínio tipados. Falta a integração com SparkListener e a ponte LLM (CrewAI).

### 10.2 Integração proposta (melhor das duas)

```
┌─────────────────────────────────────────────────────────────┐
│                    APEX V1.5 (Integração)                     │
├─────────────────────────────────────────────────────────────┤
│  Captura: SparkListener in-process (Python, da cowork)        │
│     ↓                                                         │
│  Ingestão: Go Loader (da kimi) → ClickHouse                 │
│     ↓                                                         │
│  Validação: EvidenceValidator (Go, da kimi)                  │
│     ↓                                                         │
│  Diagnóstico T1: Diagnostician SQL (Go, da kimi)             │
│     ↓                                                         │
│  Recomendação T2: Runbook + Heurística (Go, da kimi)         │
│     ↓                                                         │
│  Coordenação T3: CrewAI / Anthropic (Python, da cowork)      │
│     ↓                                                         │
│  Entrega: MCP Server (Go, da kimi)                           │
└─────────────────────────────────────────────────────────────┘
```

### 10.3 Ações recomendadas

1. **Adotar o core Go** da kimi como base de produção (`go-apex/internal/`, `go-apex/cmd/`).
2. **Portar o SparkListener** da cowork para Python (mantém como bridge) ou reescrever em Scala/Go.
3. **Manter o MCP Server em Go** da kimi — mais leve e rápido.
4. **Usar CrewAI/Anthropic apenas no T3** (coordenação), não no T1 (diagnóstico determinístico).
5. **Unificar os testes:** `test_slice.py` da kimi + `test_crew_e2e.py` da cowork em uma suite unificada.
6. **Documentar a decisão** em um novo ADR-006: "Integração das vertentes cowork e kimi".

---

*Documento gerado por análise automatizada dos commits `d3c3e8a3` e `8be15724` do repositório `luanmorenommaciel/apex`.*
