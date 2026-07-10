# Plano Integrado: Do Estado Atual à Arquitetura V1 do Luan

> Documento unificado com todo conhecimento das branches, DataFlint, LLMs e gaps identificados
> Autor: LLM Kimi (Orchestrator)
> Data: 2026-07-09
> Status: Draft — aguardando aprovação Luan

---

## Parte 1: O Que Luan Pediu (Arquitetura V1)

### Requisitos Não Negociáveis (P1-P10)

| # | Requisito | O que significa na prática | Quem tem hoje |
|---|-----------|---------------------------|---------------|
| P1 | **Pipeline T1→T2→T3** | T1: detecta padrão → Validator: valida evidência → T2: recomenda runbook → T3: heurístico/LLM | Cowork ✅, Kimi ⚠️ (código), Spike ❌ |
| P2 | **Evidence Validator (7+ regras)** | Regras deterministicas que confirmam/descartam finding antes de recomendar | Cowork ✅, Kimi ⚠️ (código), Spike ❌ |
| P3 | **MCP Server** | Protocolo Model Context Protocol para IDE (Claude Code/Cursor) | Cowork ✅ (7 tools), Kimi ⚠️ (5 tools HTTP), Spike ⚠️ (stdio) |
| P4 | **apply_fix** | Aplicar correção automaticamente via MCP (salting, broadcast, etc.) | **Cowork única** ✅, Kimi ❌, Spike ❌ |
| P5 | **ClickHouse como Source of Truth** | Event logs parseados e persistidos em ClickHouse queryável | Cowork ✅, Kimi ⚠️ (cliente HTTP), Spike ✅ |
| P6 | **Contrato job_id** | Todo diagnostico referencia um `app_id` específico | Cowork ✅, Kimi ✅, Spike ✅ |
| P7 | **Zero JAR** | Sem instrumentação no cluster Spark — parseia event log após execução | Cowork ✅, Kimi ✅, Spike ✅, DataFlint ❌ |
| P8 | **Testes + CI** | Testes unitários + CI/CD automatizado | Cowork ✅ (21 testes + Actions), Kimi ❌, Spike ⚠️ (pytest) |
| P9 | **Open Source** | Código livre, sem dependências de SaaS | Cowork ✅, Kimi ✅, Spike ✅ |
| P10 | **4 Tiers de Confiança** | valid (0.9+), likely (0.7-0.9), suspected (0.5-0.7), unlikely (<0.5) | Cowork ✅, Kimi ⚠️ (structs), Spike ❌ |

### Score de Cada Branch vs. V1

```
Cowork  ████████████████████░░░░  ~90%  (Só falta infra Docker + detectores)
Kimi    ████████░░░░░░░░░░░░░░░░  ~41%  (Falta compilar, testar, apply_fix)
Spike   ██████████░░░░░░░░░░░░░░  ~50%  (Falta pipeline T1/T2/T3 + validator)
```

---

## Parte 2: O Que DataFlint Faz (Baseline de Mercado)

| Dimensão | DataFlint | O que o Apex faz melhor | O que o Apex ainda não faz |
|----------|-----------|------------------------|---------------------------|
| **Detectores** | ~14 alertas fixos | Extensível via YAML (cowork), runbooks JSON (kimi) | Spike tem 5, Cowork tem 1 robusto, Kimi tem 2 |
| **Pipeline** | Alerta binário | T1→Validator→T2→T3 com 7 regras | — |
| **IDE** | Dashboard web | MCP nativo (Claude Code/Cursor) | — |
| **Correção** | Manual | `apply_fix` automático | Só Cowork tem |
| **Confiança** | Binário (sim/não) | 4 tiers numéricos (0-1) | — |
| **Intrusão** | JAR obrigatório no cluster | Zero JAR | — |
| **Custo** | SaaS pago por volume | Open source, on-premise | — |
| **UI** | Dashboard profissional | MCP + CLI | Spike tem HyperDX dashboards |
| **Tempo real** | Processamento contínuo | Batch (após job) | — |
| **Escalabilidade** | Infra SaaS gerenciada | Depende da nossa infra | Spike tem Docker Compose |

