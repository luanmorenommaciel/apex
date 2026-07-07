# Proposta de Unificação — Branches `cowork` × `kimi`

> **Artefato:** `docs/unificacao-proposta.md`  
> **Versão:** 1.0  
> **Data:** 2026-07-06  
> **Autor:** Augusto Cezar (ambas as vertentes)  
> **Branch-base:** `gustocezar/feature/desacoplamento-geradores` (8 commits do slice v4 de `skew_on_join`)  
> **Branches a unificar:**
> - `gustocezar/feature/cowork-desacoplamento-geradores` (14 commits, HEAD `d3c3e8a3`)
> - `gustocezar/feature/kimi-desacoplamento-geradores` (5 commits, HEAD `8be15724`)

---

## 1. Resumo Executivo

Este documento propõe a **unificação ordenada** de duas vertentes de trabalho desenvolvidas em paralelo pelo mesmo autor (Augusto Cezar) a partir do mesmo ponto de partida — o slice v4 de desacoplamento de geradores (`skew_on_join_30x`).

| Vertente | Foco Principal | Commits | HEAD |
|---|---|---|---|
| `cowork` | V1 produtiva: CrewAI, SparkListener, MCP, apresentação, testes | 14 | `d3c3e8a3` |
| `kimi` | V0.1 fundacional: tradução Go, documentação, resolução ADR-004 | 5 | `8be15724` |

**Não há conflito de autoridade** — as duas vertentes são complementares, não concorrentes. A `cowork` avançou o produto em direção à V1 (runtime Python + CrewAI + MCP). A `kimi` consolidou a fundação (documentação, contratos, tradução Go, resolução de dívida arquitetural).

**Proposta central:** manter o runtime Python como **V1 imediata** (protótipo validável e demoável), absorver a documentação e os contratos da `kimi` como **governança compartilhada**, e usar a tradução Go como **base para V2** (produção).

---

## 2. O Que Cada Branch Entregou

### 2.1 Branch `cowork` (V1 — Produto)

#### Arquitetura entregue
```
[Spark Envy] → [SparkListener] → [ClickHouse] → [Crew.ai] → [MCP] → [IDE]
```

#### Componentes concretos

| Componente | Arquivo(s) | Status |
|---|---|---|
| SparkListener Python | `v1-skeleton/listener/spark_listener.py` | ✅ Funcional (bridge via event log — ADR-005) |
| Ingestão ClickHouse | `v1-skeleton/ingest/event_log_ingest.py` | ✅ Validado: 5 stages, 7 tasks inseridos |
| Poller automático | `v1-skeleton/ingest/log_poller.py` | ✅ Rolling watch a cada 15s |
| Crew.ai Diagnóstico | `v1-skeleton/analysis/crew_diagnose.py` | ✅ 2 agents (MetricsAnalyzer + RecommendationWriter) |
| MCP Server | `v1-skeleton/mcp/server.py` | ✅ 5 tools (incl. `apply_fix`) |
| Testes E2E | `v1-skeleton/test_crew_e2e.py` | ✅ 21 testes passando |
| Apresentação V1 | `docs/presentations/apex_v1_apresentacao_luan.html` | ✅ 8 slides com DataFlint comparison |
| Docker Compose | `v1-skeleton/docker-compose.yml` | ✅ Spark 3.5 + ClickHouse + healthcheck |

#### Decisões arquiteturais formalizadas
- **ADR-005:** SparkListener in-process para V1 (aceita zero-JAR como fallback futuro)
- **ADR-005 update:** py4j inoperante em `spark-submit` → bridge via event log polling

#### Issues cobertas
| Issue | Status |
|---|---|
| #22 — Documento V1 completo | 🟡 Parcial (apresentação entregue) |
| #23 — Spark Envy Docker | ✅ Existe (repo `dataship-spark-plat-v0`) |
| #24 — SparkListener in-process | 🟡 Bridge (event log polling funcional) |
| #25 — ClickHouse setup + schema | ✅ Feito |
| #26 — Crew.ai + MCP | ✅ Feito |
| #27 — ADR-005 | ✅ Formalizado |
| #28 — Research DataFlint | ✅ Completo |

---

### 2.2 Branch `kimi` (V0.1 — Fundação)

#### Arquitetura entregue
```
[Scenario YAML] → [Go Loader] → [ClickHouse] → [Go Watcher/Analyzer] → [Finding]
```

#### Componentes concretos

