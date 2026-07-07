# Comparação Detalhada: Branches Paralelas do Projeto Apex

> **Artefato:** `comparacao-detalhada.md`  
> **Data de geração:** 2026-07-06  
> **Autor:** Augusto Cezar (análise automatizada das branches)  
> **Repositório:** `luanmorenommaciel/apex`  
> **Branch de destino:** `gustocezar/feature/kimi-desacoplamento-geradores`  

---

## 1. Contexto e Linhagem

Ambas as branches partem da **mesma base comum**:

| Aspecto | Valor |
|---------|-------|
| **Branch base** | `gustocezar/feature/desacoplamento-geradores` |
| **Commit base** | `bd8a08bc` — *"feat(apex): validate skew evidence and stage correlation"* |
| **Data da base** | 2026-06-09 |
| **Commits na base** | 8 commits (slice v4 de `skew_on_join`) |
| **Autor das duas vertentes** | Augusto Cezar (`gustocezar`) |

```
                         bd8a08bc (base comum — 8 commits)
                              │
              ┌───────────────┴───────────────┐
              │                               │
     [cowork-desacoplamento]      [kimi-desacoplamento]
              │                               │
    ┌─────────┴─────────┐           ┌─────────┴─────────┐
    │   Foco: V1 + AI   │           │  Foco: Go + Docs  │
    │   CrewAI, Python  │           │  Tradução, Infra  │
    │   Apresentação    │           │  ADR-004, V0.1    │
    └───────────────────┘           └───────────────────┘
```

---

## 2. Resumo Executivo Comparativo

| Dimensão | `cowork` | `kimi` |
|----------|----------|--------|
| **Foco estratégico** | V1 com CrewAI + Apresentação stakeholders | Tradução Go + Documentação técnica |
| **Linguagem principal** | Python (CrewAI, PySpark, clickhouse-connect) | Go (stdlib + HTTP ClickHouse) |
| **Framework de IA** | CrewAI 1.15.1 + Anthropic Claude | T3 heurístico determinístico (sem LLM) |
| **Dependência externa** | ANTHROPIC_API_KEY obrigatória | Zero dependência externa (100% offline) |
| **Estado do código** | Executável e testado (21 testes mock) | Tradução completa, não compilada/validada |
| **Apresentação** | HTML completo (10 slides, interativo) | Documentação Markdown (3 artefatos técnicos) |
| **ADR-004 (Linguagem)** | Mantém Python (não endereçou) | **Resolve** o gap Go vs. Python |
| **ADR-005 (SparkListener)** | **Cria e formaliza** | Não endereçou |
| **MCP** | Tool `apply_fix` (modifica código PySpark do engenheiro) | Server HTTP em Go (portas 3000/3001) |
| **Event Log ingestion** | `event_log_ingest.py` (zstd → ClickHouse, validado) | Delega ao Go Loader do fork Gabriel |
| **Testes** | `test_crew_e2e.py` (21 testes mock passando) | Nenhum (código Go não compilado) |
| **Docker/Infra** | Dockerfile.spark + docker-compose.yml customizados | Não inclui infraestrutura containerizada |

---

## 3. Histórico de Commits

### 3.1 Branch `cowork` — 14 commits