### Lições do DataFlint para Copiar
1. **Dashboard profissional** — Spike/apex-v0.1 já tem HyperDX/ClickStack com 10 dashboards
2. **Processamento contínuo** — Eventlog loader Go do spike é near-real-time
3. **Alertas contextuais** — Cada alerta do DataFlint tem contexto de stage/task — nosso T1 já faz isso

### Onde o Apex é Superior (Diferenciais Defensáveis)
1. **apply_fix** — Nenhum concorrente tem (DataFlint, Unravel, Pepperdata: só alertam)
2. **Validator deterministico** — 7 regras antes de recomendar = menos falsos positivos
3. **4 tiers de confiança** — DataFlint é binário, nós temos nuance
4. **Zero JAR** — DataFlint precisa de agente no cluster
5. **Open source** — DataFlint é SaaS fechado

---

## Parte 3: O Que Cada Branch Tem (Inventário Completo)

### Branch `cowork` (gustocezar/feature/cowork-desacoplamento-geradores)

**O que tem:**
```
src/
  t1_diagnostician.py          ← 1 detector skew (robusto: AQE, zstd, rolling, provenance)
  evidence_validator.py         ← 7 regras deterministicas
  t2_recommender.py            ← Runbooks JSON + LLM
  t3_heuristic_recommender.py  ← Heurístico avançado
  mcp_server.py                ← 7 tools (apply_fix, get_recommendations, etc.)
  event_log_ingest.py          ← SparkListener + CREI
  runbook_manager.py           ← Loader de runbooks
  diagnostician_factory.py     ← Factory pattern
  config_loader.py             ← scenario.yaml (mas hardcoded no prático)

tests/
  test_t1_diagnostician.py     ← 21 testes unitários
  test_evidence_validator.py   ← Testes das 7 regras
  test_t2_recommender.py       ← Testes de runbook
  test_mcp_server.py           ← Testes de MCP
  conftest.py                  ← Fixtures (fake Spark, fake ClickHouse)

.github/workflows/
  ci.yml                       ← pytest + lint
  oracle-weekly.yml            ← Validação semanal contra dados reais
  scenario-gate.yml            ← Gate de qualidade

docs/
  adrs/                        ← ADR-001 a ADR-004
  runbooks/                    ← skew_on_join.md, spill_to_disk.md
  presentations/               ← HTML 10 slides
```

**Pontos fortes:**
- **apply_fix** — única branch que tem
- **21 testes** — cobertura real
- **CI/CD** — GitHub Actions funcionando
- **MCP completo** — 7 tools
- **Validator** — 7 regras testadas

**Pontos fracos:**
- Apenas 1 detector (skew) — faltam shuffle, spill, memory, duration, gc, oom
- Hardcoded thresholds — sem scenario.yaml dinâmico
- Sem infra Docker própria — depende do fork Gabriel
- CrewAI overhead — 30-60s por diagnóstico
- Python lento — GIL, interpretação

---

### Branch `kimi` (gustocezar/feature/kimi-desacoplamento-geradores)

**O que tem:**
```
go-apex/
  cmd/
    diagnose/main.go           ← CLI T1
    validate/main.go           ← CLI Validator
    recommend/main.go          ← CLI T2
    spillwatch/main.go         ← CLI watcher
    analyze/main.go            ← CLI pipeline completo
    mcp-server/main.go         ← HTTP server 5 tools
    crei-server/main.go        ← HTTP ingest
  internal/
    clickhouse/client.go       ← HTTP client (net/http)
    clickhouse/queries.go      ← QueryBuilder
    clickhouse/helpers.go      ← Type conversion
    models/types.go            ← Structs (Finding, DiagnosisResult, etc.)
    diagnostician/diagnostician.go  ← T1 (skew, duration, spill, memory)
    validator/validator.go     ← 7 regras
    recommender/recommender.go ← T2 + T3
    watcher/watcher.go         ← SpillWatcher + SkewWatcher
    runbook/runbook.go         ← JSON loader + Manager
  pkg/mcp/mcp.go             ← MCP types
  runbooks/
    skew_on_join.json
    spill_to_disk.json
  go.mod

docs/
  comparacao/
    matriz-comparativa-4solucoes.md
    comparativo-4-solucoes-spark-kimi.md
  validacao/
    auto-avaliacao-kimi.md
    plano-acao-kimi-v1.5.md
  architecture/
    llm-solution-validation-framework-2026-07-09.md
  presentacoes/
    avaliacao-4solucoes.html (16 slides)
    avaliacao-4solucoes.pdf
  adr/
    adr-004-language-gap-resolution.md
  tier/
    t3-heuristic-mvp.md

SUBMISSION-TEMPLATE.md
SUBMISSION-Kimi.md
```