| Componente | Arquivo(s) | Status |
|---|---|---|
| Tradução Go do pipeline | `go-apex/` | ✅ Completa (cmd: analyze, diagnose, mcp-server, recommend, spillwatch, validate) |
| Modelos Go | `go-apex/internal/models/` | ✅ Estruturas de dados portadas |
| Watcher Go | `go-apex/internal/watcher/` | ✅ Portado de Python |
| Diagnostician Go | `go-apex/internal/diagnostician/` | ✅ Portado de Python |
| Recommender Go | `go-apex/internal/recommender/` | ✅ Portado de Python |
| ClickHouse client Go | `go-apex/internal/clickhouse/` | ✅ Portado de Python |
| MCP Server Go | `go-apex/pkg/mcp/` | ✅ Portado de Python |
| Runbooks | `go-apex/runbooks/` | ✅ Criados |
| Documentação v4 | `docs/` (17 arquivos) | ✅ Completa |

#### Decisões arquiteturais formalizadas
- **ADR-004 resolução:** Go para core de produção (V2+), Python para prototipação e LLM (V1)
- **ADR-004 gap:** Pipeline validado fim a fim está em Python → aceitável para V0.1/V1

#### Documentação produzida
| Documento | Uso |
|---|---|
| `docs/team-validation-guide.md` | Material didático para Crew A |
| `docs/adr-review-drafts.md` | Leitura prévia das ADRs antes de comentar |
| `docs/adr/adr-004-language-gap-resolution.md` | Resolução do gap Go vs. Python |
| `docs/apex-v4-lineage.md` | História da melhoria e relação com issues |
| `docs/architecture/validation-evidence-flow.md` | Fluxo canonico de validação |
| `docs/architecture/event-log-observability-boundary.md` | Limites do event log |
| `docs/architecture/apex-solution-drilldown.md` | Visão L0-L5 completa |
| `docs/specs/skew-slice-v4.md` | Especificação técnica do slice |
| `docs/playbooks/skew-slice-v4.md` | Operação e verificação |
| `docs/coverage/apex-coverage-report-v1.md` | Inventário de cobertura |

---

## 3. Matriz de Sobreposição, Gaps e Conflitos

### 3.1 Sobreposições (merge trivial)

| Área | `cowork` | `kimi` | Ação |
|---|---|---|---|
| ADR-005 (SparkListener) | ✅ Formalizado | ❌ Não tocado | Manter da `cowork` |
| Docs de apresentação | ✅ 8 slides HTML | ❌ Não tocado | Manter da `cowork` |
| Testes E2E CrewAI | ✅ 21 testes | ❌ Não tocado | Manter da `cowork` |
| Tradução Go | ❌ Não existe | ✅ Completa | Manter da `kimi` |
| ADR-004 resolução | ❌ Não tocado | ✅ Formalizado | Manter da `kimi` |
| Documentação v4 | 🟡 Básica | ✅ Extensa | Merge: `kimi` como base, adicionar V1 da `cowork` |
| README.md | 🟡 V1-focada | ✅ V0.1-focada | Unificar em seções distintas |

### 3.2 Gaps (nenhuma branch cobriu)

| Gap | Severidade | Ação proposta |
|---|---|---|
| CI para V1 | 🔴 Alta | Criar `.github/workflows/v1-gate.yml` |
| Falso positivo / baseline no-skew | 🔴 Alta | Criar `scenarios/no_skew_baseline.yaml` |
| SparkListener real-time (sem bridge) | 🟡 Média | Sprint 3: Scala JAR ou py4j fix |
| On-premise / offline mode | 🟡 Média | Sprint 4+: LLM local |
| OTel Collector Go (Guilherme) | 🟡 Média | Coordenar com fork do Gabriel |
| Mais cenários (spill, broadcast_miss, parallelism_collapse) | 🟡 Média | Sprint 2: expandir watchers |
| Schema ClickHouse final para histórico | 🟡 Média | Sprint 2: formalizar tabelas |

### 3.3 Conflitos Potenciais

| Conflito | Natureza | Resolução |
|---|---|---|
| **Linguagem:** Go (ADR-004) vs. Python (V1 funcional) | Estratégico, não técnico | **ADR-004 já resolve:** Python para V0.1/V1 (protótipo), Go para V2+ (produção) |
| **Captura:** SparkListener (V1) vs. zero-JAR (v3) | Arquitetural | **ADR-005 já resolve:** SparkListener para V1, zero-JAR como fallback futuro |
| **MCP Server:** Python (`cowork`) vs. Go (`kimi`) | Implementação | Manter ambos: Python para V1, Go para V2. Contrato MCP é a ponte. |
| **Diagnóstico:** CrewAI (`cowork`) vs. heurístico Go (`kimi`) | Produto | CrewAI para V1 (valor diferenciado), heurístico Go como fallback/offline |

**Conclusão:** Não há conflitos técnicos irresolvíveis. Todas as tensões já foram endereçadas por ADRs formais (004 e 005).

---

## 4. Arquitetura Unificada Proposta

