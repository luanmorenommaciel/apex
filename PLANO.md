# PLANO.md — F0 Codex Round 2

Branch local: `codex-round2`
Base de avaliacao: `pacote-comum/apex-v1-spec-reproducivel.md`
Estado usado: raio-x local ja levantado, sem nova reestruturacao.

## Objetivo Do F0

Formalizar o estado atual da engine Codex contra a spec comum da rodada 2 antes
de qualquer reestruturacao maior.

Este F0 nao tenta maquiar a branch para caber na spec. Quando a implementacao
atual cobre uma parte do requisito, o status fica como `parcial`.

## Premissas L1-L9

| Premissa | Status | Evidencia atual |
| --- | --- | --- |
| L1 Pipeline: Spark Envy Docker -> SparkListener -> ClickHouse -> Crew.ai -> MCP | Parcial | Existe ClickHouse/store, MCP stdio/subprocess, compose autonomo paralelo, listener JVM promovido para caminho oficial dos jobs, G3/G5 completos reexecutados em Spark 4.1.2 na stack autonoma, MCP aprovado/validado em Claude Code GUI e `crew_judge_diagnose` como tool read-only com provider Crew.ai opcional. Ainda falta observar Crew.ai com LLM externo configurado. |
| L2 `docker compose up` sobe tudo sem configuracao manual | Cumpre localmente | `docker-compose.yml` raiz usa Spark 4.1.2 e monta o listener oficial; `docker-compose.autonomous.yml` renderiza em Spark 4.1.2, builda a imagem `apex-autonomous-spark:4.1.2-s3a`, sobe ClickHouse/MinIO/Spark master/worker e validou G3/G5 em runtime real. |
| L3 Listener via `spark.extraListeners`, fail-safe | Cumpre | `listener-jvm/` implementa classe real fail-safe; `gradle selfTest jar` passa em container; `spark-submit --jars` registrou `apex.commander.spark.ApexSparkListener`; em F7 o listener foi promovido para `spark-defaults.conf`, compose raiz/autonomo e `build_spark_submit_rerun_command` com `--jars`, `spark.extraListeners`, output e fail-safe default. Evidencias: `evidence/g9-listener-jvm-spark-submit.log`, `evidence/g9-listener-jvm-output.ndjson`, `evidence/g9-listener-jvm-failsafe-spark-submit.log`, `evidence/f7-spark412-official-listener-tests-2026-07-18.log`. |
| L4 ClickHouse com schema definido, query por `app_id`/`job_id` | Cumpre localmente | `docs/specs/apex_telemetry_v1.sql` foi copiado literalmente do pacote comum em G0; `apex/commander/telemetry.py` carrega `job_id` e `app_id`; adapters consultam por `job_id`; a stack autonoma validou leitura/diagnostico por `app_id` em `evidence/g3-autonomous-diagnosis.json`. |
| L5 Diagnostico agentico Crew.ai explica o problema | Parcial avancado | Diagnostico T1 continua deterministico em `apex/commander/diagnostic_mvp.py`; `apex/commander/crew_judge.py` adiciona `crew_judge_diagnose` read-only após T1 + `EvidenceValidator`; `apex/commander/judge_contract.py` valida decisão/citações; `apex/commander/judge_providers.py` tem provider deterministico, fallback `noop` e provider Crew.ai opcional por `APEX_CREW_JUDGE_ENABLED=1`. Evidencia: `evidence/crew-judge-real-provider-smoke-2026-07-19.json`. |
| L6 Fix via MCP no IDE + "aplica nossa sugestao" edita o codigo do cliente | Cumpre | Existe MCP stdio e apply guardado em `apex/commander/apply_verify.py`; `apply_fix` foi exposto como contrato local guardado, validado por smoke subprocesso e validado em Claude Code GUI real com `tools/list`, `recommend_fix`, `preview_recommendation` e `apply_fix` dentro do `apply_root`. Evidencia: `evidence/g6-mcp-ide-gui-smoke-2026-07-18.log`. |
| L7 Decisoes de arquitetura registradas em ADR | Cumpre localmente | ADRs formais criadas em `docs/adr/`: onde o Apex roda, T1 antes de Crew/Judge, Spark alvo da branch Codex e MCP/`apply_fix` guardado. |
| L8 Nao focar Databricks/serverless agora — Spark puro primeiro | Cumpre | A branch trabalha com Spark event log, ClickHouse/local store e MCP; nao ha implementacao Databricks/serverless. |
| L9 Minimo viavel de cada componente antes de expandir qualquer um | Parcial avancado | Ha MVPs locais para ingest, store, detectores, validator, MCP GUI, apply guardado, rerun, Docker/Compose autonomo, SparkListener JVM real/fail-safe e Crew/Judge plugável. Continua parcial porque execução Crew.ai com LLM externo real ainda nao foi observada. |

