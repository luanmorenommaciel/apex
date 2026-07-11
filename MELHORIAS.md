# MELHORIAS.md — cowork (F6: o que as outras fazem melhor e o que vamos adotar)

> Protocolo §3.2(a) · Fonte: scorecard verificado do round 1 (framework §4–§5) e
> docs públicos de avaliação — não o código das concorrentes.
> **Data:** 2026-07-10 · Adoções viram issues `COWORK-NNN` no catálogo.

| Origem | O que fazem melhor que nós | Adoção proposta | Issue | Status |
|---|---|---|---|---|
| **spike** | Ingestão produção-grade: loader Go com dedup por chave natural, muito mais robusto que nosso `log_poller.py` Python de 15s | Adotar o loader Go como ingestor oficial (é a A02 do merge) e aposentar o poller | COWORK-001 | aguarda ADR-006 |
| **spike** | Disciplina de ambiente: `uv` + pyproject + fakes de ClickHouse/Spark nos testes (nós testamos com subprocess e mocks ad-hoc) | Introduzir fakes p/ ClickHouse nos testes do v1-skeleton — hoje t1/crew só têm teste de lógica pura, não de query | COWORK-002 | aberta |
| **spike** | Guards de detector mais maduros (min_tasks=8, min_duration=5000 desde o dia 1) | Já adotado no G2 (`diagnostics.yaml`) | COWORK-003 | fechada |
| **kimi** | Latência-alvo do T1: ~136ms com runbooks JSON versionados; nosso T1 real é 333ms com recomendações inline no código | Extrair `RECOMMENDATIONS` do `t1_triage.py` para runbooks versionados (yaml/json) e perseguir <150ms | COWORK-004 | aberta |
| **kimi** | Empacotamento como serviço (CREI em Docker com porta e healthcheck); nosso diagnóstico é script avulso | Empacotar T1+validator como serviço no compose do V1 | COWORK-005 | aberta |
| **kimi** | Baseline negativo existia desde o início lá; nós só criamos no G1 | Adotado (G1) — lição: baseline nasce JUNTO com o primeiro detector, nunca depois | COWORK-006 | fechada |
| **codex** | Disciplina de specs/planos ANTES do código (`docs/superpowers/plans`, specs datadas); nós documentamos majoritariamente depois | Adotar plano-antes-do-código nas próximas features (o próprio protocolo F0 força isso) | COWORK-007 | aberta |
| **codex** | Harness local sem Docker (store NDJSON) — dev/teste do fluxo em segundos, sem plat-v0 de pé | Criar modo `--local` no ingest/T1 (NDJSON em vez de ClickHouse) para desenvolvimento e CI | COWORK-008 | aberta |
| **codex** | Suite de testes proporcionalmente maior que o código (44 testes p/ ~200 linhas) | Meta: cobrir `apply_fix` e MCP server com testes (hoje são os componentes MENOS testados da nossa branch) | COWORK-009 | aberta |
| **DataFlint** | ~14 detectores vs nossos 5; UI de DAG; alertas proativos | Cobertura via funil de gates (roadmap V2); UI é Visão — não copiar agora | COWORK-010 | roadmap V2 |
| **DataFlint** | Instalação de 1 linha (`spark.plugins`) | Nosso onboarding exige compose+env; simplificar bootstrap no V1 (1 script) | COWORK-011 | aberta |

## Honestidade sobre nós mesmos (o que o scorecard não mostra)

- Nossos componentes de MAIOR valor (`apply_fix`, MCP server) são os de MENOR
  cobertura de teste — invertido do que deveria ser (→ COWORK-009).
- O watch "contínuo" nunca rodou mais que minutos; estabilidade de horas é claim
  não testado.
- Vantagem assimétrica declarada: a cowork leu o código das outras no round 1
  (como avaliadora) — as adoções acima citam só material público/verificado, mas
  o conhecimento existe. O juiz externo deve pesar isso.
