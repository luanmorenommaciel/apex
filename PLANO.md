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
| L1 Pipeline: Spark Envy Docker -> SparkListener -> ClickHouse -> Crew.ai -> MCP | Parcial | Existe ClickHouse/store em `apex/commander/clickhouse_adapter.py` e `apex/commander/clickhouse_http_client.py`; existe MCP stdio em `apex/commander/mcp_stdio_server.py`; nao existe Spark Envy Docker, SparkListener real nem Crew.ai. |
| L2 `docker compose up` sobe tudo sem configuracao manual | Nao cumpre | Nao ha stack Docker/Compose funcional na branch. |
| L3 Listener via `spark.extraListeners`, fail-safe | Parcial | `apex/commander/spark_rerun_template.py` monta comando com `spark.extraListeners`; nao ha listener JVM real nem teste de fail-safe. |
| L4 ClickHouse com schema definido, query por `app_id`/`job_id` | Parcial | `apex/commander/telemetry.py` carrega `job_id` e `app_id`; adapters consultam por `job_id`; falta DDL canonico `docs/specs/apex_telemetry_v1.sql`. |
| L5 Diagnostico agentico Crew.ai explica o problema | Nao cumpre | Diagnostico atual e deterministico em `apex/commander/diagnostic_mvp.py`; nao ha Crew.ai. |
| L6 Fix via MCP no IDE + "aplica nossa sugestao" edita o codigo do cliente | Parcial | Existe MCP stdio e apply guardado em `apex/commander/apply_verify.py`; a tool atual e `apply_recommendation`, nao `apply_fix`, e nao ha validacao com IDE real. |
| L7 Decisoes de arquitetura registradas em ADR | Parcial | Existe `docs/adr-review-drafts.md`; falta estrutura formal `docs/adr/ADR-*.md`. |
| L8 Nao focar Databricks/serverless agora — Spark puro primeiro | Cumpre | A branch trabalha com Spark event log, ClickHouse/local store e MCP; nao ha implementacao Databricks/serverless. |
| L9 Minimo viavel de cada componente antes de expandir qualquer um | Parcial | Ha MVPs locais para ingest, store, detectores, validator, MCP, apply guardado e rerun; faltam MVPs centrais de Docker/Spark Envy, SparkListener real e Crew.ai. |

## Gates G0-G6 Da Spec Comum

| Gate comum | Status Codex | Evidencia | Observacao sobre encaixe |
| --- | --- | --- | --- |
| G0 build + testes em ambiente limpo | Parcial | Ultima suite local: `138 passed, 2 skipped`; ha `__pycache__` e diretorios `.pytest-*` nao rastreados. | O numero difere da referencia comum de 52 testes porque a branch Codex tem historico proprio e mais testes locais. |
| G1 baseline `none`: zero finding em job saudavel | Parcial | `tests/test_commander_negative_baselines.py` e `tests/test_commander_v01.py` cobrem job saudavel/balanceado. | Cobre o comportamento, mas nao pelo contrato `scenario.yaml` classe `none` da spec comum. |
| G2 cada detector pega seu cenario sintetico | Parcial | `tests/test_commander_detectors.py` cobre skew, spill/shuffle, GC, OOM e AQE localmente. | Nao ha ainda pacote completo de cenarios v1 comuns (`data_skew_on_join_key`, `gc_pressure`, `shuffle_spill`, `oom_task_failure`, `cartesian_product`, `none`). |
| G3 sintetico ~= real no cluster + >=8 tasks reais | Parcial | `real_log.ndjson`, `oracle/compare.py`, docs v4 registram comparacao sintetico vs real para skew. | Cobre o slice de skew; nao cobre todos os detectores nem uma execucao cluster atual pelo pacote comum. |
| G4 T1 < 1s sem LLM; LLM so confidence < 0.6 | Parcial | Caminho atual e deterministico e nao chama LLM. | Falta benchmark automatizado de latencia e politica formal de escalonamento para Crew.ai/Judge. |
| G5 IDE: finding -> apply_fix -> rerun limpo | Parcial | `preview_recommendation`, `apply_recommendation`, `verify_recommendation_apply`, `execute_rerun_poll_and_compare`. | O loop existe localmente e guardado, mas nao e a tool `apply_fix`, nao roda no IDE real e nao prova ainda o rerun limpo com Spark real. |
| G6 oraculo agendado sintetico vs real drift | Nao cumpre | Existe `oracle/compare.py` manual. | Falta agendamento/infra de drift. |

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
| L1 | Falta Spark Envy Docker, SparkListener real e Crew.ai | Fechar primeiro Docker/Spark Envy e ClickHouse canonico; depois listener; depois Crew.ai. |
| L2 | Falta `docker compose up` reproduzivel | Criar compose minimo com Spark, ClickHouse e volume nomeado. |
| L3 | Falta listener real fail-safe | Implementar listener/bridge conforme escopo V1 aceito e teste que exception nao mata job. |
| L4 | Falta DDL canonico `apex_telemetry_v1.sql` e schema apex.* | Criar schema antes de expandir detectores. |
| L5 | Falta Crew.ai e contrato anti-alucinacao | Integrar so depois de T1 e EvidenceValidator estarem ligados ao schema canonico. |
| L6 | Falta `apply_fix` MCP/IDE real | Adaptar `apply_recommendation` para contrato comum `apply_fix` com backup+diff revisavel. |
| L7 | Falta ADR formal versionada | Promover rascunhos para `docs/adr/ADR-*.md`. |
| L9 | Componentes centrais ainda faltam MVP | Nao expandir UX/LLM antes de Docker, schema e listener estarem minimamente verdes. |

