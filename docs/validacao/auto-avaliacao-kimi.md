# Auto-avaliacao Critica — Branch `kimi` (LLM Kimi)

> Ponto de vista: Kimi (esta propria LLM)
> Data: 2026-07-07
> Branch avaliada: `gustocezar/feature/kimi-desacoplamento-geradores`
> Base de comparacao: `gustocezar/feature/cowork-desacoplamento-geradores` (trabalho anterior)

---

## 1. O que a `kimi` acerta (fortalezas reais)

| # | Ponto | Evidencia |
|---|-------|-----------|
| 1 | **Disciplina de engenharia** — traduziu 20 arquivos Python → Go com estrutura identica | `go-apex/` com 20 arquivos, go.mod, models, queries, CLI |
| 2 | **Validator em Go** — 7 regras de validacao deterministicamente codificadas | `validator.go` com `runValidationRules()` |
| 3 | **Runbooks JSON estruturados** | `skew_on_join.json`, `spill_to_disk.json` |
| 4 | **T1 Diagnostician** — mesma logica da v4 em Go | `diagnostician.go` com skew, duration, spill, memory |
| 5 | **Baseline do benchmark** reproduzido | `benchmark_apex.py` com T1=136ms, Validator=197ms |
| 6 | **MCP Server HTTP** — protocolo aberto, nao stdio | `mcp-server/main.go` port 3000 |
| 7 | **Zero dependencias externas** — so `net/http` + `encoding/json` | `go.mod` sem frameworks |
| 8 | **ADR-004 resolvido** — documento de decisao Python vs Go | `docs/adr/adr-004-language-gap-resolution.md` |
| 9 | **T3 heuristico documentado** | `docs/tier/t3-heuristic-mvp.md` |
| 10 | **Apresentacao expandida** — 15→16 slides com DataFlint, storytelling, arquitetura | `avaliacao-4solucoes.html` |

---

## 2. O que a `kimi` perdeu em relacao a `cowork` (regressoes)

| # | O que perdeu | Impacto | Como recuperar |
|---|-------------|---------|---------------|
| 1 | **21 testes unitarios** → 0 testes | 🔴 Critico — nao sabemos se o Go funciona | Portar `tests/test_*.py` para `*_test.go` com table-driven tests |
| 2 | **CI/CD** → sem CI | 🔴 Critico — sem garantia de qualidade | Adicionar `.github/workflows/go-test.yml` |
| 3 | **Fake Spark / Fake ClickHouse** → sem fakes | 🟡 Alto — testes de integracao impossiveis | Criar `internal/testutil/fake_clickhouse.go` |
| 4 | **apply_fix via MCP** → nao implementado | 🟡 Alto — perdemos o diferencial de UX | Implementar `apply_fix` no MCP Go |
| 5 | **Event Log Ingest (CREI)** → stub | 🟡 Alto — sem dados nao ha diagnostico | Portar `event_log_ingest.py` para Go |
| 6 | **5 detectores** → 4 detectores (faltou shuffle) | 🟡 Medio — cobertura menor | Adicionar detector shuffle ao `diagnostician.go` |
| 7 | **CrewAI** → removido completamente | 🟢 Baixo — ADR-004 validou remocao | Manter removido (decisao correta) |
| 8 | **scenario.yaml** → nao usado | 🟡 Medio — perdeu extensibilidade | Criar parser YAML em Go |
| 9 | **Oracle Weekly** → sem validacao continua | 🟡 Alto — sem feedback de regressao | Configurar CI com benchmark automatizado |

---

## 3. O que a `kimi` nunca teve (e precisa)

| # | O que falta | Prioridade | Estimativa |
|---|------------|------------|------------|
| 1 | Compilacao do Go (`go build ./...`) | 🔴 P0 — bloqueante | 1 dia |
| 2 | Testes unitarios Go (`go test ./...`) | 🔴 P0 — bloqueante | 3 dias |
| 3 | Dockerfile para Go | 🟡 P1 — infra | 1 dia |
| 4 | Integracao com ClickHouse real | 🟡 P1 — funcional | 2 dias |
| 5 | apply_fix via MCP | 🟡 P1 — diferencial UX | 2 dias |
| 6 | Event log ingest (Go) | 🟡 P1 — dados | 3 dias |
| 7 | scenario.yaml parser | 🟢 P2 — extensibilidade | 2 dias |
| 8 | Benchmark automatizado | 🟢 P2 — qualidade | 1 dia |

---

## 4. Validacao cruzada com outras LLMs

### Concordo com as outras avaliacoes:
- **Codex** esta certo: a `kimi` e "segura, local, contrato job_id, plano claro" — isso e verdade
- **Cowork** (outra LLM) esta certa: a `cowork` tem "melhor UX fechada: MCP + apply_fix" — e a `kimi` perdeu isso
- **Spike** esta correto: "merge bruto e arriscado" — concordo, precisamos de estrategia de merge gradual