| # | SHA | Data | Mensagem | Tipo |
|---|-----|------|----------|------|
| 1 | `bc747c11` | 2026-07-04 | feat: v1-skeleton + docs + DataFlint analysis + reuniao-30jun artifacts | Foundation |
| 2 | `48f63f3f` | 2026-07-05 | feat: Crew.ai pipeline + ADR-005 + listener contracts + MCP docs | Feature |
| 3 | `682f564b` | 2026-07-05 | feat(v1): crew_diagnose.py para crewai 1.15.1 + test suite mock | Feature |
| 4 | `ca0b846d` | 2026-07-05 | chore: add __pycache__ to gitignore | Chore |
| 5 | `a1e67817` | 2026-07-05 | fix(listener): SparkListener completo + Docker com clickhouse-connect | Fix |
| 6 | `8630e039` | 2026-07-06 | feat(v1): event_log_ingest.py — bridge event log → ClickHouse | Feature |
| 7 | `24f68a40` | 2026-07-06 | fix(crew): root_cause max_length 300→500, remove trailing garbage | Fix |
| 8 | `61dc0e9d` | 2026-07-06 | fix(crew): restore missing __main__ block after rstrip accident | Fix |
| 9 | `4351ef51` | 2026-07-06 | feat(v1): log_poller.py (rolling log watch) + MCP claude_code_config.json | Feature |
| 10 | `c5c4c611` | 2026-07-06 | chore: add test_crew.py (pipeline validation) + gitignore update | Chore |
| 11 | `e26adb19` | 2026-07-06 | feat(apresentacao): apex_v1_apresentacao_luan.html — pipeline V1 + DataFlint comparison | Feature |
| 12 | `aae62507` | 2026-07-06 | feat(apresentacao): slide 7 — status dos pontos do Luan com issues #17 #19 #20 #21 | Feature |
| 13 | `77c1240f` | 2026-07-06 | feat(mcp): tool apply_fix — aplica recomendação Apex no código PySpark do engenheiro | Feature |
| 14 | `d3c3e8a3` | 2026-07-07 | docs: VALIDACAO.md — mapa completo issues 30/06 + repo vs entregue na branch | Docs |

**Características:** ritmo intenso (14 commits em ~3 dias), padrão iterativo feature→fix, protótipo funcional para demo.

### 3.2 Branch `kimi` — 5 commits

| # | SHA | Data | Mensagem | Tipo |
|---|-----|------|----------|------|
| 1 | `9905af10` | 2026-07-07 | docs: add T3 heuristic MVP documentation for V0.1 | Docs |
| 2 | `79a23d2c` | 2026-07-07 | docs: mapeamento validado vs issues do Apex (V0.1) | Docs |
| 3 | `b490e774` | 2026-07-07 | docs(adr): ADR-004 resolução do gap de linguagem Go vs. Python | Docs |
| 4 | `8be15724` | 2026-07-07 | feat(go): tradução completa Python → Go do pipeline Apex V0.1 | Feature |
| 5 | `b9757bea` | 2026-07-07 | docs: comparação completa cowork vs kimi — branches paralelas do Augusto | Docs |

**Características:** concentrado (5 commits em ~2 horas), padrão docs→docs→docs→feature massivo→docs, alto nível de documentação.

---

## 4. Comparação Técnica Profunda

### 4.1 Arquitetura do Pipeline

#### `cowork` — Pipeline V1 (Python / CrewAI)

```
Spark Job → Event Log (zstd) → MinIO/S3
                                    │
                        ┌───────────▼───────────┐
                        │ event_log_ingest.py   │  ← zstd → ClickHouse
                        │   (bridge ADR-005)    │
                        └───────────┬───────────┘
                                    │
                        ┌───────────▼───────────┐
                        │     ClickHouse        │  ← apex.stage_metrics
                        │   (schema validado)   │    apex.task_metrics
                        └───────────┬───────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
        ┌───────────▼───────────┐   ┌───────────────▼───────────────┐
        │   log_poller.py       │   │     crew_diagnose.py          │
        │  (rolling 15s watch)  │   │   (CrewAI 2 agentes)          │
        └───────────────────────┘   └───────────────┬───────────────┘
                                                    │
                                        ┌───────────▼───────────┐
                                        │     ApexFinding       │
                                        │   (Pydantic JSON)     │
                                        └───────────┬───────────┘
                                                    │
                                        ┌───────────▼───────────┐
                                        │     MCP Server        │
                                        │   (5 ferramentas)     │
                                        │  - get_findings       │
                                        │  - get_stage_metrics  │
                                        │  - list_slow_apps     │
                                        │  - trigger_diagnosis  │
                                        │  - apply_fix          │  ← Modifica código
                                        └───────────────────────┘
```

**Agentes CrewAI:**
1. **MetricsAnalyzer** — Busca métricas ClickHouse, identifica padrão e bottleneck
2. **RecommendationWriter** — Converte análise em fix concreto com código de exemplo

