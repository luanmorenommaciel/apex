# Apex Codex Round2

Branch: `codex-round2`

Estado: solucao de diagnostico Spark com gates G0-G6 validados, stack autonoma exercitada, workflow remoto verde, loop autonomo G3/G5 em Spark 4.1.2 validado localmente e tambem em GitHub Actions self-hosted, com evidencias em `evidence/`.

## O Que Tem Nesta Branch

Esta branch evoluiu do slice `skew_on_join_30x` v4 para uma esteira de diagnostico e correcao assistida para Spark:

```text
event log -> detector deterministico -> EvidenceValidator -> finding
-> recomendacao -> preview de diff -> apply guardado -> rerun -> compare
```

Ela nao deve ser apresentada como V1 completa ainda. O que ela prova bem e o loop funcional com evidencia: detectar um problema real, gerar uma correcao revisavel, aplicar com seguranca, reexecutar e provar que o finding sumiu. A rodada de 14/07 provou a mesma logica em stack autonoma da propria branch; em 15/07, o G6 remoto ficou verde no campeonato. Em 18/07, o Commander definiu Spark 4.1.2 como alvo e o SparkListener JVM foi promovido para caminho oficial dos jobs. Em 19/07, o loop G3/G5 autonomo rodou verde no GitHub Actions self-hosted.

## Resumo Executivo

