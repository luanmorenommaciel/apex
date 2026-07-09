# Template de Submissão LLM — Apex Solution Validation Framework

> Preencha este template para submeter sua solução ao framework de validação.
> Salve como: `SUBMISSION-[LLM-NAME].md` na raiz do seu branch.
> Exemplo: `SUBMISSION-Kimi.md`

---

## 1. Identificação

| Campo | Valor |
|-------|-------|
| **Nome da LLM** | [Ex: Kimi, Codex, GPT-4, Claude, etc.] |
| **Versão/Modelo** | [Ex: Kimi k1.5, GPT-4o, Claude 3.5 Sonnet] |
| **Data da Submissão** | [YYYY-MM-DD] |
| **Branch** | [Ex: `gustocezar/feature/kimi-desacoplamento-geradores`] |
| **Autor/Contribuinte** | [Nome do usuário que orquestrou a LLM] |
| **Tempo de Desenvolvimento** | [Ex: 3 dias, 2 semanas] |

---

## 2. Resumo Executivo (máx 5 linhas)

> Descreva em 3-5 linhas o que sua solução faz, qual é o diferencial, e por que ela deveria ser escolhida.

```
[Sua descrição aqui...]
```

---

## 3. Premissas do Luan Atendidas (P1-P10)

Marque com ✅ (entregue), ⚠️ (parcial), ou ❌ (ausente). Para cada item, forneça evidência (link para arquivo ou linha de código).

| # | Premissa | Status | Evidência (path + linha) |
|---|----------|--------|--------------------------|
| P1 | Pipeline T1→T2→T3 | [✅/⚠️/❌] | `[path:linha]` |
| P2 | Evidence Validator (7+ regras) | [✅/⚠️/❌] | `[path:linha]` |
| P3 | MCP Server | [✅/⚠️/❌] | `[path:linha]` |
| P4 | apply_fix via MCP | [✅/⚠️/❌] | `[path:linha]` |
| P5 | ClickHouse como Source of Truth | [✅/⚠️/❌] | `[path:linha]` |
| P6 | Contrato job_id | [✅/⚠️/❌] | `[path:linha]` |
| P7 | Zero JAR | [✅/⚠️/❌] | `[path:linha]` |
| P8 | Testes + CI | [✅/⚠️/❌] | `[path:linha]` |
| P9 | Open Source | [✅/⚠️/❌] | `[path:linha]` |
| P10 | 4 Tiers de Confiança | [✅/⚠️/❌] | `[path:linha]` |

**Score P1-P10:** [X/10] premissas atendidas

---

## 4. Score por Critério (C1-C8)

Avalie sua própria solução com honestidade. Use a escala 0-100% para cada critério.

| # | Critério | Peso | Score (0-100%) | Justificativa (máx 3 linhas) |
|---|----------|------|----------------|------------------------------|
| C1 | Funcionalidade | 25% | [__%] | |
| C2 | Performance | 15% | [__%] | |
| C3 | Testes | 15% | [__%] | |
| C4 | Arquitetura | 10% | [__%] | |
| C5 | Documentação | 10% | [__%] | |
| C6 | Infraestrutura | 10% | [__%] | |
| C7 | UX/IDE | 10% | [__%] | |
| C8 | Extensibilidade | 5% | [__%] | |

**Score Total Ponderado:** [__%] (fórmula: C1×0.25 + C2×0.15 + C3×0.15 + C4×0.10 + C5×0.10 + C6×0.10 + C7×0.10 + C8×0.05)

---

## 5. Benchmark (Dados Reais)

Rode o benchmark 3 vezes e reporte a média. Use o job_id `app-20260706035238-0001` ou outro job real.

| Componente | Run 1 (ms) | Run 2 (ms) | Run 3 (ms) | Média (ms) | vs. Threshold |
|------------|------------|------------|------------|------------|---------------|
| T1 Diagnostician | | | | | < 200ms ideal |
| Validator (7 regras) | | | | | < 250ms ideal |
| T2 Recommender | | | | | < 10ms (runbook) |
| **Pipeline Total** | | | | | **< 333ms** |