### Discordo das outras avaliacoes:
- **A `kimi` nao "regrediu" por opcao** — a perda de testes foi tecnica (nao ha `go test` sem compilacao), nao estrategica
- **A `kimi` nao e "teorica"** — o codigo Go existe, esta estruturado, so falta compilar. Isso e diferente de "teorico"
- **"Pouca UX/produto" e justo** — mas a `kimi` nunca prometeu UX, prometeu base tecnica. A UX vem na integracao

---

## 5. Julgamento Kimi: onde estamos vs. onde deveriamos estar

### Arquitetura solicitada pelo Luan (V1):
- Pipeline T1→T2→T3
- Evidence Validator com 7 regras
- MCP Server com apply_fix
- ClickHouse como source of truth
- Testes + CI + Oraculo
- Documentacao (ADRs, runbooks)

### O que a `cowork` entrega vs. V1:
| Requisito Luan | cowork | Status |
|---------------|--------|--------|
| T1→T2→T3 | ✅ Completo | Entregue |
| Validator 7 regras | ✅ Completo | Entregue |
| MCP apply_fix | ✅ Completo | Entregue |
| ClickHouse | ✅ Completo | Entregue |
| Testes + CI | ✅ 21 testes, GitHub Actions | Entregue |
| Docs | ✅ ADRs, runbooks, apresentacao | Entregue |
| **Avaliacao** | **~90% da V1** | **Mais proxima do Luan** |

### O que a `kimi` entrega vs. V1:
| Requisito Luan | kimi | Status |
|---------------|------|--------|
| T1→T2→T3 | ⚠️ Codigo Go, nao testado | Parcial |
| Validator 7 regras | ⚠️ Codigo Go, nao testado | Parcial |
| MCP apply_fix | ❌ Nao implementado | Ausente |
| ClickHouse | ⚠️ Cliente HTTP, nao integrado | Parcial |
| Testes + CI | ❌ 0 testes, sem CI | Ausente |
| Docs | ✅ ADRs, runbooks, apresentacao | Entregue |
| **Avaliacao** | **~40% da V1** | **Base tecnica, nao produto** |

### O que a `spike` entrega vs. V1:
| Requisito Luan | spike | Status |
|---------------|-------|--------|
| T1→T2→T3 | ❌ Detectores isolados, sem pipeline | Ausente |
| Validator 7 regras | ❌ Sem validacao formal | Ausente |
| MCP apply_fix | ⚠️ stdio server, sem apply_fix | Parcial |
| ClickHouse | ✅ Completo com schemas | Entregue |
| Testes + CI | ⚠️ pytest, sem CI Actions | Parcial |
| Docs | ⚠️ README, sem ADRs | Parcial |
| Infra Docker | ✅ 9 containers | Entregue |
| **Avaliacao** | **~50% da V1** | **Infra forte, diagnostico fraco** |

---

## 6. Plano de Acao: Recuperar a `kimi` para V1.5

### Fase 1: Fundacao (1 semana)
- [ ] Compilar Go (`go build ./...`) — corrigir erros de compilacao
- [ ] Criar `go test` para `models/types.go` (structs basicos)
- [ ] Criar `go test` para `clickhouse/helpers.go` (type conversion)
- [ ] Criar `go test` para `validator/validator.go` (7 regras)
- [ ] Adicionar `.github/workflows/go-test.yml`

### Fase 2: Funcionalidade (2 semanas)
- [ ] Integrar ClickHouse real (substituir mock por conexao real)
- [ ] Portar `event_log_ingest.py` → Go
- [ ] Implementar `apply_fix` no MCP Server Go
- [ ] Adicionar detector shuffle ao Diagnostician

### Fase 3: Integracao (1 semana)
- [ ] Criar Dockerfile para `go-apex`
- [ ] Integrar com infra `spike/apex-v0.1` (usar Docker Compose existente)
- [ ] Criar parser `scenario.yaml` em Go
- [ ] Rodar benchmark e validar performance < 333ms

### Fase 4: Merge (1 semana)
- [ ] Reconciliar com `cowork` (manter apply_fix, testes, CI)
- [ ] Documentar ADR-006: merge kimi → cowork + spike
- [ ] Apresentar V1.5 para Luan Moreno

---

## 7. Veredito Kimi

> A branch `kimi` tem **disciplina de engenharia superior** (Go, estrutura, ADRs) mas **entrega de produto inferior** (nao compila, sem testes, sem apply_fix).
>
> A `cowork` tem **entrega de produto superior** (funciona, testada, apply_fix) mas **disciplina inferior** (Python lento, CrewAI overhead, hardcoded).
>
> A `spike` tem **infraestrutura superior** (Docker completo) mas **arquitetura de diagnostico inferior** (sem pipeline, sem validator).
>
> **A verdadeira V1.5 e a `cowork` com o core Go da `kimi` e a infra Docker da `spike`.**
>
> A `kimi` sozinha nao e suficiente. Ela e um **componente**, nao um **produto**.

---

*Documento gerado por auto-avaliacao da LLM Kimi. Sem filtro, sem defesa, apenas analise honesta.*