| Area | Status | Evidencia |
|---|---|---|
| Baseline negativo | Fechado | `evidence/g1-baseline.log` |
| Deteccao sintetica oficial | Fechado | `evidence/g2-cenarios.log` |
| Dado real Spark | Fechado | `evidence/g3-real.log` |
| Latencia T1 sem LLM | Fechado | `evidence/g4-t1.log` - 226.991 ms |
| Ciclo detectar -> fix -> rerun -> limpo | Fechado | `evidence/g5-ciclo.log` |
| Contrato `apply_fix` + MCP stdio local | Fechado localmente | `evidence/g6-apply-fix-mcp-smoke.log` |
| MCP subprocess, estilo cliente externo | Fechado localmente | `apex/commander/mcp_stdio_cli.py`; `evidence/g6-apply-fix-mcp-smoke.log` |
| Docker autonomo paralelo | Fechado localmente | `docker-compose.autonomous.yml`; `evidence/g3-autonomous-diagnosis.json`; `evidence/g5-autonomous-ciclo.log` |
| SparkListener JVM real | Fechado localmente/runtime smoke | `listener-jvm/`; `evidence/g9-listener-jvm-spark-submit.log`; `evidence/g9-listener-jvm-failsafe-spark-submit.log` |
| Spark 4.1.2 + listener oficial | Fechado localmente com G3/G5 real | `docker-compose.yml`; `docker-compose.autonomous.yml`; `docker/spark/spark-defaults.conf`; `docker/autonomous/spark/spark-defaults.conf`; `evidence/f7-spark412-g5-compare-memory-2026-07-18.log`; `evidence/f7-spark412-final-focused-tests-2026-07-18.log`; `ISSUES.md` CODEX-041 a CODEX-044 |
| Loop CI stack autonoma | Fechado local e remotamente: `Apex Scenario Gate` executou `real-stack` verde no runner self-hosted | `scripts/f7_autonomous_stack_loop.py`; `.github/workflows/scenario-gate.yml`; `tests/test_f7_autonomous_stack_loop.py`; `evidence/f7-autonomous-stack-loop-20260718-real-local-6.log`; `evidence/f7-remote-real-stack-run-29671461366-loop.log`; `ISSUES.md` CODEX-045/CODEX-046/CODEX-062 |
| Crew/Judge provider opcional | Fechado como tool read-only | `apex/commander/crew_judge.py`; `apex/commander/judge_contract.py`; `apex/commander/judge_providers.py`; `evidence/crew-judge-real-provider-smoke-2026-07-19.json`; `ISSUES.md` CODEX-064/CODEX-065 |
| Crew.ai external smoke | Fechado com LLM externo real | `tools/crew_judge_provider_smoke.py`; `evidence/crew-judge-external-llm-success-final-2026-07-19.json`; `ISSUES.md` CODEX-065/CODEX-068 |
| MCP/IDE subprocess smoke | Fechado localmente, incluindo `crew_judge_diagnose` | `tools/mcp_ide_subprocess_smoke.py`; `evidence/g6-mcp-ide-subprocess-smoke.jsonl`; `evidence/g6-mcp-crew-judge-subprocess-smoke-2026-07-19.jsonl`; `ISSUES.md` CODEX-066 |
| Claude Code project MCP | Fechado em IDE GUI real | `.mcp.json`; `evidence/g6-mcp-ide-gui-smoke-2026-07-18.log` |
| Playbook IDE GUI MCP | Executado no Claude Code | `docs/playbooks/mcp-ide-gui-approval-smoke-2026-07-18.md`; `evidence/g6-mcp-ide-gui-smoke-2026-07-18.log` |
| Telemetria via MCP GUI | Fechada em read-only | `evidence/g6-mcp-ide-gui-telemetry-compare-2026-07-18.log`; `evidence/f6-mcp-gui-telemetry-compare-local-2026-07-18.log`; `evidence/f6-mcp-gui-telemetry-compare-tests-2026-07-18.log` |
| G6 oracle/drift smoke | Fechado remoto | `tools/g6_oracle_drift_smoke.py`; `.github/workflows/scenario-gate.yml`; `evidence/g6-oracle-drift-smoke.log`; `evidence/g6-oracle-drift-summary.json`; `evidence/g6-remote-workflow-latest-summary.json` |
| Loop agentico local | Fechado para checks locais, sem LLM e sem mutacao | `apex/commander/agentic_loop.py`; `tools/agentic_validation_loop.py`; `evidence/agentic-validation-loop-report.json` |
| Product readiness UI + Judge local | Fechado localmente | `docs/presentations/apex-product-readiness-2026-07-19.html`; `evidence/apex-product-readiness-2026-07-19-summary.json`; `apex/commander/product_report.py`; `tools/generate_product_report.py`; `ISSUES.md` CODEX-063 |
| Apex Commander UI local + demo MCP segura | Fechado localmente | `tools/run_commander_ui.py`; `docs/presentations/apex-commander-ui-mvp.html`; `docs/guides/apex-commander-ui-demo.md`; `apex/commander/ui_server.py` |
| Especificacao tecnica 15/07 | Atualizada para juiz | `docs/specs/apex-codex-technical-spec-2026-07-15.md` |
| Comparacao de produto atual | Atualizada em 22/07 | `docs/architecture/apex-codex-vs-dataflint-2026-07-22.md` |
| Apresentacao Codex 15/07 | Atualizada para juiz | `docs/presentations/apex-codex-solucao-end-to-end-2026-07-15.html` |
| Autoavaliacao | Fechada | `docs/autoavaliacao.md` |
| Catalogo de issues | Fechado/aberto conforme item | `ISSUES.md` |
| ADRs formais | Criadas | `docs/adr/ADR-001-onde-o-apex-roda.md`; `docs/adr/ADR-002-t1-antes-de-crew-judge.md`; `docs/adr/ADR-003-spark-alvo-da-branch-codex.md`; `docs/adr/ADR-004-mcp-ide-e-apply-fix-guardado.md` |
| Plano F0/F5 | Fechado | `PLANO.md` |

## Resultado Mais Importante

Caso real validado: skew em join.

| Metrica | Antes | Depois |
|---|---:|---:|
| `app_id` | `app-20260712053414-0001` | `app-20260712131734-0004` |
| Finding count | 1 | 0 |
| Severidade | high | n/a |
| Skew ratio valido | 29.4 | 0 |
| Shuffle read bytes | 1.157.481 | 0 |

Leitura: o Apex detectou skew real, gerou preview de correcao, aplicou com token/hash/verify, reexecutou o job e comprovou que o finding caiu para zero.

Rodada autonoma 14/07:

| Metrica | Antes autonomo | Depois autonomo |
|---|---:|---:|
| `app_id` | `app-20260714112858-0003` | `app-20260714113809-0004` |
| Finding count | 1 | 0 |
| Severidade | high | n/a |
| Skew ratio valido | 29.4 | 0 |
| Shuffle read bytes | 1.157.481 | 0 |

Leitura: o mesmo ciclo G3/G5 foi repetido na stack autonoma da branch, com event log novo e sem dependencia da stack historica `plat-v0`.

