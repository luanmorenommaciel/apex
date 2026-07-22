# Operador e Juiz - Passo a Passo (2026-07-22)

Este playbook separa os papeis. O operador demonstra ou executa o fluxo; o
juiz valida a evidencia. Nenhum deles deve alterar limiares, logs ou resultados
durante a avaliacao.

## Operador

1. Confirme a branch e o commit com `git status --short --branch` e
   `git log -1 --oneline`.
2. Abra o pacote de apresentacao em `docs/presentations/` e siga o roteiro de
   tres minutos.
3. Rode `python tools/run_commander_ui.py` e abra `http://127.0.0.1:8765/`.
4. Mostre o caso `job-42`: finding, evidencia por stage, Judge e before/after.
5. Na Demo MCP Segura, gere recomendacao e preview. Nao aplique a partir da UI.
6. Caso o juiz aprove uma mutacao de teste, execute o fluxo MCP com token e
   registre o transcript; depois compare a telemetria antes/depois.

## Juiz

| Pergunta | Evidencia minima |
|---|---|
| O baseline nao gera falso positivo? | `evidence/g1-baseline.log` |
| Os detectores oficiais disparam corretamente? | `evidence/g2-cenarios.log` |
| Existe dado real Spark? | `evidence/g3-real.log` |
| T1 depende de LLM? | `evidence/g4-t1.log` e codigo do caminho medido |
| O fix foi guardado e verificado? | `evidence/g5-ciclo.log` e `apply_verify.py` |
| O IDE consegue usar o MCP? | `evidence/g6-mcp-ide-gui-smoke-2026-07-18.log` |
| O runtime autonomo repete o ciclo? | `evidence/f7-remote-real-stack-run-29671461366-loop.log` |
| O Judge externo foi observado? | `evidence/crew-judge-external-llm-success-final-2026-07-19.json` |

## Veredito

Classifique cada pergunta como `confirmado`, `parcial` ou `nao confirmado`.
Registre o caminho exato da evidencia e qualquer dependencia operacional. Nao
use score de documento historico como prova; priorize log cru, teste e artefato
executavel da branch atual.

## Limites que devem ser declarados

- A UI e local, single-user e read-only.
- A demonstracao usa dados versionados, nao um ClickHouse produtivo vivo.
- O runner remoto requer maquina self-hosted com Docker, Spark 4.1.2 e S3A.
- O Judge externo e opcional e nunca aplica mudanca diretamente.
