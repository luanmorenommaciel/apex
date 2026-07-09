# LLM Solution Validation Framework

> Documento: `docs/architecture/llm-solution-validation-framework-2026-07-09.md`
> Versão: 1.0
> Autor: LLM Kimi (Orchestrator)
> Data: 2026-07-09
> Status: Draft — aguardando aprovação Luan Moreno

---

## 1. Visão Geral

Este framework estabelece um processo estruturado para **múltiplas LLMs gerarem, competirem e refinarem** soluções para o projeto Apex, convergindo para uma **única solução testável e segura**.

**Filosofia:**
> Cada LLM gera a melhor solução dela. O Orchestrator (Kimi) compara, valida e transforma as melhores partes numa solução única, testável e segura.

**Processo:**
```
[LLM A] ────┐
[LLM B] ────┼──→ [Comparação] ──→ [Validação] ──→ [Refinamento] ──→ [V1.5]
[LLM C] ────┘         ↑              ↑                ↑
                   Matriz          Gates           Iteração
```

---

## 2. Premissas do Luan (Requisitos Não Negociáveis)

| # | Premissa | Descrição | Origem |
|---|----------|-----------|--------|
| P1 | **Pipeline T1→T2→T3** | T1 (diagnóstico), T2 (runbook), T3 (heurístico/LLM) | Issue #1, ADR-001 |
| P2 | **Evidence Validator** | 7+ regras de validação deterministicas | Issue #3, ADR-002 |
| P3 | **MCP Server** | Protocolo MCP para integração IDE (Claude Code/Cursor) | Issue #4, ADR-003 |
| P4 | **apply_fix** | Capacidade de aplicar correção via MCP | Issue #5 |
| P5 | **ClickHouse como Source of Truth** | Event logs persistidos e queryáveis | Issue #7 |
| P6 | **Contrato job_id** | Todo diagnóstico referencia um app_id específico | Issue #8 |
| P7 | **Zero JAR** | Sem instrumentação no cluster Spark | Issue #9 |
| P8 | **Testes + CI** | Cada gate exige testes verdes | Issue #10 |
| P9 | **Open Source** | Código livre, sem dependências de SaaS | Issue #11 |
| P10 | **4 Tiers de Confiança** | valid (0.9+), likely (0.7-0.9), suspected (0.5-0.7), unlikely (<0.5) | Issue #12 |

---

## 3. Critérios de Avaliação (Com Pesos)

| Critério | Peso | Descrição | Como medir |
|----------|------|-----------|------------|
| **C1: Funcionalidade** | 25% | Implementa os 10 requisitos do Luan? | Checklist P1-P10 |
| **C2: Performance** | 15% | Pipeline completo < 333ms? | Benchmark T1+Validator+T2 |
| **C3: Testes** | 15% | Cobertura > 80%? Testes passam? | `pytest` / `go test` |
| **C4: Arquitetura** | 10% | Separação T1/T2/T3, desacoplamento | Review de código |
| **C5: Documentação** | 10% | ADRs, runbooks, apresentação | Checklist docs |
| **C6: Infraestrutura** | 10% | Docker, CI/CD, deploy fácil | `docker-compose up` |
| **C7: UX/IDE** | 10% | MCP funcional, apply_fix, feedback claro | Teste manual IDE |
| **C8: Extensibilidade** | 5% | scenario.yaml, novos detectores fáceis | Adicionar detector novo |

**Score total:** Soma ponderada (max 100%)
**Score mínimo para aprovação:** 70% (Gate 3)
**Score mínimo para merge:** 85% (Gate 5)

---

## 4. Matriz Comparativa — DataFlint como Baseline