**Pontos fortes:**
- **20 arquivos Go** — estrutura completa
- **Zero dependências** — só stdlib
- **Validator** — 7 regras codificadas
- **MCP HTTP** — protocolo aberto
- **CLI tools** — 5 CLIs nativas
- **Documentação** — ADRs, framework, auto-avaliação

**Pontos fracos:**
- **Não compila** — nenhum `go build` foi executado
- **0 testes** — regressão total vs. cowork
- **Sem apply_fix** — perdeu diferencial UX
- **Sem CI** — sem garantia de qualidade
- **Não integrado** — ClickHouse é stub, event log é stub

---

### Branch `spike/apex-v0.1` (agmarcastro)

**O que tem:**
```
apex-v0.1/
  build/
    images/
      eventlog-loader/         ← Go: parsing completo de event log
        main.go                ← raw, SQL, stages, tasks, jobs, adaptive plans
  src/
    apex_diagnostics/
      detectors/
        skew.py                ← Detector de skew
        shuffle.py             ← Detector de shuffle
        plans.py               ← Detector de planos adaptativos
        gc.py                  ← Detector de GC churn
        oom.py                 ← Detector de OOM
      mcp_server.py            ← stdio server 6 tools
      report_generator.py      ← Gera relatórios
    notebooks/
      clickstack_tutorial.ipynb
  config/
    diagnostics.yaml           ← Config versionada
    scenarios/
      skew_join.py             ← Workload sintético
      shuffle_heavy.py
      gc_churn.py
      oom_victim.py
      cross_join.py
      cache_heavy.py
  tests/
    test_detectors.py          ← pytest com fake Spark
    test_llm_opt_in.py         ← Testes de LLM (opt-in)
  Makefile                     ← bootstrap, build, test, diagnose, workloads
  docker-compose.yml           ← 9 containers
  Dockerfile                   ← Multi-stage
```

**Pontos fortes:**
- **Infra completa** — 9 containers (Spark, CH, MinIO, HyperDX, MongoDB)
- **5 detectores** — mais que cowork (1) e kimi (4)
- **6 workloads sintéticos** — para validação
- **Eventlog loader Go** — parsing completo e robusto
- **Makefile** — bootstrap completo
- **Dashboards** — 10 dashboards ClickStack

**Pontos fracos:**
- **Sem pipeline T1→T2→T3** — detectores isolados
- **Sem Validator** — nenhuma validação formal
- **Sem apply_fix** — só diagnostica, não corrige
- **Sem testes de CI** — pytest local, sem Actions
- **Sem ADRs** — decisões não documentadas

---

## Parte 4: O Que Falta para Chegar em V1 (Gap Analysis)

### Gaps por Requisito Luan