## Fluxo Didatico Em Macro Passos

```mermaid
flowchart LR
    A["1. Job Spark"] --> B["2. Listener e event log"]
    B --> C["3. Telemetria por job e stage"]
    C --> D["4. T1 + EvidenceValidator"]
    D --> E["5. Finding e recomendacao"]
    E --> F["6. Preview revisavel"]
    F --> G["7. Apply guardado + rerun"]
    G --> H["8. Compare e proxima decisao"]

    D -. "evidencia insuficiente" .-> M["manual_review"]
    H -. "sem melhoria" .-> I["Issue ou nova recomendacao"]
```

Para uma explicacao curta, use
`docs/guides/apex-commander-macro-flow-2026-07-22.md`. Para uma demonstracao
controlada, use `docs/playbooks/apex-operator-judge-2026-07-22.md`.

### Estado De Um Finding

```mermaid
stateDiagram-v2
    [*] --> Collected: event log ou listener
    Collected --> Validated: T1 + EvidenceValidator aceita
    Collected --> ManualReview: evidencia incompleta
    Validated --> Recommended: recommend_fix
    Recommended --> Previewed: preview_fix sem mutacao
    Previewed --> Applied: token + hash + apply_root validos
    Previewed --> Rejected: humano nao aprova
    Applied --> Rerun: verify confirma o hash final
    Rerun --> Resolved: findings = 0 e metrica melhora
    Rerun --> FollowUp: finding persiste ou piora
    ManualReview --> FollowUp
    Rejected --> FollowUp
    Resolved --> [*]
    FollowUp --> Recommended
```

O estado `Applied` nao pode ser alcançado pela UI local. Ele exige o contrato
MCP, uma aprovacao humana e a verificacao de token, hash e raiz permitida.

### Sequencia Operacional

```mermaid
sequenceDiagram
    participant Eng as Engenheiro
    participant Spark as Spark + Listener
    participant Store as Event log / Store
    participant T1 as T1 + Validator
    participant MCP as MCP / IDE
    participant Guard as Preview + apply_fix
    participant Compare as Rerun + Compare

    Eng->>Spark: submete job
    Spark->>Store: emite event log e telemetria
    Store->>T1: entrega job_id, stages e metricas
    T1->>MCP: finding validado + recomendacao
    MCP->>Guard: solicita preview (somente leitura)
    Guard-->>Eng: diff e escopo da mudanca
    Eng->>Guard: aprova com token
    Guard->>Guard: aplica, verifica hash e apply_root
    Guard->>Spark: reexecuta job corrigido
    Spark->>Compare: publica nova telemetria
    Compare-->>Eng: before/after e decisao
```

## Arquitetura Da Solucao

```mermaid
flowchart TD
    LOG["Spark event log<br/>real ou sintetico"] --> T1["T1 deterministico<br/>diagnostic_mvp.py"]
    T1 --> VAL["EvidenceValidator<br/>evidence_validator.py"]
    VAL --> FIND["Finding<br/>kind, severity, evidence"]
    FIND --> REC["Recommendation<br/>recommendations.py"]
    REC --> PREV["Preview diff<br/>fix_preview.py"]
    PREV --> APPLY["Apply guardado<br/>apply_verify.py"]
    APPLY --> RERUN["Rerun Spark<br/>spark_rerun_template.py"]
    RERUN --> CMP["Compare telemetry<br/>telemetry_compare.py"]
    CMP --> OUT["Resultado<br/>limpo ou issue aberta"]
```

## Componentes Principais