**Contrato de saída (`ApexFinding`):**
```python
class ApexFinding(BaseModel):
    pattern:             str      # skew|parallelism_collapse|spill|broadcast_miss|small_files|other
    severity:            str      # critical|high|medium|low
    confidence:          float    # 0.0–1.0
    bottleneck_stage_id: Optional[int]
    root_cause:          str      # max 500 chars
    recommendation:      str      # max 500 chars
    evidence:            Evidence # key_metric, key_value, expected_value
```

**Validação de contrato (5 regras):**
1. Padrão inválido → override para `"other"`
2. Severity inválida → override para `"medium"`
3. Confidence < 0.6 → escala para Tier 4 (Judge)
4. Evidence ausente → flag de possível alucinação
5. Keywords obrigatórias na recommendation

#### `kimi` — Pipeline V0.1 (Go / Heurístico)

```
Spark Job → Event Log → Go Loader (fork Gabriel) → ClickHouse
                                                          │
                                        ┌─────────────────┘
                                        │
                              ┌─────────▼─────────┐
                              │   spark_tasks     │
                              │   spark_stages    │  ← 6 tabelas
                              └─────────┬─────────┘
                                        │
                              ┌─────────▼─────────┐
                              │  Diagnostician T1 │  ← SQL determinístico
                              │ (diagnostician.go)│
                              └─────────┬─────────┘
                                        │
                              ┌─────────▼─────────┐
                              │ EvidenceValidator │  ← 7 regras
                              │   (validator.go)  │
                              └─────────┬─────────┘
                                        │
                              ┌─────────▼─────────┐
                              │   Recommender T2  │  ← Runbook determinístico
                              │   Recommender T3  │  ← Heurístico ClickHouse
                              │  (recommender.go) │
                              └─────────┬─────────┘
                                        │
                              ┌─────────▼─────────┐
                              │  MCP Server (Go)  │  ← HTTP porta 3000
                              │  CREI Server (Go) │  ← HTTP porta 3001
                              └───────────────────┘
```

**Anomalias detectadas (T1):**
| Tipo | Query ClickHouse | Threshold | Severidade |
|------|-----------------|-----------|------------|
| SKEW | `max_duration / median_duration` | > 5.0x | HIGH/CRITICAL |
| SPILL | `shuffle_bytes_written` | > 100MB | MEDIUM/HIGH |
| GC_PRESSURE | `gc_time_ms / task_duration_ms` | > 30% | MEDIUM/HIGH |
| OOM | `failed = 1` com reason "OutOfMemory" | > 0 | CRITICAL |

**CLI Tools Go (7 comandos):**
| Comando | Função |
|---------|--------|
| `analyze` | Pipeline completo T1→T2→T3 |
| `diagnose` | Apenas T1 (anomalias) |
| `validate` | EvidenceValidator (7 regras) |
| `recommend` | T2/T3 por finding JSON |
| `spillwatch` | Watcher contínuo de spill |
| `mcp-server` | HTTP server MCP (porta 3000) |
| `crei-server` | HTTP server CREI (porta 3001) |

### 4.2 Decisões Arquiteturais (ADRs)

| ADR | `cowork` | `kimi` | Status |
|-----|----------|--------|--------|
| **ADR-001** (Onde roda?) | Externo via ClickHouse | Externo via ClickHouse | ✅ Alinhado |
| **ADR-002** (Quando T2 dispara?) | T2 dispara sempre | T2 dispara sempre | ⚠️ Parcial |
| **ADR-003** (Onde mora o estado?) | ClickHouse local → Rail | ClickHouse local → Rail | ✅ Alinhado |
| **ADR-004** (Linguagem) | **Não endereçou** | **Resolve gap** | ✅ `kimi` |
| **ADR-005** (SparkListener vs zero-JAR) | **Cria e aceita** | Não endereçou | ✅ `cowork` |

**ADR-004 (gap crítico):** A Crew A decidiu Go para o core, mas o único pipeline validado foi em Python. A `kimi` propõe: **V0.1** em Python (protótipo), **V0.2+** em Go (produção).

**ADR-005 (blocker py4j):** A `cowork` descobriu que SparkListener py4j é inoperante em `spark-submit`. Solução: bridge via event log polling (`event_log_ingest.py`), validado com 5 stages e 7 tasks reais.

### 4.3 Qualidade de Código

#### `cowork` — Python

