# Rascunho de Revisao das ADRs

> **Fonte canônica:** branch `gustocezar/feature/desacoplamento-geradores`  
> Ver `docs/adr-review-drafts.md` na branch para versão completa.

Contexto: estudo validado localmente pelo Augusto. Crew A revisa e decide. ADRs recebem comentários **apenas depois** da revisão do time.

## Posição do slice em cada ADR

| ADR | Issue | O que o slice reforca |
|---|---|---|
| ADR-001 — Onde o Apex roda? | #5 | Apex externo, não-intrusivo — sem JAR, sem listener, sem alterar SparkSession |
| ADR-002 — Quando Tier 2 dispara? | #6 | Skew é detectável deterministicamente; Tier 2 só entra em ambiguidade/baixa confiança |
| ADR-003 — Estado histórico (ClickHouse) | #7 | Finding sugere campos: watcher, stage, severity, confidence, evidence, root_cause, scenario_hash |
| ADR-004 — Linguagem dos componentes | #8 | Python = laboratório; Go = core futuro após contrato estável |
| ADR-001 Go OTel Collector | #22 | Slice não altera. Ponto de integração: Collector deve preservar campos para Watchers |
| ADR-003 Deprioritization | #24 | Baseline antes de divergência trouxe valor — slice revisável com evidência concreta |

## Comentário padrão para ADRs

Usar sempre como "nota de estudo local" — nunca "fechar" ADR sem decisão explícita da Crew A.