| Componente | Caminho | Papel |
|---|---|---|
| Detectores deterministicos | `apex/commander/diagnostic_mvp.py` | Detecta skew, GC, shuffle/spill, OOM e cartesian product |
| Validador de evidencia | `apex/commander/evidence_validator.py` | Confere se o finding tem evidencia suficiente |
| Telemetria | `apex/commander/telemetry.py` | Normaliza `job_id`, `app_id`, stages, tasks e plano |
| ClickHouse adapter | `apex/commander/clickhouse_adapter.py`, `apex/commander/clickhouse_findings.py` | Store e adaptadores para testes e persistencia de findings |
| ClickHouse HTTP client | `apex/commander/clickhouse_http_client.py` | Cliente para ambiente ClickHouse real |
| MCP stdio | `apex/commander/mcp_stdio_server.py` | Exposicao local de tools para agente/IDE |
| Recomendacoes | `apex/commander/recommendations.py` | Converte finding em recomendacao |
| Preview de fix | `apex/commander/fix_preview.py` | Gera diff antes de qualquer apply |
| Apply guardado | `apex/commander/apply_verify.py` | Aplica com token, hash, root permitido e verificacao |
| Rerun/compare | `apex/commander/rerun_orchestrator.py`, `apex/commander/telemetry_compare.py` | Reexecuta de forma guardada e compara telemetria antes/depois |
| Template Spark rerun | `apex/commander/spark_rerun_template.py` | Monta comando Spark para reexecucao controlada |

## Gates Validados

| Gate | O que prova | Artefato |
|---|---|---|
| G0 | Fundacao/testes/contratos iniciais | `evidence/g0-testes.log` |
| G1 | Baseline saudavel nao gera falso positivo | `evidence/g1-baseline.log` |
| G2 | Os 5 cenarios oficiais disparam severidade esperada | `evidence/g2-cenarios.log` |
| G3 | Job real Spark multicore bate o comportamento sintetico | `evidence/g3-real.log` |
| G4 | T1 deterministico roda abaixo de 1s sem LLM | `evidence/g4-t1.log` |
| G5 | Ciclo completo detectar -> aplicar -> reexecutar -> limpar | `evidence/g5-ciclo.log` |
| G5 autônomo | Mesmo ciclo na stack autônoma sem `plat-v0` | `evidence/g5-autonomous-ciclo.log` |
| G6 local | Contrato `apply_fix` e smoke MCP stdio local | `evidence/g6-apply-fix-mcp-smoke.log` |
| G7 local | Compose autônomo sobe sem `spark-plat-v0-*`, Spark grava event log, G3/G5 passam e listener JVM roda | `evidence/g3-autonomous-diagnosis.json`; `evidence/g5-autonomous-ciclo.log`; `evidence/g9-listener-jvm-spark-submit.log` |
| F7 loop | Runner orquestra G3/G5 autônomo em Spark 4.1.2, fechou execução real local e execução remota verde no GitHub Actions/self-hosted | `scripts/f7_autonomous_stack_loop.py`; `.github/workflows/scenario-gate.yml`; `evidence/f7-autonomous-stack-loop-20260718-real-local-6.log`; `evidence/f7-remote-real-stack-run-29671461366-loop.log` |
| G8 local | Política Crew/Judge futura sem LLM obrigatória | `evidence/g8-agentic-loop-python.log` |
| G9 local | Listener JVM compila, gera JAR, carrega via `spark-submit --jars`, emite NDJSON e não derruba job em fail-mode | `evidence/g9-listener-jvm-spark-submit.log`; `evidence/g9-listener-jvm-output.ndjson`; `evidence/g9-listener-jvm-failsafe-spark-submit.log` |

## Cenarios Oficiais Cobertos

Os cenarios vieram do pacote comum:

```text
pacote-comum/scenarios/no_skew_baseline.yaml
pacote-comum/scenarios/skew_on_join_30x.yaml
pacote-comum/scenarios/gc_pressure_25pct.yaml
pacote-comum/scenarios/shuffle_spill_disk.yaml
pacote-comum/scenarios/oom_on_aggregation.yaml
pacote-comum/scenarios/cartesian_product.yaml
```

Resultado G2:

| Cenario | Resultado esperado | Status |
|---|---|---|
| no skew baseline | zero warning+ | fechado |
| skew on join | high | fechado |
| GC pressure | critical | fechado |
| shuffle spill disk | critical | fechado |
| OOM aggregation | critical | fechado |
| cartesian product | critical | fechado |

## Seguranca Do Apply

O apply nao e uma edicao livre feita por agente. Ele passa por controles:

| Controle | Motivo |
|---|---|
| Preview obrigatorio | Mostra o diff antes de alterar arquivo |
| Approval token | Amarra aprovacao ao `job_id`, recomendacao, alvo e hashes |
| `apply_root` | Bloqueia escrita fora do workspace permitido |
| Hash antes/depois | Garante que o arquivo aplicado e exatamente o previsto |
| Verify | Confirma que o arquivo final bate com o hash esperado |
| Rerun/compare | Prova se a correcao melhorou a execucao |