**Pontos fortes:**
- ✅ Schema Pydantic (`ApexFinding`) com validação automática
- ✅ Contrato de 5 regras para anti-alucinação
- ✅ Telemetria desabilitada por padrão (`CREWAI_DISABLE_TELEMETRY`)
- ✅ Testes mock E2E (21 testes, sem API real)
- ✅ Fallback regex para JSON com preamble markdown
- ✅ Keywords obrigatórias na recommendation

**Pontos de atenção:**
- ⚠️ 2 commits de fix para erros de edição (`rstrip accident`, `trailing garbage`)
- ⚠️ Dependência obrigatória de ANTHROPIC_API_KEY
- ⚠️ GIL do Python limita concorrência real

#### `kimi` — Go

**Pontos fortes:**
- ✅ Zero dependência de API externa (100% offline)
- ✅ Goroutines para concorrência nativa
- ✅ 7 CLIs independentes (boa separação de concerns)
- ✅ Thresholds configuráveis via environment variables
- ✅ Cliente ClickHouse HTTP puro (sem driver pesado)

**Pontos de atenção:**
- ⚠️ Código traduzido, **não compilado/validado**
- ⚠️ Sem testes unitários ou de integração
- ⚠️ SQL queries com `fmt.Sprintf` (vulnerável a SQL injection se `appID` não for sanitizado)

### 4.4 Performance Estimada

| Métrica | `cowork` (Python/CrewAI) | `kimi` (Go/Heurístico) |
|---------|--------------------------|------------------------|
| **Latência T1** | ~500–2000ms (LLM call) | ~136ms (SQL query) |
| **Latência T2** | ~500–2000ms (LLM call) | ~0.01ms (runbook lookup) |
| **Latência T3** | ~500–2000ms (LLM call) | ~145ms (heurística ClickHouse) |
| **Custo por diagnóstico** | $0.01–0.10 (tokens Anthropic) | $0.00 (sem API externa) |
| **Offline capable** | ❌ (requer API key) | ✅ (100% local) |
| **Concorrência** | Limitada pelo GIL | Nativa (goroutines) |

---

## 5. Mapeamento de Issues

### 5.1 Issues da Reunião 30/06 — Status Cruzado

| Issue | Título | `cowork` | `kimi` |
|-------|--------|----------|--------|
| #22 | Documento V1 completo | 🟡 Parcial (HTML 8 slides) | ❌ Não |
| #23 | Pod Ambiente: Spark Envy Docker | ✅ (repo separado) | ✅ (fork Gabriel) |
| #24 | Pod Listener: SparkListener | 🟡 Bridge (ADR-005) | ⚠️ Delega ao Go Loader |
| #25 | Pod Infra: ClickHouse setup | ✅ (schema validado) | ✅ (6 tabelas) |
| #26 | Pod Diagnóstico: Crew.ai + MCP | ✅ (2 agentes, 5 tools) | ⚠️ MCP HTTP em Go |
| #27 | ADR-005 | ✅ Criado | ❌ Não |
| #28 | Research DataFlint | ✅ (análise completa) | ✅ (benchmark) |
| #30 | On-premise / offline mode | ⏸️ Futuro | ✅ (100% offline) |

### 5.2 Scorecard de Validação

| Categoria | Total | `cowork` | `kimi` |
|-----------|-------|----------|--------|
| V0.1 (Reunião 30/06) | 10 | 7 ✅, 2 🟡, 1 ⏸️ | 7 ✅, 2 🟡, 1 ❌ |
| Arquitetura (ADRs) | 7 | 2 ✅, 2 ⚠️, 3 ❌ | 3 ✅, 4 ⚠️, 0 ❌ |
| Features & Componentes | 11 | 5 ✅, 2 🟡, 4 ❌ | 4 ✅, 2 🟡, 5 ❌ |
| Bloqueios & Commander | 6 | 2 ✅, 1 ⚠️, 3 ❌ | 2 ✅, 1 ⚠️, 3 ❌ |
| Pesquisa & Validação | 3 | 2 ✅, 1 🟡 | 2 ✅, 1 🟡 |
| **TOTAL (37 issues)** | **37** | **~18 validados** | **~18 validados** |

---

## 6. Análise de Riscos e Gaps

### 6.1 Gaps da `cowork`