| Dimensão | DataFlint (Baseline) | spike/apex-v0.1 | cowork (nossa) | kimi (esta) | Peso |
|----------|---------------------|-------------------|----------------|-------------|------|
| **Detectores** | ~14 fixos | 5, testados | 1 (skew robusto) + Crew.ai | 2 runbooks Go (não compilado) | C1 |
| **Velocidade** | Tempo real | Determinístico rápido | LLM 30-60s | Teórica (Go) | C2 |
| **Fecha loop IDE** | ❌ Dashboard | ❌ | ✅ apply_fix | ❌ | C7 |
| **Config** | Admin UI | diagnostics.yaml | Hardcoded | Runbooks JSON | C8 |
| **Rigor** | n/a | testes + fakes + uv | 20 testes + CI + ADRs | Regrediu (0 testes) | C3 |
| **Validado real** | ✅ Produto | ✅ | ✅ | ⚠️ Só Python antiga | C1 |
| **Pipeline T1→T2→T3** | ❌ | ❌ | ✅ | ⚠️ Código, não testado | C4 |
| **MCP apply_fix** | ❌ | ❌ | ✅ | ❌ | C7 |
| **Docker** | ❌ SaaS | ✅ 9 containers | ❌ | ❌ | C6 |
| **Documentação** | ❌ | ⚠️ README | ✅ ADRs + runbooks | ✅ ADRs | C5 |

**Legenda:**
- ✅ Entregue | ⚠️ Parcial | ❌ Ausente

---

## 5. Gates de Validação (Gate por Gate)

### Gate 0: Submissão (Entrada)
- **O que:** LLM submete sua solução via template padronizado
- **Pré-requisito:** Documento `SUBMISSION.md` preenchido
- **Output:** Issue GitHub `[LLM-<nome>] Submissão: <titulo>`
- **Responsável:** LLM participante

### Gate 1: Triagem (Rápida)
- **O que:** Verifica se a submissão atende premissas mínimas (P1-P10)
- **Checklist:**
  - [ ] Tem pipeline T1→T2→T3?
  - [ ] Tem Evidence Validator?
  - [ ] Tem MCP Server?
  - [ ] Tem testes?
  - [ ] Documentação existe?
- **Tempo:** 15 minutos
- **Output:** Pass/Fail. Fail = retorna para LLM com feedback
- **Responsável:** Orchestrator (Kimi)

### Gate 2: Benchmark (Performance)
- **O que:** Mede T1 Diagnostician + Validator + T2 Recommender
- **Métricas:**
  - T1 < 200ms (aceitável) / < 100ms (ideal)
  - Validator < 250ms (aceitável) / < 150ms (ideal)
  - T2 < 10ms (runbook) / < 50ms (LLM)
  - Pipeline total < 333ms (threshold Luan)
- **Tempo:** 30 minutos
- **Output:** Relatório de benchmark comparativo
- **Responsável:** Orchestrator + CI

### Gate 3: Qualidade (Testes + Arquitetura)
- **O que:** Avalia cobertura de testes, qualidade de código, arquitetura
- **Checklist:**
  - [ ] Testes unitários > 80% cobertura
  - [ ] Testes de integração (fake Spark/CH)
  - [ ] CI passa (GitHub Actions)
  - [ ] Código review: separação T1/T2/T3 clara
  - [ ] ADR explica decisões arquiteturais
- **Score mínimo:** 70%
- **Tempo:** 1 dia
- **Output:** Scorecard por critério (C1-C8)
- **Responsável:** Orchestrator + Revisores

### Gate 4: UX/IDE (Integração)
- **O que:** Testa MCP Server, apply_fix, experiência no IDE
- **Checklist:**
  - [ ] MCP Server responde no IDE (Claude Code/Cursor)
  - [ ] `get_recommendations` retorna findings estruturados
  - [ ] `apply_fix` aplica correção e reporta sucesso/falha
  - [ ] Feedback claro ao engenheiro (skew_ratio, stage_id, etc.)
- **Tempo:** 1 dia
- **Output:** Screenshot/video da integração
- **Responsável:** Tester + Luan (opcional)

### Gate 5: Validação Real (Dados Reais)
- **O que:** Roda com event log real de produção
- **Checklist:**
  - [ ] Detecta skew real em job de produção
  - [ ] Validator confirma com evidência (7/7 regras)
  - [ ] Recomendação aplica correção e mede speedup
  - [ ] Sem falsos positivos (precision > 90%)
- **Score mínimo:** 85% (para merge)
- **Tempo:** 2-3 dias
- **Output:** Relatório de validação real com métricas
- **Responsável:** Luan Moreno + Equipe

### Gate 6: Merge (Integração)
- **O que:** Merge aprovado para branch principal
- **Pré-requisito:** Gates 1-5 passados, score >= 85%
- **Output:** PR mergeado, tag V1.5
- **Responsável:** Luan Moreno (decisão final)