### 4.1 Visão de Produto: Duas Velocidades

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           APEX UNIFICADO                                │
├─────────────────────────────────────────────────────────────────────────┤
│  CAMADA DE EXPERIÊNCIA (V1 — Python + CrewAI)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  MCP Server │  │   CrewAI    │  │  Diagnose   │  │  Apply Fix  │   │
│  │   (Python)  │  │  (Python)   │  │  (Python)   │  │  (Python)   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│         ↑                                                              │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │              CLICKHOUSE (Schema Unificado)                      │   │
│  └────────────────────────────────────────────────────────────────┘   │
│         ↑                                                              │
│  CAMADA DE INFRAESTRUTURA (V0.1 → V2 — Go + Python)                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ Go Loader   │  │ Go Watcher  │  │ Go Spill    │  │ Go Validate │   │
│  │ (Parser)    │  │ (Skew)      │  │  Watch      │  │   (Gate)    │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│         ↑                                                              │
│  ┌─────────────┐  ┌─────────────┐                                      │
│  │  Event Log  │  │  SparkListener │  ← ADR-005: ambos coexistem       │
│  │  (zero-JAR) │  │  (in-process) │     zero-JAR fallback              │
│  └─────────────┘  └─────────────┘                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Princípios da Unificação

1. **Nada descartado:** Todo código funcional de ambas as branches é preservado
2. **Duas velocidades:** V1 (Python/CrewAI) para demo e validação rápida; V2 (Go) para produção
3. **Contrato como rei:** O `scenario.yaml` e o schema MCP são a interface estável entre linguagens
4. **Documentação convergente:** Toda a documentação da `kimi` vira base; docs da `cowork` complementam
5. **Testes unificados:** Gate único que roda testes Python + validação Go (quando aplicável)

### 4.3 Estrutura de Diretórios Unificada Proposta

```
apex/
├── v1/                              # ← da branch cowork
│   ├── listener/
│   ├── ingest/
│   ├── analysis/
│   ├── mcp/
│   ├── schema/
│   ├── jobs/
│   └── tests/
├── go-apex/                         # ← da branch kimi
│   ├── cmd/
│   ├── internal/
│   ├── pkg/
│   └── runbooks/
├── docs/
│   ├── unified/                     # ← NOVO: este artefato + docs de merge
│   ├── v1/                          # ← da cowork (apresentação, ADR-005)
│   ├── v0.1/                        # ← da kimi (specs, playbooks, ADRs)
│   ├── adr/
│   ├── architecture/
│   ├── specs/
│   ├── playbooks/
│   └── coverage/
├── generators/                      # ← base comum (v4)
├── watchers/                        # ← base comum (v4)
├── oracle/                          # ← base comum (v4)
├── scenarios/                       # ← base comum (v4)
├── tests/                           # ← base comum (v4)
└── .github/
    └── workflows/
        ├── scenario-gate.yml        # ← base comum (v4)
        └── v1-gate.yml              # ← NOVO: gate da V1
```

---

## 5. Roadmap de Integração

### Fase 1: Consolidação Documental (1–2 dias)

| Tarefa | Owner | Branch |
|---|---|---|
| Mover `docs/` da `kimi` para estrutura `docs/v0.1/` e `docs/unified/` | Augusto | `kimi` |
| Mover docs da `cowork` (apresentação, ADR-005) para `docs/v1/` | Augusto | `cowork` |
| Criar `docs/unificacao-proposta.md` (este documento) | Augusto | `kimi` |
| Atualizar `README.md` raiz com seções V0.1 e V1 | Augusto | `kimi` |

### Fase 2: Merge de Código Não-Conflitante (2–3 dias)

| Tarefa | Owner | Risco |
|---|---|---|
| Integrar `v1-skeleton/` da `cowork` como `v1/` no destino | Augusto | Baixo — diretório novo |
| Manter `go-apex/` da `kimi` como está | — | Zero — já isolado |
| Unificar `docs/adr/`: ADR-004 (`kimi`) + ADR-005 (`cowork`) | Augusto | Baixo — arquivos distintos |
| Unificar `README.md`: V0.1 (`kimi`) como base + V1 (`cowork`) como adição | Augusto | Médio — precisa reconciliar |

### Fase 3: Resolução de Conflitos (1 dia)

| Conflito | Resolução |
|---|---|
| `README.md` raiz | Usar `kimi` como base (mais completo), adicionar seção "V1 — Produto" com conteúdo da `cowork` |
| `docs/adr-review-drafts.md` | `kimi` tem versão mais completa; adicionar menção a ADR-005 |
| `docs/agentspec-alignment.md` | Manter da `kimi` (mais detalhado) |
| `run_slice.sh` | `kimi` tem versão mais simples; `cowork` não modificou — manter `kimi` |

### Fase 4: Validação (1 dia)