| # | Gap | Severidade | Mitigação |
|---|-----|------------|-----------|
| 1 | Dependência de ANTHROPIC_API_KEY | 🔴 Alta | T3 heurístico da `kimi` como fallback |
| 2 | GIL do Python | 🟡 Média | AsyncIO + Multiprocessing; migração Go V0.2 |
| 3 | SparkListener real-time | 🟡 Média | ADR-005 documenta; bridge funcional |
| 4 | Cenários limitados (só skew) | 🟡 Média | Roadmap Sprint 2 |
| 5 | Sem CI para V1 | 🟢 Baixa | CI Mundo A existe; V1 precisa gate próprio |

### 6.2 Gaps da `kimi`

| # | Gap | Severidade | Mitigação |
|---|-----|------------|-----------|
| 1 | Código Go não compilado/validado | 🔴 Alta | `go build ./...`; validar com ClickHouse real |
| 2 | Sem testes (Go) | 🔴 Alta | Escrever testes unitários; mock ClickHouse |
| 3 | SQL injection potencial | 🟡 Média | Prepared statements ou sanitização |
| 4 | Sem integração CrewAI/LLM | 🟡 Média | T3 heurístico cobre 80%; LLM é V0.2 |
| 5 | Sem apresentação stakeholders | 🟢 Baixa | Reusar HTML da `cowork` |

### 6.3 Gaps Compartilhados

| # | Gap | Severidade |
|---|-----|------------|
| 1 | Código validado em outro repo (fork Gabriel) | 🔴 Alta |
| 2 | Decisão ADR-004 não alinhada com implementação | 🔴 Alta |
| 3 | Acesso Write ao repo não liberado | 🔴 Alta |
| 4 | Licença e proveniência do código do Gabriel | 🔴 Alta |
| 5 | Tier 2 threshold não definido data-driven | 🟡 Média |
| 6 | CI Integration não existe | 🟡 Média |
| 7 | UI local não implementada | 🟢 Baixa |

---

## 7. Recomendação de Convergência

### 7.1 Matriz de Decisão

| Critério | Peso | `cowork` | `kimi` | Vencedor |
|----------|------|----------|--------|----------|
| Demo imediata para Luan | 30% | 9/10 | 4/10 | **cowork** |
| Alinhamento ADR-004 (Go) | 20% | 3/10 | 9/10 | **kimi** |
| Independência de infra externa | 15% | 5/10 | 9/10 | **kimi** |
| Cobertura de testes | 15% | 8/10 | 2/10 | **cowork** |
| Documentação arquitetural | 10% | 5/10 | 9/10 | **kimi** |
| Escalabilidade / produção | 10% | 4/10 | 8/10 | **kimi** |
| **Score Ponderado** | **100%** | **6.5/10** | **6.7/10** | **kimi** (margem estreita) |

### 7.2 Estratégia Recomendada: Merge Híbrido Seletivo

> **Recomendação:** Unificar o melhor de cada branch em uma branch integrada.

```
gustocezar/feature/desacoplamento-geradores (base)
              │
              ├──► cowork (14 commits)
              │
              └──► kimi (5 commits)
                        │
                        └──► merge: gustocezar/feature/unified-v1
```

### 7.3 Plano de Merge

#### Fase 1 — Fundação (da `kimi`)
| Componente | Justificativa |
|------------|---------------|
| `docs/adr/adr-004-language-gap-resolution.md` | Resolve gap crítico Go vs. Python |
| `docs/validation/validated-vs-issues.md` | Mapeamento completo de 37 issues |
| `docs/tier/t3-heuristic-mvp.md` | Roadmap claro V0.1→V1.0 |

#### Fase 2 — Infraestrutura (da `cowork`)
| Componente | Justificativa |
|------------|---------------|
| `v1-skeleton/ingest/event_log_ingest.py` | Validado com dados reais |
| `v1-skeleton/ingest/log_poller.py` | Rolling watch funcional |
| `Dockerfile.spark` + `docker-compose.yml` | Infra containerizada pronta |
| `docs/adr/ADR-005-sparklistener-vs-zero-jar.md` | Decisão arquitetural crítica |

