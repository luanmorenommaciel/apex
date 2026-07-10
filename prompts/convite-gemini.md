# Prompt para Convidar Gemini (Google) — Apex Solution Championship

> Copie e cole este prompt no Gemini (gemini.google.com)
> Tempo estimado de resposta: 5-10 minutos para o plano, 30-60 minutos para codigo completo

---

## PROMPT (copie a partir daqui)

Voce foi convidado a participar do **Apex Solution Championship** — uma competicao de arquitetura de software onde multiplas LLMs geram solucoes para o mesmo problema, e um orchestrator (LLM Kimi) compara, valida e integra as melhores partes.

## O Problema

Criar uma ferramenta de **diagnostico de performance para Apache Spark** que:
1. Analisa event logs de jobs Spark (sem JAR no cluster)
2. Detecta padroes de problema (skew, shuffle, spill, memory, OOM, GC churn)
3. Valida evidencias antes de recomendar (Evidence Validator)
4. Recomenda correcoes (runbooks) via MCP Server integrado ao IDE (Claude Code/Cursor)
5. Aplica correcoes automaticamente (`apply_fix`)

## Requisitos Nao Negociaveis (Premissas P1-P10)

| # | Premissa | O que significa |
|---|----------|----------------|
| P1 | Pipeline T1→T2→T3 | T1: detecta padrao → Validator: valida evidencia → T2: recomenda runbook → T3: heuristico/LLM |
| P2 | Evidence Validator (7+ regras) | Regras deterministicas que confirmam/descartam finding |
| P3 | MCP Server | Protocolo MCP para IDE (Claude Code/Cursor) |
| P4 | apply_fix | Aplicar correcao automaticamente via MCP |
| P5 | ClickHouse como Source of Truth | Event logs parseados e persistidos em ClickHouse |
| P6 | Contrato job_id | Todo diagnostico referencia um app_id especifico |
| P7 | Zero JAR | Sem instrumentacao no cluster Spark |
| P8 | Testes + CI | Testes unitarios + CI/CD automatizado |
| P9 | Open Source | Codigo livre, sem dependencias de SaaS |
| P10 | 4 Tiers de Confianca | valid (0.9+), likely (0.7-0.9), suspected (0.5-0.7), unlikely (<0.5) |

## O Que Ja Existe (Contexto)

Tres solucoes foram submetidas:
1. **Cowork** (Python/CrewAI): 90% da V1, 21 testes, apply_fix funciona, MCP com 7 tools
2. **Spike** (Python+Go): Infra Docker completa (9 containers), 5 detectores, dashboards HyperDX
3. **Kimi** (Go): 20 arquivos Go, disciplina de engenharia, mas nao compila, 0 testes

## Sua Tarefa

Gere **a sua melhor solucao** para o Apex V1. Nao se preocupe em copiar as existentes — traga **sua perspectiva unica** como Gemini.

### Entregaveis Obrigatorios

1. **Arquitetura**: Diagrama ou descricao da sua solucao
2. **Codigo**: Implementacao completa (pode ser Python, Go, Rust, Java, ou outra linguagem)
3. **Testes**: Testes unitarios com > 80% cobertura
4. **Benchmark**: Tempo de T1 + Validator + T2 (pipeline completo)
5. **Documentacao**: ADR explicando suas decisoes arquiteturais
6. **Auto-avaliacao**: Score honesto (0-100%) nos criterios abaixo

### Critérios de Avaliacao (Pesos)

| Critério | Peso | O que mede |
|----------|------|-----------|
| Funcionalidade | 25% | Implementa P1-P10? |
| Performance | 15% | Pipeline < 333ms? |
| Testes | 15% | Cobertura > 80%? |
| Arquitetura | 10% | Separacao T1/T2/T3 clara? |
| Documentacao | 10% | ADRs, runbooks? |
| Infraestrutura | 10% | Docker, CI/CD? |
| UX/IDE | 10% | MCP funciona, apply_fix? |
| Extensibilidade | 5% | scenario.yaml, novos detectores faceis? |

### Template de Submissao

Preencha e entregue:

```markdown
# Submissao: [Nome da sua solucao]

## LLM: Gemini (Google)
## Data: [YYYY-MM-DD]

## 1. Resumo Executivo (3 linhas)

## 2. Premissas Atendidas (P1-P10)
| # | Premissa | Status (✅/⚠️/❌) | Evidencia |

## 3. Score por Criterio (C1-C8)
| Criterio | Score | Justificativa |

## 4. Benchmark
| Componente | Tempo (ms) |
|------------|------------|
| T1 | |
| Validator | |
| T2 | |
| Pipeline Total | |

## 5. Arquitetura
[Diagrama ou descricao]

## 6. O que faz MELHOR que as outras?

## 7. O que faz PIOR que as outras?

## 8. Codigo
[Link ou anexo com codigo completo]
```

## Instrucoes

1. **Seja honesto** sobre o que funciona e o que nao funciona
2. **Nao invente dados** — se nao rodou benchmark, diga "nao testado"
3. **Justifique decisoes** — por que escolheu Python/Go/Rust? Por que usou essa arquitetura?
4. **Codigo funcional** — prefira menos codigo que funciona a mais codigo que nao funciona
5. **Entregue em portugues** (ou ingles, se preferir)

## Diferencial Esperado do Gemini

Baseado no perfil do Gemini, esperamos que voce se destaque em:
- **Escalabilidade**: Arquitetura cloud-native, Kubernetes, auto-scaling
- **Multi-modulo**: Organizacao em servicos, microservicos se aplicavel
- **Performance**: Otimizacoes, caching, paralelismo
- **Infraestrutura**: Docker, Terraform, GCP/Azure/AWS

## O Que Acontece Depois

1. Voce entrega a submissao
2. O orchestrator (Kimi) roda os 6 Gates de validacao
3. Sua solucao e comparada com Cowork (90%), Spike (50%), Kimi (41%)
4. As melhores partes de cada LLM sao integradas na V1.5 final
5. Voce e creditado como contribuidor

## Pergunta Inicial

Como voce projetaria a infraestrutura do Apex para escalar de 1 job/dia para 10.000 jobs/dia? Considere ClickHouse, Kubernetes, e multi-tenant.

---

## FIM DO PROMPT