---

## 6. Processo de Submissão LLM

### 6.1. LLMs Participantes

| LLM | Papel | Branch | Status |
|-----|-------|--------|--------|
| **Kimi** (esta) | Orchestrator + Participante | `gustocezar/feature/kimi-desacoplamento-geradores` | Submetida |
| **Codex** | Participante | `estudo/dataflint` (indireto) | A convidar |
| **Cowork** | Participante (base) | `gustocezar/feature/cowork-desacoplamento-geradores` | Submetida |
| **Spike** | Participante | `spike/apex-v0.1` | Submetida |

### 6.2. Template de Submissão

Cada LLM deve preencher:

```markdown
# Submissão: [Nome da Solução]

## LLM: [Nome da LLM]
## Data: [YYYY-MM-DD]
## Branch: [nome/branch]

## 1. Resumo Executivo (3 linhas)

## 2. Premissas Atendidas (P1-P10)
| # | Premissa | Status | Evidência |
|---|----------|--------|-----------|

## 3. Score por Critério (C1-C8)
| Critério | Score | Justificativa |
|----------|-------|---------------|

## 4. Arquitetura (Diagrama ou Descrição)

## 5. Benchmark (T1, Validator, T2, Pipeline)

## 6. Testes (Cobertura, CI)

## 7. Diferencial vs. DataFlint

## 8. Riscos e Mitigações

## 9. Roadmap para V1.5
```

### 6.3. Critérios de Desempate

Se duas LLMs empatarem no score:
1. **Performance:** Menor tempo de pipeline
2. **Testes:** Maior cobertura
3. **Documentação:** Mais ADRs e runbooks
4. **UX:** apply_fix funcional > apenas diagnóstico

---

## 7. Roteiro de Implementação Gate por Gate

### Semana 1: Setup do Framework
- [ ] Luan aprova este documento (ADR)
- [ ] Criar issue template para submissões LLM
- [ ] Configurar CI para rodar benchmarks automaticamente
- [ ] Criar `SUBMISSION.md` template

### Semana 2-3: Submissões
- [ ] Kimi refina submissão (compila, testa)
- [ ] Codex submete (se convidada)
- [ ] Spike formaliza submissão
- [ ] Cowork (base) avaliada como baseline

### Semana 4: Gates 1-3 (Triagem → Qualidade)
- [ ] Gate 1: Triagem de todas as submissões
- [ ] Gate 2: Benchmark comparativo
- [ ] Gate 3: Scorecard de qualidade

### Semana 5: Gates 4-5 (UX → Validação Real)
- [ ] Gate 4: Teste de integração IDE
- [ ] Gate 5: Validação com dados reais

### Semana 6: Gate 6 (Merge)
- [ ] Decisão final Luan
- [ ] Merge aprovado
- [ ] Tag V1.5

---

## 8. Documentos Relacionados

| Documento | Path | Descrição |
|-----------|------|-----------|
| Auto-avaliação Kimi | `docs/validacao/auto-avaliacao-kimi.md` | Avaliação crítica da branch kimi |
| Plano de Ação V1.5 | `docs/validacao/plano-acao-kimi-v1.5.md` | 5 semanas para recuperar kimi |
| Matriz Comparativa | `docs/comparacao/matriz-comparativa-4solucoes.md` | Comparação 4 soluções |
| Documento Comparativo | `docs/comparacao/comparativo-4-solucoes-spark-kimi.md` | Análise aprofundada |
| Apresentação | `docs/presentacoes/avaliacao-4solucoes.html` | 16 slides para Luan |

---

## 9. Próximo Passo

**Para Luan Moreno:**
1. Revisar e aprovar este framework
2. Decidir quais LLMs convidar (além das já participantes)
3. Aprovar premissas P1-P10 (há alguma que deva mudar?)
4. Ajustar pesos dos critérios C1-C8 (prioridades diferentes?)

**Para o Orchestrator (Kimi):**
1. Após aprovação, criar issues de submissão para cada LLM
2. Configurar CI para benchmark automatizado
3. Agendar checkpoints semanais

---

*Framework gerado por LLM Kimi. Aberto a refinamento por Luan Moreno e equipe.*
