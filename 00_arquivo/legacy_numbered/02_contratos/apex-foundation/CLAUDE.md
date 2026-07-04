# CLAUDE.md — contexto do projeto para agentes

Este arquivo é lido automaticamente pelo Claude Code no início de cada sessão. Ele dá ao agente
o contexto que um humano novo no time precisaria. Mantenha-o curto e verdadeiro.

## O que é o Apex

Um sistema de agentes que analisa performance de Spark/Databricks. Pega anti-patterns que o code
review deixa passar (antes do merge) e diagnostica jobs lentos/caros (depois do deploy).

## Arquitetura em uma frase

Listener captura telemetria do Spark → Collector (Go) move pro ClickHouse → Watchers
especializados detectam problemas → Coordinator junta → Judge revisa quando a confiança é baixa
→ Recommendation gera a sugestão de correção.

## Regras que o agente DEVE seguir

- **Respeite os contratos em `contracts/`.** Nunca invente um novo formato de evento ou de achado;
  use o que está combinado. Se precisar mudar um contrato, pare e abra uma proposta de ADR.
- **Trabalhe só na pasta do componente em questão.** Não crie dependência direta entre pastas de
  componentes — a comunicação é sempre pelo contrato.
- **Confiança vem de evidência, nunca de auto-avaliação.** Ao gerar um achado, baseie o `confidence`
  nos números medidos, não num "eu acho".
- **Antes de dizer que terminou:** o teste do cenário relevante em `scenarios/` precisa passar.

## Onde está o conhecimento

- Formatos e interfaces: `contracts/`
- Ambiente local pra rodar: `platform/` (use o Makefile dele)
- Casos de teste com bug plantado: `scenarios/`
- Decisões já tomadas: `docs/ADRs/`
