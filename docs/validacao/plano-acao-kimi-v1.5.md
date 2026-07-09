# Plano de Acao: Recuperar a `kimi` para Arquitetura V1 do Luan

> Gerado por: LLM Kimi (auto-avaliacao)
> Data: 2026-07-07
> Branch alvo: `gustocezar/feature/kimi-desacoplamento-geradores`
> Referencia: Arquitetura V1 solicitada por Luan Moreno

---

## Resumo Executivo

A branch `kimi` tem **~40% da V1** (base tecnica Go) vs. a `cowork` que tem **~90%** (produto funcional). Este plano recupera o gap em **4 semanas** (5 semanas com buffer), transformando a `kimi` em um **componente produtivo** dentro da arquitetura V1.5.

**Filosofia:** Nao reescrever a `cowork`. Integrar o core Go da `kimi` como **motor de performance** dentro da arquitetura da `cowork`.

---

## Fase 1: Fundacao — "Compila e Testa" (Semana 1)

**Objetivo:** O codigo Go compila, passa em testes unitarios, tem CI.

| # | Task | Estimativa | Criterio de aceitacao | Depende de |
|---|------|-----------|----------------------|------------|
| 1.1 | Instalar Go no ambiente de desenvolvimento | 2h | `go version` funciona | Nada |
| 1.2 | Rodar `go build ./...` e corrigir erros de compilacao | 1 dia | Build passa sem erros | 1.1 |
| 1.3 | Criar `internal/testutil/fake_clickhouse.go` | 1 dia | Fake responde queries HTTP com JSON mock | 1.2 |
| 1.4 | Escrever `models/types_test.go` | 4h | Testes de marshaling/unmarshaling JSON | 1.2 |
| 1.5 | Escrever `clickhouse/helpers_test.go` | 4h | Testes de conversao de tipos | 1.2 |
| 1.6 | Escrever `validator/validator_test.go` | 1 dia | 7 regras testadas com table-driven tests | 1.2 |
| 1.7 | Escrever `diagnostician/diagnostician_test.go` | 1 dia | 4 detectores testados com dados mock | 1.3 |
| 1.8 | Criar `.github/workflows/go-test.yml` | 4h | CI roda `go test ./...` em PRs | 1.4-1.7 |
| 1.9 | Criar `Makefile` (`test`, `build`, `lint`) | 2h | `make test` funciona localmente | 1.2 |

**Entrega Fase 1:** `go test ./...` passa, CI verde, build funciona.
**Estimativa total:** 1 semana (5 dias uteis)

---

## Fase 2: Funcionalidade — "Integra e Fecha Loop" (Semanas 2-3)

**Objetivo:** O codigo Go se conecta a ClickHouse real, ingesta event logs, e fecha o loop no IDE.

| # | Task | Estimativa | Criterio de aceitacao | Depende de |
|---|------|-----------|----------------------|------------|
| 2.1 | Configurar conexao ClickHouse real | 1 dia | Query `SELECT 1` retorna sucesso | 1.2 |
| 2.2 | Portar `event_log_ingest.py` → `cmd/ingest/main.go` | 3 dias | Ingesta event log real para ClickHouse | 2.1 |
| 2.3 | Implementar `apply_fix` no MCP Server | 2 dias | Tool `apply_fix` recebe JSON e retorna status | 1.2 |
| 2.4 | Adicionar detector `shuffle` ao Diagnostician | 1 dia | Detecta skew em shuffle operations | 1.2 |
| 2.5 | Criar `cmd/analyze/main.go` (pipeline T1→T2→T3) | 2 dias | `go run ./cmd/analyze -app-id=xxx` retorna findings | 2.1-2.4 |
| 2.6 | Validar benchmark T1 < 136ms em Go | 1 dia | `go test -bench` confirma < 136ms | 2.4 |
| 2.7 | Criar parser `scenario.yaml` em Go | 2 dias | Le YAML e gera config de detectores | 1.2 |
| 2.8 | Portar testes de integracao (fake Spark + CH) | 2 dias | Testes passam sem infra real | 1.3 |

**Entrega Fase 2:** Pipeline completo funcional em Go, conectado a ClickHouse, com apply_fix.
**Estimativa total:** 2 semanas (10 dias uteis)

---

## Fase 3: Integracao — "Docker e Plataforma" (Semana 4)

**Objetivo:** O Go da `kimi` roda dentro da infra Docker da `spike/apex-v0.1`.

| # | Task | Estimativa | Criterio de aceitacao | Depende de |
|---|------|-----------|----------------------|------------|
| 3.1 | Criar `Dockerfile` para `go-apex` | 1 dia | `docker build -t go-apex .` funciona | 2.1 |
| 3.2 | Criar `docker-compose.yml` overlay | 1 dia | `docker-compose up go-apex` sobe com ClickHouse | 3.1 |
| 3.3 | Integrar com `spike/apex-v0.1` docker-compose | 2 dias | Go se conecta a ClickHouse do spike | 3.2 |
| 3.4 | Criar script `bootstrap.sh` | 1 dia | `make bootstrap` configura ambiente completo | 3.3 |
| 3.5 | Rodar benchmark end-to-end | 1 dia | Pipeline completo < 333ms com dados reais | 3.3 |
| 3.6 | Documentar ADR-005: Docker integration | 4h | ADR explica decisoes de arquitetura | Nada |