## Gates G0-G6 Da Spec Comum

| Gate comum | Status Codex | Evidencia | Observacao sobre encaixe |
| --- | --- | --- | --- |
| G0 build + testes em ambiente limpo | Parcial | Ultima suite local: `138 passed, 2 skipped`; ha `__pycache__` e diretorios `.pytest-*` nao rastreados. | O numero difere da referencia comum de 52 testes porque a branch Codex tem historico proprio e mais testes locais. |
| G1 baseline `none`: zero finding em job saudavel | Parcial | `tests/test_commander_negative_baselines.py` e `tests/test_commander_v01.py` cobrem job saudavel/balanceado. | Cobre o comportamento, mas nao pelo contrato `scenario.yaml` classe `none` da spec comum. |
| G2 cada detector pega seu cenario sintetico | Parcial | `tests/test_commander_detectors.py` cobre skew, spill/shuffle, GC, OOM e AQE localmente. | Nao ha ainda pacote completo de cenarios v1 comuns (`data_skew_on_join_key`, `gc_pressure`, `shuffle_spill`, `oom_task_failure`, `cartesian_product`, `none`). |
| G3 sintetico ~= real no cluster + >=8 tasks reais | Parcial | `real_log.ndjson`, `oracle/compare.py`, docs v4 registram comparacao sintetico vs real para skew. | Cobre o slice de skew; nao cobre todos os detectores nem uma execucao cluster atual pelo pacote comum. |
| G4 T1 < 1s sem LLM; LLM so confidence < 0.6 | Parcial avancado | `evidence/g4-t1.log` mede o caminho T1 deterministico contra `app-20260712053414-0001`: 226.991 ms, com `EvidenceValidator` aceitando o finding e grep sem referencias a LLM/API no caminho medido; `crew_judge_diagnose` agora implementa o ponto de escalonamento read-only sem entrar no caminho quente. | A latencia T1 esta abaixo de 1s; provider Crew.ai existe, mas chamada com LLM externo real depende de ambiente e segue aberta em CODEX-065. |
| G5 IDE: finding -> apply_fix -> rerun limpo | Cumpre | `evidence/g5-ciclo.log` valida o ciclo funcional real no `spv0-spark-master`; `evidence/g5-autonomous-ciclo.log` valida o mesmo ciclo na stack autonoma: finding 1 -> 0, shuffle 1.157.481 -> 0; `evidence/g6-mcp-ide-subprocess-smoke.jsonl` valida `apply_fix` via cliente subprocesso JSON-RPC; `evidence/g6-mcp-ide-gui-smoke-2026-07-18.log` valida `apex-commander` em Claude Code GUI real. | Verde funcionalmente e validado em IDE GUI real para o contrato MCP/apply guardado. |
| G6 oraculo agendado sintetico vs real drift | Fechado | `tools/g6_oracle_drift_smoke.py` gera sintetico oficial, roda `oracle/compare.py` contra `real_log.ndjson` e salva resumo JSON; `.github/workflows/scenario-gate.yml` tem `workflow_dispatch`, cron semanal e job `g6-oracle-drift`; evidencias locais em `evidence/g6-oracle-drift-smoke.log` e `evidence/g6-oracle-drift-summary.json`; execucao remota atual em `evidence/g6-remote-workflow-latest-summary.json`. | O workflow remoto `Apex Scenario Gate` passou inteiro no campeonato em `9510d12`: jobs `gate` e `g6-oracle-drift` verdes. A falha anterior ficou registrada em CODEX-033 como incidente corrigido. |
| G7 local MCP/compose/listener/judge | Parcial avancado | `evidence/g6-mcp-ide-subprocess-smoke.jsonl`, `evidence/g6-mcp-ide-gui-smoke-2026-07-18.log`, `evidence/g7-autonomous-spark-pi-v2.log`, `evidence/g3-autonomous-diagnosis.json`, `evidence/g5-autonomous-ciclo.log`, `evidence/g9-listener-jvm-spark-submit.log`, `evidence/g9-listener-jvm-failsafe-spark-submit.log`, `evidence/f7-remote-real-stack-run-29671461366-loop.log`, `evidence/crew-judge-real-provider-smoke-2026-07-19.json`. | Fecha contrato local, compose autonomo com G3/G5, listener runtime/fail-safe, MCP GUI real, loop remoto real-stack e Judge plugável read-only; ainda falta execução Crew.ai com LLM externo real. |
| G8 loop agentico local | Parcial | `apex/commander/agentic_loop.py` e `tools/agentic_validation_loop.py` executam um loop deterministico com agentes locais `EvidenceCollector`, `DeterministicJudge` e `NextActionPlanner`; evidencia em `evidence/agentic-validation-loop-report.json`. | Sem LLM e sem mutacao; smoke GUI MCP e real-stack remoto ja foram observados. A pendencia restante e evoluir para Crew.ai/Judge real ou UI de produto, se o Commander priorizar. |