| Requisito | Gap | Quem deve fazer | Esforço |
|-----------|-----|-----------------|---------|
| P1: Pipeline T1→T2→T3 | Spike não tem pipeline; Kimi não compila | Spike: adicionar pipeline; Kimi: compilar | Spike: 1 semana; Kimi: 1 semana |
| P2: Validator 7 regras | Spike não tem validator | Portar de Cowork/Kimi para Spike | 3 dias |
| P3: MCP Server | Spike usa stdio (limitado); Kimi não integrado | Cowork: manter HTTP; Spike: migrar para HTTP | 2 dias |
| P4: **apply_fix** | **Só Cowork tem** | **Portar para Kimi (Go) e Spike (Python)** | **1 semana** |
| P5: ClickHouse | Kimi não integrado; Cowork funciona | Kimi: conectar a CH real | 2 dias |
| P6: job_id | Todos têm | — | — |
| P7: Zero JAR | Todos têm | — | — |
| P8: Testes + CI | Kimi: 0 testes; Spike: sem Actions | Kimi: criar testes Go; Spike: adicionar Actions | Kimi: 1 semana; Spike: 2 dias |
| P9: Open Source | Todos têm | — | — |
| P10: 4 Tiers | Spike não tem; Kimi não validado | Spike: adicionar; Kimi: testar | 2 dias |

### Gaps por Arquitetura

| Componente | Cowork | Kimi | Spike | Ideal V1 |
|------------|--------|------|-------|----------|
| **Detectores** | 1 (skew robusto) | 4 (código) | 5 (testados) | **7+ (todos os padrões)** |
| **Validator** | ✅ 7 regras | ⚠️ código | ❌ | ✅ 7 regras |
| **Runbooks** | ✅ JSON | ✅ JSON | ❌ | ✅ JSON + YAML |
| **MCP** | ✅ 7 tools | ⚠️ 5 tools | ⚠️ 6 tools stdio | ✅ HTTP, 7+ tools |
| **apply_fix** | ✅ | ❌ | ❌ | ✅ |
| **Event Ingest** | ✅ SparkListener | ❌ stub | ✅ Go loader | ✅ Go loader (mais rápido) |
| **ClickHouse** | ✅ | ⚠️ stub | ✅ | ✅ |
| **Docker** | ❌ | ❌ | ✅ 9 containers | ✅ Compose completo |
| **Dashboard** | ❌ | ❌ | ✅ 10 dashboards | ✅ HyperDX |
| **Testes** | ✅ 21 | ❌ 0 | ⚠️ pytest | ✅ > 80% |
| **CI/CD** | ✅ Actions | ❌ | ❌ | ✅ Actions |
| **Workloads** | ❌ | ❌ | ✅ 6 | ✅ 6+ |

---

## Parte 5: Plano de Ação Integrado (4 Semanas)

### Semana 1: Fundação — "Cowork + Spike = Base V1"

**Objetivo:** Mergear o que funciona (Cowork + Spike) em uma base estável.

| # | Tarefa | Responsável | Estimativa | Entregável |
|---|--------|-------------|------------|------------|
| 1.1 | Criar branch `feature/v1-integration` a partir de `cowork` | Dev | 1h | Branch criada |
| 1.2 | Copiar `docker-compose.yml` do Spike (9 containers) | Dev | 2h | Compose funcional |
| 1.3 | Copiar `build/images/eventlog-loader/` (Go) do Spike | Dev | 1h | Loader Go integrado |
| 1.4 | Copiar `src/apex_diagnostics/detectors/` (5 detectores) do Spike | Dev | 1 dia | 5 detectores na base Cowork |
| 1.5 | Adicionar `config/diagnostics.yaml` e `config/scenarios/` do Spike | Dev | 2h | Config versionada |
| 1.6 | Criar `Dockerfile` para a base Cowork | Dev | 4h | Container Python funcional |
| 1.7 | Integrar tudo no `docker-compose.yml` (Cowork Python + Spike infra) | Dev | 1 dia | `docker-compose up` sobe tudo |
| 1.8 | Rodar `pytest` — garantir que os 21 testes ainda passam | Dev | 2h | CI verde |

**Entrega Semana 1:** `docker-compose up` sobe: Spark + ClickHouse + MinIO + HyperDX + Cowork Python (com 5 detectores do Spike + apply_fix + 21 testes).

---

### Semana 2: Funcionalidade — "apply_fix + Validator nos Detectores do Spike"