## Documentacao Importante

| Documento | Uso |
|---|---|
| `PLANO.md` | Plano F0/F5, premissas L1-L9, gates e gaps |
| `ISSUES.md` | Catalogo formal CODEX-001 em diante |
| `docs/autoavaliacao.md` | Scorecard C1-C6 e Captain's Report |
| `docs/specs/skew-slice-v4.md` | Especificacao tecnica atualizada da solucao Codex Round2 |
| `docs/architecture/apex-codex-vs-dataflint-2026-07-22.md` | Comparacao atual Codex × DataFlint, com fontes oficiais e limites declarados |
| `docs/guides/apex-commander-macro-flow-2026-07-22.md` | Fluxo didatico de oito passos para apresentar a solucao |
| `docs/playbooks/apex-operator-judge-2026-07-22.md` | Passo a passo do operador e criterios verificaveis do juiz |
| `docs/specs/apex-codex-technical-spec-2026-07-15.md` | Especificacao tecnica reprodutivel da branch Codex |
| `docs/presentations/apex-codex-luan-3min-2026-07-19.pptx` | Deck executivo atual de quatro slides para o Luan |
| `docs/presentations/apex-commander-one-slide-2026-07-19.html` | Resumo visual de uma pagina para abertura da demonstracao |
| `docs/presentations/apex-codex-luan-3min-2026-07-19.md` | Roteiro falado de tres minutos, com tempo por slide |
| `docs/presentations/apex-codex-solucao-end-to-end-2026-07-14.html` | Apresentacao end-to-end da nossa solucao |
| `docs/presentations/apex-codex-solucao-end-to-end-2026-07-15.html` | Apresentacao final da nossa solucao para o juiz |
| `docs/presentations/apex-product-readiness-2026-07-19.html` | Relatorio HTML de prontidao produto/Judge local com score 100/100 no pacote de evidencias, before/after remoto, MCP GUI, T1 e gaps conhecidos |
| `docs/presentations/apex-commander-ui-mvp.html` | UI local navegavel: caso `job-42`, telemetria, Judge, recomendacao e preview seguro |
| `docs/guides/apex-commander-ui-demo.md` | Roteiro de 10 minutos para testar a UI com o time |
| `docs/superpowers/specs/2026-07-19-apex-commander-ui-local-app-design.md` | Decisoes, rotas e limites de seguranca da UI local |
| `docs/presentations/apex-codex-projeto-luan-2026-07-14.html` | Apresentacao executiva para o Luan |
| `docs/architecture/llm-solution-validation-framework-2026-07-09.md` a `2026-07-15.md` | Historico do campeonato; nao usar como fotografia atual da branch |

## Apresentacoes

Pacote atual para apresentar ao Luan:

```text
docs/presentations/apex-codex-luan-3min-2026-07-19.pptx
docs/presentations/apex-commander-one-slide-2026-07-19.html
docs/presentations/apex-codex-luan-3min-2026-07-19.md
docs/presentations/apex-commander-ui-mvp.html
docs/presentations/apex-product-readiness-2026-07-19.html
```

Sugestao:

1. Abra o deck de tres minutos e use o roteiro correspondente.
2. Demonstre o produto atual com `python tools/run_commander_ui.py` e `apex-commander-ui-mvp.html`.
3. Para perguntas sobre prontidao e evidencias, abra `apex-product-readiness-2026-07-19.html`.
4. Para uma comparacao de produto atual, use apenas `apex-codex-vs-dataflint-2026-07-22.md`.
5. Os frameworks comparativos de 09/07 a 15/07 permanecem como historico e nao devem ser usados como fotografia atual.

## Produto Visual Local

O MVP navegavel do **Apex Commander UI** esta em
`docs/presentations/apex-commander-ui-mvp.html`. Para usa-lo como aplicacao
local, sem depender de rede ou de credenciais, execute:

```powershell
python tools/run_commander_ui.py
```

Abra `http://127.0.0.1:8765/`. A UI e apenas de leitura e mostra evidencia,
findings, Crew/Judge, before/after e Fix Center. O roteiro completo esta em
`docs/guides/apex-commander-ui-demo.md`.