## Ordem De Trabalho Recomendada

1. **F1 — Docker/Spark Envy minimo**
   - `docker compose up` sobe Spark local e ClickHouse com named volume.
   - Produz event log ou artefato de telemetria reproduzivel.

2. **F2 — Schema ClickHouse canonico**
   - Criar `docs/specs/apex_telemetry_v1.sql`.
   - Alinhar adapters atuais ao contrato `apex.*`, `job_id`, `app_id`, `shuffle_records`.

3. **F3 — Listener/bridge real fail-safe**
   - Ligar `spark.extraListeners` ou bridge aceito pela ADR.
   - Garantir fail-safe.

4. **F4 — Cenarios comuns e gates G1-G3**
   - Portar cenarios v1 do pacote comum.
   - Rodar baseline `none` e detectores sinteticos.
   - Validar skew sintetico vs real.

5. **F5 — T1 latencia**
   - Medir T1 < 1s sem LLM.
   - Registrar log cru em `evidence/`.

6. **F6 — MCP IDE/apply_fix**
   - Converter apply guardado atual para contrato `apply_fix`.
   - Preservar backup, diff revisavel, token/confirmacao e verificacao.

7. **F7 — Crew.ai**
   - Entrar apenas quando T1 + EvidenceValidator + schema canonico estiverem estaveis.

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

- Docker/Spark Envy: criar do zero para a spec comum.
- DDL ClickHouse canonico `apex_telemetry_v1.sql`: criar/alinha-lo ao pacote comum.
- Listener real fail-safe: implementar, nao apenas template.
- Crew.ai: implementar camada nova, sem substituir T1 deterministico.
- Tool `apply_fix`: adaptar contrato atual para o nome/forma esperados pelo MCP/IDE comum.
- ADRs formais: promover rascunhos para `docs/adr/ADR-*.md`.

## Observacoes F0

- `ISSUES.md` foi citado como existente com `CODEX-001`, mas nao foi encontrado neste checkout durante a formalizacao. Por isso, nao foi criado nem alterado neste F0.
- Proveniencia do fix guardado: `apex/commander/fix_preview.py` aparece primeiro em `4983b10` (2026-07-09) e `apex/commander/apply_verify.py` aparece primeiro em `8f4b802` (2026-07-11). Como a branch ja continha `docs/architecture/codex-branch-solution-comparison-2026-07-09.md`, a origem conceitual do fix guardado deve ser tratada como risco de proveniencia e foi registrada em `ISSUES.md` como `CODEX-007`.
- `docs/autoavaliacao.md` e `MELHORIAS.md` foram criados como arquivos vazios, conforme pedido de `touch`.
- `evidence/`, `docs/adr/` e `docs/meetings/` foram criados como diretorios locais. Se precisarem ser versionados vazios, sera necessario adicionar arquivos sentinela em etapa posterior.
- Nada foi enviado para remote.