**Entrega Fase 3:** `go-apex` roda em container, integrado a infra spike.
**Estimativa total:** 1 semana (5 dias uteis)

---

## Fase 4: Merge — "Reconcilia e Apresenta" (Semana 5)

**Objetivo:** A `kimi` se funde com a `cowork` formando V1.5.

| # | Task | Estimativa | Criterio de aceitacao | Depende de |
|---|------|-----------|----------------------|------------|
| 4.1 | Mapear overlap entre `cowork` e `kimi` | 1 dia | Documento de compatibilidade | Nada |
| 4.2 | Decidir: o que fica em Go, o que fica em Python | 1 dia | ADR-006 aprovado | 4.1 |
| 4.3 | Implementar `apply_fix` em Go (copiar da cowork) | 2 dias | Feature parity com cowork | 2.3 |
| 4.4 | Portar testes da cowork para Go | 2 dias | Cobertura >= 80% | 1.8 |
| 4.5 | Criar teste de regressao (cowork vs kimi) | 1 dia | Mesmo input, mesmo output | 4.4 |
| 4.6 | Documentar `docs/adr/adr-006-merge-v1.5.md` | 1 dia | ADR explica merge strategy | 4.2 |
| 4.7 | Criar apresentacao V1.5 para Luan | 1 dia | 10 slides, executivo | 4.6 |
| 4.8 | Rehearsal (dry-run com Luan) | 1 dia | Feedback incorporado | 4.7 |

**Entrega Fase 4:** Branch `kimi` pronta para merge, com testes, docs, e apresentacao.
**Estimativa total:** 1 semana (5 dias uteis, 1 dia buffer)

---

## Matriz de Dependencias

```
[1.1 Instalar Go]
    ↓
[1.2 go build] ─────┬──→ [1.3 Fake CH]
    ↓               │         ↓
[1.4 types_test] ←──┘    [2.1 CH real]
[1.5 helpers_test]            ↓
[1.6 validator_test]      [2.2 ingest]
[1.7 diagnostician_test]     ↓
    ↓                    [2.3 apply_fix]
[1.8 CI] ─────────────────────┘
    ↓
[2.4 shuffle] ───→ [2.5 pipeline]
    ↓                ↓
[2.6 benchmark]  [2.7 YAML parser]
    ↓                ↓
[3.1 Dockerfile]  [2.8 integr tests]
    ↓
[3.2 compose] ───→ [3.3 spike integ]
    ↓
[3.4 bootstrap] ───→ [3.5 benchmark e2e]
    ↓
[3.6 ADR-005] ───→ [4.1-4.8 Merge]
```

---

## Checkpoints de Validacao

| Semana | Checkpoint | Quem valida | Passa se |
|--------|-----------|-------------|----------|
| 1 | `go test ./...` passa | CI + Desenvolvedor | 100% testes passam |
| 2 | Pipeline T1→T2→T3 funciona | Teste manual | `analyze` retorna findings reais |
| 3 | `apply_fix` funciona | Teste manual | MCP retorna "fix applied" |
| 4 | Docker sobe completo | CI | `docker-compose up` sobe 10 containers |
| 5 | Benchmark < 333ms | Script | T1+Validator+T2 < 333ms |
| 5 | Apresentacao Luan | Luan Moreno | Aprovacao para merge |

---

## Riscos e Mitigacoes

| Risco | Probabilidade | Impacto | Mitigacao |
|-------|--------------|---------|-----------|
| Go nao compila (erros de sintaxe) | Alta | 🔴 Bloqueante | Fase 1 dedicada so para isso |
| ClickHouse Go driver nao funciona | Media | 🔴 Bloqueante | Usar HTTP client nativo (ja implementado) |
| apply_fix em Go e mais complexo que Python | Media | 🟡 Alto | Copiar logica da cowork, nao reinventar |
| Spike muda durante o merge | Baixa | 🟡 Alto | Pinar versao do spike no Docker Compose |
| Luan muda requisitos | Media | 🟡 Alto | Checkpoint semanal com review |

---

## Estimativa Consolidada

| Fase | Dias | Semanas | Buffer |
|------|------|---------|--------|
| 1: Fundacao | 5 | 1 | 0 |
| 2: Funcionalidade | 10 | 2 | 0 |
| 3: Integracao | 5 | 1 | 0 |
| 4: Merge | 5 | 1 | 1 dia |
| **Total** | **25** | **5** | **1 dia** |

> **Realista para apresentar ao Luan:** 5 semanas (1 mes) para V1.5 funcional.

---

*Plano gerado por auto-avaliacao da LLM Kimi. Tasks sao atomicas, verificaveis, e priorizadas por dependencia.*