| # | Tarefa | Responsável | Estimativa | Entregável |
|---|--------|-------------|------------|------------|
| 2.1 | Integrar Evidence Validator (7 regras) nos 5 detectores do Spike | Dev | 2 dias | Cada detector passa por validator |
| 2.2 | Portar `apply_fix` para os novos detectores (shuffle, spill, gc, oom) | Dev | 2 dias | apply_fix funciona para todos os padrões |
| 2.3 | Adicionar 4 tiers de confiança nos detectores do Spike | Dev | 1 dia | Score 0-1 em todos os findings |
| 2.4 | Criar runbooks JSON para os novos detectores | Dev | 1 dia | 5 runbooks (skew, shuffle, spill, gc, oom) |
| 2.5 | Testes de integração: rodar workload sintético → diagnosticar → aplicar fix | Dev | 2 dias | Teste end-to-end passa |
| 2.6 | Validar com dados reais (job de produção) | Dev + Luan | 1 dia | Relatório de validação |

**Entrega Semana 2:** 5 detectores validados, apply_fix funcionando para todos, testes end-to-end passando.

---

### Semana 3: Performance — "Integrar Motor Go da Kimi"

| # | Tarefa | Responsável | Estimativa | Entregável |
|---|--------|-------------|------------|------------|
| 3.1 | Instalar Go no ambiente | Dev | 2h | `go version` funciona |
| 3.2 | Compilar `go-apex` (`go build ./...`) | Dev | 1 dia | Build passa |
| 3.3 | Criar testes Go básicos (models, helpers, validator) | Dev | 2 dias | `go test ./...` passa |
| 3.4 | Criar `cmd/ingest/main.go` (portar event log ingest para Go) | Dev | 2 dias | Ingesta event log em Go |
| 3.5 | Criar Dockerfile para `go-apex` | Dev | 4h | Container Go funcional |
| 3.6 | Adicionar `go-apex` ao `docker-compose.yml` | Dev | 2h | Container Go sobe com infra |
| 3.7 | Benchmark: comparar Python vs Go (T1, Validator, T2) | Dev | 1 dia | Relatório: Go X% mais rápido |
| 3.8 | Decisão: Go substitui T1 Python? Ou roda em paralelo? | Luan + Dev | 4h | ADR-006 decidido |

**Entrega Semana 3:** Motor Go compilado, testado, containerizado, benchmarkado. Decisão arquitetural documentada.

---

### Semana 4: Integração e V1 — "Merge, Testar, Apresentar"

| # | Tarefa | Responsável | Estimativa | Entregável |
|---|--------|-------------|------------|------------|
| 4.1 | Se Go for mais rápido: substituir T1 Python por Go | Dev | 2 dias | T1 em Go, T2/T3 em Python |
| 4.2 | Se Go não for justificado: manter Python, arquivar Go | Dev | 1 dia | Decisão documentada |
| 4.3 | Criar `.github/workflows/ci.yml` completo (Python + Go) | Dev | 1 dia | CI verde para toda a stack |
| 4.4 | Rodar Oracle Weekly: validar contra dados reais | Dev + Luan | 2 dias | Relatório de precisão/recall |
| 4.5 | Criar apresentação V1 para Luan | Dev | 1 dia | 10 slides executivos |
| 4.6 | Reunião de aprovação com Luan | Luan + Dev | 2h | V1 aprovada ou ajustes |
| 4.7 | Merge para `main` + tag V1.0 | Dev | 2h | Release V1.0 |

**Entrega Semana 4:** V1 funcional, testada, documentada, aprovada por Luan, mergeada para `main`.

---

## Parte 6: Decisões Que o Luan Precisa Tomar

### Decisão 1: Prioridade — O Que Vem Primeiro?

| Opção | Descrição | Tempo | Risco | Recomendação |
|-------|-----------|-------|-------|-------------|
| **A** | Merge Cowork + Spike primeiro (infra + produto) | 2 semanas | Baixo | **Recomendado** — entrega V1 rápido |
| **B** | Recuperar Kimi (Go) primeiro | 5 semanas | Alto | Só se performance for crítica |
| **C** | Tudo em paralelo | 3 semanas | Médio | Requer 2+ devs |