Na secao **Demo MCP Segura**, a interface executa `recommend_fix` e um preview
real para o job de demonstracao. Ela usa um alvo fixo, remove o approval token
da resposta e nao oferece `apply_fix`.

Para manter a apresentacao coerente, `job-42` e o identificador do caso. As
linhas `before-job` e `after-job` sao as duas execucoes de telemetria exibidas
na comparacao antes/depois desse mesmo caso.

## Como Validar A Branch

Os logs crus ja estao em `evidence/`. Para nova validacao completa, use os gates do pacote comum e os scripts locais.

Leitura rapida:

```text
evidence/g1-baseline.log
evidence/g2-cenarios.log
evidence/g3-real.log
evidence/g4-t1.log
evidence/g5-ciclo.log
evidence/g6-apply-fix-mcp-smoke.log
evidence/agentic-validation-loop-report.json
docs/specs/apex-codex-technical-spec-2026-07-15.md
docs/architecture/apex-codex-vs-dataflint-2026-07-22.md
evidence/g7-autonomous-compose-config.log
evidence/g8-agentic-loop-python.log
evidence/g9-listener-jvm-environment.log
```

Suite historica:

```powershell
python -m pytest tests -q
```

Observacao: em Windows, alguns comandos antigos podem precisar de basetemp local por permissao no diretorio temporario do usuario. Isso foi registrado durante G5.

## Limites Reais Da Primeira Entrega

| Limite | Impacto e tratamento atual |
|---|---|
| UI local e single-user | A demonstracao roda somente em `127.0.0.1`; nao ha autenticacao, RBAC ou sessao compartilhada. |
| UI nao aplica mudancas | Por seguranca, a UI so permite recomendacao e preview no caso fixo. `apply_fix` continua no MCP/IDE, com aprovacao humana. |
| Demo baseada em evidencia versionada | O caso `job-42` e reproduzivel, mas a UI ainda nao lista jobs de um ClickHouse produtivo em tempo real. |
| Judge externo | Crew.ai com LLM externo foi observado, mas a matriz de baixa confianca, evidencia incompleta e rejeicao do validator ainda deve crescer. |
| Runner self-hosted | O workflow real depende de runner com Docker, Spark 4.1.2 e S3A/MinIO preparados; o ciclo de vida dele precisa de dono operacional. |

## Aderencia Ao Pedido Do Luan

| Pedido/criterio | Status |
|---|---|
| Baseline negativo | Cumpre |
| Detectores oficiais | Cumpre |
| Dado real Spark | Cumpre |
| Latencia sem LLM | Cumpre |
| Ciclo apply/rerun limpo | Cumpre funcionalmente |
| ClickHouse/job_id/app_id | Parcial |
| MCP/apply_fix local | Cumpre localmente |
| MCP subprocess estilo cliente externo | Cumpre localmente |
| IDE real | Fechado em Claude Code GUI: `tools/list`, `recommend_fix`, `preview_recommendation` e `apply_fix` |
| SparkListener real | Cumpre localmente/runtime smoke |
| Crew.ai/Judge | Cumpre localmente: tool read-only, contrato anti-alucinação, provider Crew.ai opcional e execução real com LLM externo observada |
| Plataforma Docker standalone | Cumpre localmente em Spark 4.1.2: compose sobe, listener oficial carrega, G3/G5 reais passam |

## Proximos Passos Recomendados

1. Definir dono operacional do runner self-hosted `apex-local-GUSTUS` e da retencao de evidencias.
2. Monitorar o G6 agendado e manter o job legado `gate` verde no CI remoto.
3. Evoluir a UI de demonstracao para consulta multi-job com dados vivos, autenticacao e RBAC.
4. Expandir a matriz do Judge para incerteza, evidencia incompleta e rejeicao pelo validator, mantendo-o depois de T1.
5. Priorizar agente de cluster, revisao de PR ou observabilidade de frota somente apos definir o proximo caso real.

## Estado De Publicacao

Esta branch tem historico publicado em `campeonato/codex-round2`. Antes de publicar novas mudancas, confirme:

```powershell
git status --short --branch
git log --oneline --decorate -5
```

Nao faca push de alteracoes novas sem revisao quando a branch remota estiver sendo avaliada.