## Mapeamento Do Gate 14 Interno

O Gate 14 interno da branch Codex adicionou:

- template canonico de `spark-submit` com `spark.extraListeners`;
- polling de telemetria por `after_job_id`;
- `execute_rerun_poll_and_compare` guardado.

Ele nao corresponde 1:1 a um gate comum. O melhor encaixe e:

| Gate 14 interno | Gate comum relacionado | Encaixe |
| --- | --- | --- |
| Spark submit template | L3 / parte de L1 | Prepara o comando, mas nao implementa o listener real. |
| Telemetry polling | L4 / G5 | Ajuda a esperar evidencia antes/depois, mas nao substitui ClickHouse schema canonico nem IDE. |
| Rerun + compare local | G5 | Aproxima o ciclo "aplicar -> reexecutar -> provar", mas ainda com runner/fakes ou comando local configuravel, nao Spark real completo. |

Conclusao: Gate 14 e uma base util para G5, mas nao torna G5 verde sozinho.

## Gaps Por Premissa

| Premissa | Gap principal | Ordem proposta |
| --- | --- | --- |
| L1 | Falta observar Crew.ai com LLM externo real | Manter T1 deterministico como nucleo; provider Crew.ai ja existe como opcional e read-only. |
| L2 | Fechado localmente em Spark 4.1.2 | Manter regressao G3/G5 autonoma com `spark.executor.memory=3g` e `spark.driver.memory=2g`. |
| L3 | Fechado no smoke runtime e usado no G3/G5 autonomo | Promover o JAR para template oficial dos jobs. |
| L4 | Fechado localmente com DDL canonico e adapters por `app_id`/`job_id`; ainda falta consolidar como schema de producao na V1 composta | Manter o DDL do pacote comum como contrato imutavel e validar qualquer migracao ClickHouse contra ele. |
| L5 | Contrato anti-alucinacao implementado; falta ambiente Crew.ai/LLM externo | Configurar `APEX_CREW_JUDGE_ENABLED=1`, dependencia Crew.ai e credenciais/modelo apenas se o Commander autorizar custo/segredo. |
| L6 | Fechado em Claude Code GUI | Manter regressao do transcript MCP GUI e repetir quando mudar `.mcp.json`/`tool_contract.py`. |
| L7 | ADR formal versionada criada | Manter ADRs curtas e atualizar quando o Commander decidir a V1 composta. |
| L9 | MVPs centrais locais existem; falta observar provider Crew.ai com LLM externo | Nao colocar LLM no caminho quente; preservar regressao G0-G6, stack autonoma, schema, listener, MCP GUI e Judge contract verdes. |

## Ordem De Trabalho Recomendada

1. **Etapa 1 — Docker/Spark Envy minimo**
   - Fechado localmente com `docker-compose.autonomous.yml`.
   - Loop automatizado construido em `scripts/f7_autonomous_stack_loop.py`.
   - Execucao real local do runner fechada em `evidence/f7-autonomous-stack-loop-20260718-real-local-6.log`.
   - Execucao real remota fechada no `Apex Scenario Gate` com `run_real_stack=true` em `evidence/f7-remote-real-stack-run-29671461366-loop.log`.
   - Proximo passo: decidir se o runner self-hosted permanece ativo para avaliacao ou deve ser removido apos o julgamento.

2. **Etapa 2 — Schema ClickHouse canonico**
   - Fechado localmente com `docs/specs/apex_telemetry_v1.sql`.
   - Proximo passo: validar qualquer evolucao de schema contra o contrato do pacote comum.