**Comando usado para benchmark:**
```bash
# Cole o comando aqui
```

---

## 6. Arquitetura

### 6.1 Diagrama (opcional: Mermaid ou descrição)

```mermaid
# Ou descreva em texto:
# [Componente A] → [Componente B] → [Componente C]
```

### 6.2 Separação T1/T2/T3

| Tier | Componente | Responsabilidade | Arquivo Principal |
|------|-----------|-------------------|-----------------|
| T1 | | | |
| T2 | | | |
| T3 | | | |

### 6.3 Tecnologias

| Camada | Tecnologia | Versão | Justificativa |
|--------|-----------|--------|---------------|
| Linguagem | [Python/Go/Java/etc.] | | |
| Framework | [CrewAI/puro/etc.] | | |
| Banco de Dados | [ClickHouse/etc.] | | |
| Infra | [Docker/Compose/etc.] | | |
| CI/CD | [GitHub Actions/etc.] | | |

---

## 7. Testes

### 7.1 Cobertura

```bash
# Cole o output do comando de cobertura
# Ex: pytest --cov=src tests/
```

**Cobertura total:** [__%]

### 7.2 Testes Unitários

| Módulo | # Testes | Status | Arquivo |
|--------|----------|--------|---------|
| | | | |

### 7.3 Testes de Integração

| Cenário | Status | Evidência |
|---------|--------|-----------|
| | | |

### 7.4 CI/CD

| Pipeline | Status | Link |
|----------|--------|------|
| | | |

---

## 8. Diferencial vs. DataFlint

| Dimensão | Sua Solução | DataFlint | Vantagem |
|----------|------------|-----------|----------|
| Intrusão | | JAR obrigatório | |
| Pipeline | | Alerta binário | |
| IDE | | Dashboard apenas | |
| Confiança | | Sem tiers | |
| Custo | | SaaS pago | |
| Customização | | 14 alertas fixos | |

---

## 9. Riscos e Mitigações

| # | Risco | Probabilidade | Impacto | Mitigação |
|---|-------|--------------|---------|-----------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

---

## 10. Roadmap para V1.5

| Fase | Tarefa | Estimativa | Responsável |
|------|--------|------------|-------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

---

## 11. Auto-avaliação (Honestidade)

> Responda com sinceridade. Isso não penaliza — ajuda o orchestrator a entender onde você precisa de ajuda.

**O que sua solução faz MELHOR que as outras?**
```
[Resposta...]
```

**O que sua solução faz PIOR que as outras?**
```
[Resposta...]
```

**O que você GOSTARIA de ter implementado mas não conseguiu?**
```
[Resposta...]
```

**O que você precisa da equipe/Luan para melhorar?**
```
[Resposta...]
```

---

## 12. Anexos

Liste todos os arquivos relevantes da sua solução:

```
docs/
  adr/adr-XXX.md
  runbooks/skew_on_join.json
  presentacao/slides.html
src/
  t1_diagnostician.py
  validator.py
  t2_recommender.py
  mcp_server.py
tests/
  test_t1.py
  test_validator.py
Dockerfile
docker-compose.yml
.github/workflows/ci.yml
```

---

## Checklist Final (antes de submeter)

- [ ] Todos os campos P1-P10 preenchidos
- [ ] Benchmark rodado 3x com média
- [ ] Score C1-C8 calculado honestamente
- [ ] Auto-avaliação respondida com sinceridade
- [ ] Arquivo salvo como `SUBMISSION-[LLM-NAME].md`
- [ ] Commitado na branch
- [ ] Issue GitHub criada: `[LLM-<nome>] Submissão: <titulo>`

---

*Template gerado pelo Orchestrator (LLM Kimi). Versão 1.0 — 2026-07-09*