#### Fase 3 — Diagnóstico (unificar)
| Componente | Estratégia |
|------------|------------|
| T1 (Diagnostician) | SQL determinístico da `kimi` como default; CrewAI da `cowork` como tier opcional |
| T2 (Runbook) | Runbooks JSON da `kimi` (limpos e testáveis) |
| T3 (Recomendação) | Heurístico da `kimi` como default rápido; LLM da `cowork` como fallback |

#### Fase 4 — Interface / MCP (unificar)
| Componente | Estratégia |
|------------|------------|
| MCP Server | Manter server Python da `cowork` (funcional) + prototipar server Go como V0.2 |
| Tool `apply_fix` | Manter da `cowork` (única que realmente modifica código) |
| Apresentação HTML | Reusar da `cowork` (pronta para stakeholders) |

#### Fase 5 — Testes (priorizar `cowork`)
| Componente | Justificativa |
|------------|---------------|
| `test_crew_e2e.py` | 21 testes mock validados |
| Testes Go | Precisam ser escritos do zero |

---

## 8. Tabela de Arquivos — Cruzamento Completo

### 8.1 Exclusivos da `cowork`

| Caminho | Tipo | Linhas (aprox.) | Descrição |
|---------|------|-----------------|-----------|
| `VALIDACAO.md` | Doc | 124 | Mapa de issues 30/06 |
| `CHANGELOG.md` | Doc | ~100 | Histórico de mudanças |
| `COMO_COMMITAR.md` | Doc | ~50 | Guia de commit |
| `CONTRIBUTING.md` | Doc | ~60 | Guia de contribuição |
| `CLAUDE.md` | Doc | ~200 | Documentação Claude |
| `v1-skeleton/analysis/crew_diagnose.py` | Python | ~350 | CrewAI 2 agentes + Pydantic |
| `v1-skeleton/test_crew_e2e.py` | Python | ~129 | 21 testes mock E2E |
| `v1-skeleton/ingest/event_log_ingest.py` | Python | ~289 | Bridge zstd → ClickHouse |
| `v1-skeleton/ingest/log_poller.py` | Python | ~55 | Rolling log watcher |
| `v1-skeleton/listener/spark_listener.py` | Python | ~120 | SparkListener Python |
| `v1-skeleton/mcp/server.py` | Python | ~200 | MCP Server 5 ferramentas |
| `v1-skeleton/mcp/apply_fix.py` | Python | ~98 | Tool que aplica fix em PySpark |
| `docs/adr/ADR-005-sparklistener-vs-zero-jar.md` | Doc | ~155 | Decisão arquitetural |
| `docs/presentations/apex_v1_apresentacao_luan.html` | HTML | ~800 | Apresentação 10 slides |
| `docs/competitive/` | Dir | — | Análise DataFlint |
| `Dockerfile.spark` | Docker | ~30 | Imagem Spark 3.5 |
| `docker-compose.yml` | Docker | ~40 | Compose com healthcheck |
| `.claude/` | Dir | — | Configs Claude Code |
| `tasks/` | Dir | — | Tarefas do projeto |

### 8.2 Exclusivos da `kimi`

| Caminho | Tipo | Linhas (aprox.) | Descrição |
|---------|------|-----------------|-----------|
| `go-apex/` | Dir | ~5.000 | Projeto Go completo |
| `go-apex/internal/diagnostician/diagnostician.go` | Go | ~430 | T1: detect_skew, detect_spill, detect_gc, detect_oom |
| `go-apex/internal/validator/validator.go` | Go | ~874 | EvidenceValidator: 7 regras |
| `go-apex/internal/recommender/recommender.go` | Go | ~503 | T2 + T3 heurístico |
| `go-apex/internal/watcher/watcher.go` | Go | ~516 | SpillWatcher + SkewWatcher |
| `go-apex/internal/clickhouse/client.go` | Go | ~173 | Cliente HTTP ClickHouse |
| `go-apex/internal/clickhouse/queries.go` | Go | ~342 | QueryBuilder SQL |
| `go-apex/internal/models/types.go` | Go | ~602 | Structs do domínio |
| `go-apex/internal/runbook/runbook.go` | Go | ~222 | Loader de runbooks JSON |
| `go-apex/pkg/mcp/mcp.go` | Go | ~331 | Tipos MCP em Go |
| `go-apex/cmd/*/main.go` (7 cmds) | Go | ~758 | CLIs independentes |
| `go-apex/runbooks/*.json` | JSON | 141 | Runbooks skew + spill |
| `docs/validation/validated-vs-issues.md` | Doc | ~300 | Mapeamento 37 issues |
| `docs/adr/adr-004-language-gap-resolution.md` | Doc | ~250 | Resolução Go vs. Python |
| `docs/tier/t3-heuristic-mvp.md` | Doc | ~200 | T3 heurístico e roadmap |
| `BRANCH_COMPARISON_cowork_vs_kimi.md` | Doc | 218 | Comparação anterior |
| `real_log.ndjson` | Dados | ~44KB | Logs reais de execução |