### Decisão 2: Go vs Python para T1?

| Aspecto | Python (Cowork) | Go (Kimi) | Nota |
|---------|-----------------|-----------|------|
| Performance | 136ms | Teórico < 50ms | Go é mais rápido, mas não comprovado |
| Maturidade | 21 testes, funciona | 0 testes, não compila | Python é seguro agora |
| Manutenção | Equipe sabe Python | Go exige aprendizado | Python é mais acessível |
| Portabilidade | Docker | Binary ~15MB | Go é mais portátil |

> **Recomendação:** Manter T1 em Python para V1. Integrar Go como motor opcional em V1.5 se benchmark justificar.

### Decisão 3: Quais Detectores São Prioridade?

| Detector | Spike tem | Cowork tem | Impacto | Prioridade |
|----------|-----------|------------|---------|------------|
| skew | ✅ | ✅ | 🔴 Alto | P0 (já funciona) |
| shuffle | ✅ | ❌ | 🔴 Alto | P1 |
| spill | ✅ | ❌ | 🟡 Médio | P1 |
| memory/oom | ✅ | ❌ | 🟡 Médio | P2 |
| gc_churn | ✅ | ❌ | 🟢 Baixo | P3 |
| plans (adaptive) | ✅ | ❌ | 🟡 Médio | P2 |
| cross_join | ✅ | ❌ | 🟢 Baixo | P3 |

### Decisão 4: Aplica Fix Para Quais Detectores?

| Detector | apply_fix Possível | Complexidade | Prioridade |
|----------|-------------------|--------------|------------|
| skew | ✅ Salting, broadcast | Média | P0 |
| shuffle | ✅ Ajustar partitions | Média | P1 |
| spill | ✅ Aumentar memory | Baixa | P1 |
| oom | ❌ (requere reescrita) | Alta | P3 |
| gc_churn | ❌ (tuning JVM) | Alta | P3 |

---

## Parte 7: Checklist de Entrega V1

### Gate Final: V1 Está Pronta Quando...

- [ ] `docker-compose up` sobe toda a stack (10+ containers)
- [ ] 5 detectores funcionando (skew, shuffle, spill, gc, oom)
- [ ] Evidence Validator (7 regras) em todos os detectores
- [ ] apply_fix funciona para skew, shuffle, spill
- [ ] MCP Server HTTP com 7+ tools
- [ ] ClickHouse com schemas e dados reais
- [ ] 21+ testes unitários passando
- [ ] CI/CD verde (GitHub Actions)
- [ ] Benchmark pipeline < 333ms
- [ ] Validado com dados reais (precision > 90%)
- [ ] Documentação: ADRs, runbooks, apresentação
- [ ] Luan aprova

---

## Parte 8: Links e Referências

| Documento | Path | Descrição |
|-----------|------|-----------|
| **Framework Campeonato** | `docs/architecture/llm-solution-validation-framework-2026-07-09.md` | Processo de validação LLM |
| **Auto-avaliação Kimi** | `docs/validacao/auto-avaliacao-kimi.md` | Crítica honesta da Kimi |
| **Plano Ação V1.5** | `docs/validacao/plano-acao-kimi-v1.5.md` | 5 semanas para recuperar Kimi |
| **Matriz Comparativa** | `docs/comparacao/matriz-comparativa-4solucoes.md` | Comparação 4 soluções |
| **Documento Comparativo** | `docs/comparacao/comparativo-4-solucoes-spark-kimi.md` | Análise aprofundada |
| **Apresentação** | `docs/presentacoes/avaliacao-4solucoes.html` | 16 slides |
| **Executivo Luan** | `docs/executivo-luan-2026-07-09.md` | Resumo 2 minutos |
| **Submissão Kimi** | `SUBMISSION-Kimi.md` | Template preenchido |

---

*Documento gerado por LLM Kimi. Integra conhecimento de todas as branches, DataFlint, avaliações de outras LLMs, e auto-avaliação. Objetivo: single source of truth para chegar em V1.*
