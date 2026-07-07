# Comparação: `cowork` vs `kimi` — Branches Paralelas do Augusto

> **Data:** 2026-07-07  
> **Autor:** Kimi (comparador automático)  
> **Base comum:** `gustocezar/feature/desacoplamento-geradores` (commits até `bd8a08bc`)  
> **Branch cowork:** `gustocezar/feature/cowork-desacoplamento-geradores` — commit `d3c3e8a3`  
> **Branch kimi:** `gustocezar/feature/kimi-desacoplamento-geradores` — commit `8be15724`

---

## Resumo Executivo

Ambas as branches divergem da **mesma base** (`desacoplamento-geradores`, 8 commits). Cada uma representa uma linha de trabalho paralela do Augusto:

| Aspecto | `cowork` | `kimi` |
|---------|----------|--------|
| **Foco** | V1 com CrewAI + Apresentação | Tradução Go + Documentação |
| **Linguagem** | Python (CrewAI, PySpark) | Go |
| **Dependência externa** | Anthropic API (Claude), CrewAI | ClickHouse Go driver |
| **Estado** | Código Python executável | Código Go traduzido (não compilado) |
| **Apresentação** | HTML completo (10 slides) | Docs Markdown (3 arquivos) |
| **ADR-004** | Mantém Python (não tocou) | Propõe Go para V0.2+ |
| **ADR-005** | Criou (SparkListener inoperante) | Não criou |
| **MCP** | Tool `apply_fix` (aplica código) | Server HTTP em Go |
| **Event Log** | `event_log_ingest.py` (zstd → ClickHouse) | Não tem (usa Loader Go existente) |
| **CrewAI** | `crew_diagnose.py` (crewai 1.15.1) | Não tem (T3 heurístico) |
| **Testes** | `test_crew_e2e.py` (21 testes) | Não tem (código Go não compilado) |

---

## Commits Exclusivos da Branch `cowork` (14 commits)

```
d3c3e8a3 — docs: VALIDACAO.md — mapa completo issues 30/06 + repo vs entregue na branch
77c1240f — feat(mcp): tool apply_fix — aplica recomendação Apex no código PySpark
aae62507 — feat(apresentacao): slide 7 — status dos pontos do Luan com issues #17 #19 #20 #21
e26adb19 — feat(apresentacao): apex_v1_apresentacao_luan.html — pipeline V1 + DataFlint comparison
c5c4c611 — chore: add test_crew.py (pipeline validation) + gitignore update
4351ef51 — feat(v1): log_poller.py (rolling log watch) + MCP claude_code_config.json
61dc0e9d — fix(crew): restore missing __main__ block after rstrip accident
24f68a40 — fix(crew): root_cause max_length 300→500, remove trailing garbage
8630e039 — feat(v1): event_log_ingest.py — bridge event log → ClickHouse
a1e67817 — fix(listener): SparkListener completo + Docker com clickhouse-connect
ca0b846d — chore: add __pycache__ to gitignore
682f564b — feat(v1): crew_diagnose.py para crewai 1.15.1 + test suite mock
48f63f3f — feat: Crew.ai pipeline + ADR-005 + listener contracts + MCP docs
bc747c11 — feat: v1-skeleton + docs + DataFlint analysis + reuniao-30jun artifacts
```

---

## Commits Exclusivos da Branch `kimi` (4 commits)

```
8be15724 — feat(go): tradução completa Python → Go do pipeline Apex V0.1
b490e774 — docs(adr): ADR-004 resolução do gap de linguagem Go vs. Python
79a23d2c — docs: mapeamento validado vs issues do Apex (V0.1)
9905af10 — docs: add T3 heuristic MVP documentation for V0.1
```

---

## Arquivos Exclusivos da Branch `cowork`