```bash
# 1. Testes v4 (base comum)
python -m pytest tests/test_slice.py -q

# 2. Testes V1 (cowork)
cd v1 && python -m pytest tests/ -q

# 3. Build Go (kimi)
cd go-apex && go build ./...

# 4. Validação documental
# Verificar se todos os links em docs/unified/ estão funcionando
```

### Fase 5: Branch Destino Única (1 dia)

Após validação, a branch `gustocezar/feature/kimi-desacoplamento-geradores` vira a **branch unificada oficial**. A `cowork` pode ser arquivada (não deletada) para preservar histórico.

---

## 6. Decisões Pendentes do Commander

| Decisão | Contexto | Recomendação |
|---|---|---|
| **Aprovar Python para V1?** | ADR-004 propõe Go para core, mas V1 funcional está em Python | ✅ **Aprovar** — V1 é protótipo; Go para V2 |
| **Manter duas branches ou uma?** | Duas branches dão visibilidade, mas fragmentam | 📋 **Merge em `kimi`** após Fase 5; `cowork` vira `archived/cowork-v1` |
| **Prioridade: mais cenários ou Go core?** | Time limitado | 📋 **Mais cenários primeiro** — prova valor do produto; Go é infraestrutura |
| **CI unificado ou separado?** | v4 tem `scenario-gate.yml`; V1 não tem CI | 📋 **CI unificado** — novo `v1-gate.yml` que roda em PRs que tocam `v1/` |

---

## 7. Anexos

### Anexo A: Diff Estatístico entre as Branches

```text
Branch cowork (d3c3e8a3):
  + v1-skeleton/          (novo)
  + docs/presentations/   (novo)
  + docs/adr/ADR-005*     (novo)
  + docs/competitive/     (novo)
  + test_crew.py          (novo)
  ~ README.md             (expandido para V1)
  ~ VALIDACAO.md          (novo)
  ~ CHANGELOG.md          (expandido)

Branch kimi (8be15724):
  + go-apex/              (novo)
  + docs/                 (expandido: 17 arquivos)
  + docs/adr/adr-004*     (novo)
  ~ README.md             (expandido para V0.1)
  ~ docs/apex-v4-lineage.md (expandido)
```

### Anexo B: Rastreamento de Commits

```text
cowork (14 commits desde base):
  bc747c11 feat: v1-skeleton + docs + DataFlint analysis + reuniao-30jun
  48f63f3f feat: Crew.ai pipeline + ADR-005 + listener contracts + MCP docs
  682f564b feat(v1): crew_diagnose.py para crewai 1.15.1 + test suite mock
  ca0b846d chore: add __pycache__ to gitignore
  a1e67817 fix(listener): SparkListener completo + Docker com clickhouse-connect
  8630e039 feat(v1): event_log_ingest.py — bridge event log → ClickHouse
  24f68a40 fix(crew): root_cause max_length 300→500
  61dc0e9d fix(crew): restore missing __main__ block
  4351ef51 feat(v1): log_poller.py + MCP claude_code_config.json
  c5c4c611 chore: add test_crew.py + gitignore update
  e26adb19 feat(apresentacao): apex_v1_apresentacao_luan.html
  aae62507 feat(apresentacao): slide 7 — status dos pontos do Luan
  77c1240f feat(mcp): tool apply_fix
  d3c3e8a3 docs: VALIDACAO.md — mapa completo issues 30/06

kimi (5 commits desde base):
  bd8a08bc feat(apex): validate skew evidence and stage correlation
  9905af10 docs: add T3 heuristic MVP documentation for V0.1
  79a23d2c docs: mapeamento validado vs issues do Apex (V0.1)
  b490e774 docs(adr): ADR-004 resolução do gap de linguagem Go vs. Python
  8be15724 feat(go): tradução completa Python → Go do pipeline Apex V0.1
```

### Anexo C: Referências Cruzadas

| Documento | Branch | Descrição |
|---|---|---|
| `VALIDACAO.md` | `cowork` | Mapa completo de issues da reunião 30/06 |
| `docs/adr/ADR-005-sparklistener-vs-zero-jar.md` | `cowork` | Decisão arquitetural V1 |
| `docs/adr/adr-004-language-gap-resolution.md` | `kimi` | Resolução do gap Go vs. Python |
| `docs/apex-v4-lineage.md` | `kimi` | Histórico técnico do slice v4 |
| `docs/team-validation-guide.md` | `kimi` | Guia de revisão para Crew A |
| `docs/adr-review-drafts.md` | `kimi` | Rascunhos de comentários para ADRs |

---

*Documento gerado em 2026-07-06 como artefato de unificação das vertentes `cowork` e `kimi` do projeto Apex.*  
*Autoria: Augusto Cezar (ambas as branches) · Síntese por agente de orquestração.*