3. **Etapa 3 — Listener/bridge real fail-safe**
   - Fechado localmente com `listener-jvm/` e `spark-submit --jars`.
   - Proximo passo: integrar o JAR ao template oficial de submissao.

4. **Etapa 4 — Cenarios comuns e gates G1-G3**
   - Portar cenarios v1 do pacote comum.
   - Rodar baseline `none` e detectores sinteticos.
   - Validar skew sintetico vs real.

5. **Etapa 5 — T1 latencia**
   - Medicao inicial concluida em `evidence/g4-t1.log`: 226.991 ms contra o event log real `app-20260712053414-0001`.
   - Manter regressao automatizada de latencia antes de evoluir Crew.ai/Judge.

6. **Etapa 6 — MCP IDE/apply_fix**
   - Ciclo funcional real concluido em `evidence/g5-ciclo.log` usando `apply_recommendation`.
   - Contrato local `apply_fix` concluido em `evidence/g6-apply-fix-mcp-smoke.log`, mantendo `apply_recommendation` como compatibilidade.
   - Preservar backup, diff revisavel, token/confirmacao e verificacao.
   - Validado em IDE real no Claude Code GUI com `tools/list`, `recommend_fix`, `preview_recommendation`, `apply_fix` e `compare_job_telemetry`.

7. **Etapa 7 — Crew.ai**
   - Provider opcional criado em `apex/commander/judge_providers.py`.
   - Tool read-only criada como `crew_judge_diagnose`.
   - Smoke de ambiente criado em `tools/crew_judge_provider_smoke.py`: `crewai_installed=true`.
   - Tentativa com `APEX_CREW_JUDGE_ENABLED=1` e `--allow-external-llm` retornou `llm_credentials_missing`, sem chamada externa ruidosa.
   - Proximo passo: executar com Crew.ai/LLM externo apenas quando houver credenciais aprovadas.

## Reaproveitar Versus Refazer

### Reaproveitar

- Loop deterministico: `diagnose_findings`, `debug_job`, detectores locais.
- EvidenceValidator: manter como camada de bloqueio antes de agente/LLM.
- Store/adapters ClickHouse: reaproveitar limite de client e testes fake/HTTP.
- MCP stdio: reaproveitar JSON-RPC local e metadados de safety.
- Apply guardado: reaproveitar token, preview, hash, `apply_root`, verify.
- Rerun/compare/polling: reaproveitar como base do G5.
- Oracle e real log do slice v4: reaproveitar como evidencia historica de skew.

### Refazer Ou Alinhar Ao Pacote Comum

- Docker/Spark Envy: stack autonoma Spark 4.1.2 existe, sobe e fechou G3/G5 real; proximo passo e transformar em regressao oficial.
- DDL ClickHouse canonico `apex_telemetry_v1.sql`: reaproveitar como contrato imutavel, ja alinhado ao pacote comum.
- Listener real fail-safe: ja existe runtime smoke; alinhar ao job template oficial e manter teste de fail-safe.
- Crew.ai: camada plugavel implementada; alinhar execucao externa real somente apos aprovacao de ambiente/segredos.
- Tool `apply_fix`: contrato local ja adaptado e validado em Claude Code GUI; ajustar formato apenas se outro cliente MCP escolhido pelo Commander exigir.
- ADRs formais: criadas em `docs/adr/ADR-*.md`; falta revisao do Commander para decisoes finais de produto.

## Observacoes F0

- `ISSUES.md` existe hoje na raiz como catalogo formal do F0, com `CODEX-001` a `CODEX-007`; `CODEX-007` esta fechado como fato estabelecido, com evidencia nos commits `52b181b`, `64478f6`, `086e3a0` e `8f4b802`.
- Proveniencia do fix guardado: `apex/commander/fix_preview.py` aparece primeiro em `4983b10` (2026-07-09) e `apex/commander/apply_verify.py` aparece primeiro em `8f4b802` (2026-07-11). O `CODEX-007` confirma que o Gate 11 adotou o conceito `apply_fix` da Cowork, lido no comparativo de 08/07 antes do Gate 11 ser definido, e nao foi invencao paralela independente.
- `docs/autoavaliacao.md` e `MELHORIAS.md` foram criados como arquivos vazios, conforme pedido de `touch`.
- `evidence/`, `docs/adr/` e `docs/meetings/` foram criados como diretorios locais. Se precisarem ser versionados vazios, sera necessario adicionar arquivos sentinela em etapa posterior.
- O F0 foi sincronizado com a branch remota `campeonato/codex-round2` apos a confirmacao de proveniencia.