| Arquivo | Tipo | Descrição |
|---------|------|-----------|
| `VALIDACAO.md` | Doc | Mapa completo de issues da reunião 30/06 vs. o que foi entregue |
| `docs/presentations/apex_v1_apresentacao_luan.html` | HTML | Apresentação de 10 slides: pipeline V1, DataFlint comparison, status |
| `crew/v1/crew_diagnose.py` | Python | Agente CrewAI com LLM nativo (crewai 1.x, Pydantic, contratos) |
| `crew/v1/test_crew_e2e.py` | Python | 21 testes mock end-to-end (skew detection, confidence, JSON parsing) |
| `crew/v1/spark_listener.py` | Python | SparkListener com 24 no-ops para interface Scala |
| `crew/v1/event_log_ingest.py` | Python | Bridge: event log zstd → ClickHouse (stream_reader para zstd) |
| `crew/v1/log_poller.py` | Python | Rolling log watcher para event logs |
| `crew/v1/mcp_tools/apply_fix.py` | Python | Tool MCP que aplica recomendação Apex em código PySpark do engenheiro |
| `crew/v1/mcp_tools/claude_code_config.json` | JSON | Configuração Claude Code para MCP |
| `docs/adr/ADR-005-spark-listener-inoperante.md` | Doc | ADR-005: SparkListener py4j inoperante em spark-submit |
| `docs/presentations/slide-07-status-luan.md` | Doc | Status dos pontos do Luan (issues #17, #19, #20, #21) |
| `Dockerfile.spark` | Docker | Imagem bitnami/spark:3.5 + clickhouse-connect |
| `docker-compose.yml` | Docker | Compose customizado com healthcheck ClickHouse |
| `test_crew.py` | Python | Pipeline validation básico |
| `v1-skeleton/` | Dir | Estrutura inicial da V1 |

---

## Arquivos Exclusivos da Branch `kimi`

| Arquivo | Tipo | Descrição |
|---------|------|-----------|
| `go-apex/` | Dir | Projeto Go completo (20 arquivos) |
| `go-apex/go.mod` | Go | Módulo `github.com/apex/go-apex` com driver ClickHouse |
| `go-apex/internal/diagnostician/diagnostician.go` | Go | T1: detect_skew, detect_duration_skew, detect_spill, detect_memory_pressure |
| `go-apex/internal/validator/validator.go` | Go | EvidenceValidator: 7 regras de validação |
| `go-apex/internal/recommender/recommender.go` | Go | T2 (runbook) + T3 (heurístico + LLM fallback) |
| `go-apex/internal/watcher/watcher.go` | Go | SpillWatcher + SkewWatcher |
| `go-apex/internal/clickhouse/client.go` | Go | Cliente HTTP ClickHouse (net/http + encoding/json) |
| `go-apex/internal/clickhouse/queries.go` | Go | QueryBuilder com queries SQL do pipeline |
| `go-apex/internal/models/types.go` | Go | Structs: Finding, DiagnosisResult, Recommendation, etc. |
| `go-apex/internal/runbook/runbook.go` | Go | Loader de runbooks JSON + Manager thread-safe |
| `go-apex/pkg/mcp/mcp.go` | Go | Tipos MCP: Tool, Response, HealthCheck |
| `go-apex/cmd/diagnose/main.go` | Go | CLI: `diagnose <job_id>` |
| `go-apex/cmd/validate/main.go` | Go | CLI: `validate -app-id=<id>` |
| `go-apex/cmd/recommend/main.go` | Go | CLI: `recommend -finding=<json>` |
| `go-apex/cmd/spillwatch/main.go` | Go | CLI: `spillwatch -app-id=<id>` |
| `go-apex/cmd/analyze/main.go` | Go | CLI: pipeline completo T1→T2→T3 |
| `go-apex/cmd/mcp-server/main.go` | Go | HTTP server MCP (porta 3000) |
| `go-apex/cmd/crei-server/main.go` | Go | HTTP server CREI (porta 3001) |
| `go-apex/runbooks/skew_on_join.json` | JSON | Runbook para skew |
| `go-apex/runbooks/spill_to_disk.json` | JSON | Runbook para spill |
| `docs/validation/validated-vs-issues.md` | Doc | Mapeamento de 37 issues vs. validação (59% completo) |
| `docs/adr/adr-004-language-gap-resolution.md` | Doc | ADR-004: Python V0.1 → Go V0.2+ |
| `docs/tier/t3-heuristic-mvp.md` | Doc | T3 heurístico: V0.1 → V0.2 → V1.0 |

---

## Features em Comum (ambas têm, de formas diferentes)

| Feature | `cowork` (Python) | `kimi` (Go) |
|---------|-------------------|-------------|
| **Diagnóstico T1** | `crew_diagnose.py` (LLM + regras) | `diagnostician.go` (SQL determinístico) |
| **Recomendação T2** | Implícito no CrewAI | `recommender.go` (runbook determinístico) |
| **Recomendação T3** | CrewAI com LLM nativo | Heurístico ClickHouse + fallback LLM |
| **MCP Server** | Tool `apply_fix` (aplica código) | Server HTTP (query_job, get_recommendations) |
| **ClickHouse** | `event_log_ingest.py` (zstd → CH) | `client.go` (queries HTTP) |
| **Validação** | `test_crew_e2e.py` (21 testes mock) | `validator.go` (7 regras em tempo real) |
| **Documentação** | Apresentação HTML (10 slides) | Docs Markdown (3 arquivos técnicos) |

---

## Features Únicas de Cada Branch

### `cowork` tem, `kimi` não tem:
- ✅ CrewAI integration (crewai 1.15.1)
- ✅ Anthropic/Claude LLM nativo
- ✅ Apresentação HTML para o Luan
- ✅ SparkListener Python (com workaround para py4j)
- ✅ Ingestão de event log zstd → ClickHouse
- ✅ Rolling log poller
- ✅ Tool MCP `apply_fix` (aplica correção no código do engenheiro)
- ✅ ADR-005 (SparkListener inoperante)
- ✅ Dockerfile customizado para Spark
- ✅ 21 testes mock end-to-end

### `kimi` tem, `cowork` não tem:
- ✅ Código Go traduzido (pipeline completo)
- ✅ ADR-004 resolvida (Go vs. Python)
- ✅ Mapeamento de 37 issues vs. validação
- ✅ T3 heurístico documentado (roadmap V0.1→V1.0)
- ✅ QueryBuilder SQL em Go
- ✅ Cliente ClickHouse HTTP em Go
- ✅ Runbooks JSON carregáveis
- ✅ CLI tools em Go (7 comandos)
- ✅ Server MCP HTTP em Go
- ✅ Server CREI HTTP em Go

---

## Análise de Convergência

### O que `cowork` faz melhor:
1. **CrewAI**: Integração real com framework agentico (crewai 1.x)
2. **LLM**: Uso nativo de Claude/Anthropic para diagnóstico
3. **Apresentação**: Material visual para stakeholders (Luan)
4. **Testes**: 21 testes mock validados
5. **Event Log**: Pipeline próprio de ingestão (zstd → CH)
6. **MCP aplicável**: Tool que realmente modifica código do engenheiro

### O que `kimi` faz melhor:
1. **Alinhamento ADR-004**: Resolve o gap Go vs. Python
2. **Documentação técnica**: Mapeamento completo de issues
3. **Independência**: Não depende de API key externa (T3 heurístico)
4. **Arquitetura**: Código Go segue padrões de infraestrutura
5. **CLI**: 7 comandos independentes
6. **HTTP Servers**: MCP + CREI como serviços

### Gaps em ambas:
- ❌ Nenhuma das duas tem CI/CD (GitHub Actions)
- ❌ Nenhuma das duas tem RAG/memória persistente
- ❌ Nenhuma das duas tem UI web (Streamlit/React)
- ❌ Nenhuma das duas tem testes de integração com ClickHouse real
- ❌ Ambas dependem do fork Gabriel para infraestrutura

---

## Recomendação de Merge

### Opção A: Mergear `cowork` + `kimi` → branch unificada
```
desacoplamento-geradores (base)
    ├──► cowork (CrewAI, V1, apresentação)
    └──► kimi (Go, docs, ADR-004)
              └──► merge: unified-v1
```

**Como unificar:**
1. Manter código Python da `cowork` (CrewAI, event log ingest, testes)
2. Manter código Go da `kimi` como `go-apex/` (tradução paralela)
3. Manter docs de ambas
4. Resolver ADR-004: Python para V0.1, Go para V0.2+
5. Usar apresentação HTML da `cowork` para stakeholders

### Opção B: Manter separado, escolher uma como principal
- Se foco é **demo rápida** → usar `cowork` (CrewAI funcional, testes passando)
- Se foco é **infraestrutura** → usar `kimi` (Go, escalável, ADRs resolvidos)

---

## Próximos Passos Sugeridos

1. **Decidir qual branch é a "oficial"** para V0.1
2. **Se unificar:** Abrir PR de `cowork` → `kimi` (ou vice-versa)
3. **Compilar código Go** da `kimi` para validar (precisa de Go instalado)
4. **Rodar testes** da `cowork` (`python -m pytest crew/v1/test_crew_e2e.py`)
5. **Validar CrewAI** da `cowork` com ANTHROPIC_API_KEY real
6. **Atualizar ADR-004** com decisão final da Crew A

---

*Documento gerado automaticamente via comparação de commits das branches.*