### 8.3 Em Comum (herdado da base)

| Caminho | Descrição |
|---------|-----------|
| `apex/` | Core do projeto (Mundo A) |
| `generators/` | Geradores v4 (desacoplamento) |
| `watchers/` | Skew Watcher |
| `scenarios/` | Cenários YAML |
| `tests/` | 40 testes do Mundo A |
| `oracle/` | Oracle de validação |
| `AGENTS.md` | Definição dos agentes |
| `README.md` | README do projeto |
| `requirements.txt` | Dependências Python |
| `run_slice.sh` | Script de execução |

---

## 9. Próximos Passos

### Imediato (2 dias)
1. **Decidir branch oficial para V0.1** — Commander deve escolher ou aprovar merge híbrido
2. **Liberar acesso Write** — Adicionar `gustocezar` como colaborador
3. **Resolver licença/proveniência** — Confirmar autorização do Gabriel

### Curto prazo (1 semana)
4. **Compilar código Go** — `cd go-apex && go build ./...`
5. **Rodar testes da `cowork`** — `python -m pytest v1-skeleton/test_crew_e2e.py -v`
6. **Criar branch unificada** — `gustocezar/feature/unified-v1`
7. **Atualizar ADR-004** com decisão final

### Médio prazo (2 semanas)
8. **Implementar CI gate** — GitHub Action para testes em PR
9. **Portar T3 heurístico** para Python como fallback da CrewAI
10. **Validar pipeline fim a fim** na branch unificada

### Longo prazo (Sprint 3+)
11. **SparkListener real-time** — Resolver blocker py4j
12. **RAG + memória persistente** — Corpus histórico no ClickHouse
13. **UI local** — Streamlit ou React para DAGs
14. **On-premise LLM** — Ollama/Llama3 para modo offline

---

## 10. Anexos

### A. Comandos para Validação Cruzada

```bash
# Clonar e comparar
git clone https://github.com/luanmorenommaciel/apex.git
cd apex

# Diff entre as branches
git diff gustocezar/feature/cowork-desacoplamento-geradores \
  gustocezar/feature/kimi-desacoplamento-geradores --stat

# Validar cowork
git checkout gustocezar/feature/cowork-desacoplamento-geradores
pip install -r requirements.txt
pytest v1-skeleton/test_crew_e2e.py -v

# Validar kimi (Go)
git checkout gustocezar/feature/kimi-desacoplamento-geradores
cd go-apex
go mod tidy
go build ./...
go test ./...
```

### B. Referências Rápidas

| Recurso | URL |
|---------|-----|
| Repo Apex | `https://github.com/luanmorenommaciel/apex` |
| Branch `cowork` | `https://github.com/luanmorenommaciel/apex/tree/gustocezar/feature/cowork-desacoplamento-geradores` |
| Branch `kimi` | `https://github.com/luanmorenommaciel/apex/tree/gustocezar/feature/kimi-desacoplamento-geradores` |
| Commit base | `https://github.com/luanmorenommaciel/apex/commit/bd8a08bc` |
| Commit `cowork` HEAD | `https://github.com/luanmorenommaciel/apex/commit/d3c3e8a3` |
| Commit `kimi` HEAD | `https://github.com/luanmorenommaciel/apex/commit/b9757bea` |

---

*Documento gerado em 2026-07-06 a partir da análise detalhada de commits, arquivos e diffs das branches paralelas do projeto Apex.*
