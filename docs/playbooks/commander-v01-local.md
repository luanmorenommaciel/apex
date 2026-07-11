# Commander V0.1 Local Harness

Este playbook executa localmente o primeiro corte do fluxo pedido pelo Luan.

Branch local:

```text
local/luan-v01-commander
```

Regra desta branch:

```text
Nao fazer push enquanto a branch online avaliada estiver em revisao.
```

## O que este corte prova

Fluxo local:

```mermaid
flowchart LR
    LOG["Spark event log<br/>real ou fixture"]
    CONTRACT["Telemetry contract<br/>apex.commander.telemetry"]
    STORE["ClickStack MVP<br/>NDJSON local"]
    DIAG["Diagnostic MVP<br/>diagnose_job"]
    CLI["CLI demo<br/>job_id"]

    LOG --> CONTRACT --> STORE --> DIAG --> CLI
```

Este corte materializa o contrato da V0.1:

- um `job_id` identifica a execucao;
- eventos Spark viram um envelope de telemetria;
- o store local simula o papel inicial do ClickStack;
- o diagnostico retorna um Finding deterministico;
- a CLI demonstra a experiencia "debuga esse job".

## O que ainda nao e

Este corte ainda nao e:

- um JVM `SparkListener` real injetado no Spark;
- ClickHouse/ClickStack real;
- CrewAI real;
- servidor MCP real;
- alteracao automatica de codigo;
- UI local de DAG/replay.

Essas pecas entram depois que a Crew validar o contrato local.

## Rodar a demo

Gerar um store local a partir do log versionado:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python tools/commander_v01_demo.py real_log.ndjson .commander-v01-store.ndjson --job-id real-log-demo
```

Saida esperada:

```json
{
  "confidence": "medium",
  "job_id": "real-log-demo",
  "status": "finding",
  "title": "shuffle_skew_candidate"
}
```

## Rodar testes

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_v01.py -q --basetemp .pytest-luan-v01
```

Rodar tudo:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests -q --basetemp .pytest-luan-v01-all
```

## Como evoluir para o desenho do Luan

| Ponto do Luan | Estado neste corte | Proxima troca |
| --- | --- | --- |
| Spark Env | Usa event log existente | Docker/Spark local gerando logs novos |
| SparkListener | Contrato por parser de event log | Listener JVM emitindo o mesmo envelope |
| ClickStack | NDJSON local | ClickHouse/ClickStack com schema versionado |
| CrewAI | Diagnostico deterministico | Agente lendo evidencias do store |
| MCP | CLI local por `job_id` | MCP tool `debug_job(job_id)` |
| Sugestao de correcao | Recomendacao textual | Patch/review com aprovacao humana |

## Gate 1: Contrato executavel do Luan

Este gate transforma a branch Codex em uma validacao local da arquitetura do Luan.

Componentes:

- `debug_job(job_id)`: retorna diagnostico deterministico e validacao de evidencia.
- `explain_evidence(job_id)`: mostra a telemetria armazenada para o job.
- `EvidenceValidator`: bloqueia findings fracos antes de qualquer agente/LLM.
- Baseline negativo: job balanceado nao pode gerar skew.
- `fix_preview`: gera diff sem alterar arquivo.

Rodar:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_v01.py tests/test_commander_evidence_validator.py tests/test_commander_mcp_contract.py tests/test_commander_fix_preview.py -q --basetemp .pytest-commander-gate1
```

Esperado:

```text
13 passed
```

## Gate 2: Detectores locais multiplos

O Gate 2 amplia `debug_job(job_id)` para retornar uma lista de findings validados, mantendo `finding` como campo legado para o primeiro finding.

Detectores locais:

- `shuffle_skew_candidate`
- `shuffle_spill_candidate`
- `gc_pressure_candidate`
- `oom_candidate`
- `plan_aqe_replan_candidate`

Contrato atualizado:

- `diagnose_findings(store_path, job_id)` retorna todos os findings deterministico locais;
- `debug_job(store_path, job_id)` retorna `findings` e `validations`;
- `debug_job(store_path, job_id)` preserva `finding` e `validation` para compatibilidade;
- `EvidenceValidator` aceita os cinco tipos de finding com regras especificas por tipo.

Rodar:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_detectors.py tests/test_commander_mcp_contract.py tests/test_commander_evidence_validator.py -q --basetemp .pytest-commander-gate2
```

Esperado:

```text
16 passed
```

Limite consciente deste gate:

- os thresholds ainda estao fixos no codigo;
- ainda nao ha ClickHouse real;
- ainda nao ha MCP server real;
- ainda nao ha aplicacao automatica de fix.

## Gate 3: Baseline negativo executavel

O Gate 3 transforma controle de falso positivo em contrato executavel.

Novo componente:

- `evaluate_negative_baseline(store_path, job_id)`: roda `diagnose_findings` contra um job que deveria ser saudavel.

Resultado esperado para job saudavel:

```json
{
  "job_id": "healthy-job",
  "status": "passed",
  "unexpected_findings": [],
  "unexpected_finding_count": 0
}
```

Resultado esperado quando qualquer detector dispara:

```json
{
  "job_id": "spill-job",
  "status": "failed",
  "unexpected_finding_count": 1
}
```

Rodar:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_negative_baselines.py -q --basetemp .pytest-commander-gate3
```

Esperado:

```text
2 passed
```

O que este gate prova:

- job com skew balanceado nao gera finding;
- spill abaixo do threshold nao gera finding;
- GC saudavel nao gera finding;
- menos de 3 updates AQE nao gera finding;
- se um detector dispara em baseline, o gate retorna `failed`.

## Gate 4: Adapter ClickHouse/ClickStack com fake client

O Gate 4 prepara a troca do NDJSON local por ClickHouse/ClickStack sem exigir servidor real nesta etapa.

Novos componentes:

- `ClickHouseTelemetryStore`: adapter injetavel que usa um client com `command`, `insert` e `query`;
- `query_envelopes(store, job_id)`: helper que permite ao Commander ler tanto path NDJSON quanto stores com `query_by_job_id`;
- fake client em teste cobrindo schema, insert, query e protecao contra nome de tabela inseguro.

Contrato preservado:

- `append_envelope(path, envelope)` e `query_by_job_id(path, job_id)` continuam funcionando com NDJSON;
- `diagnose_findings(store, job_id)` aceita o adapter fake;
- `explain_evidence(store, job_id)` aceita o adapter fake.

Rodar:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_clickhouse_adapter.py tests/test_commander_negative_baselines.py tests/test_commander_mcp_contract.py tests/test_commander_v01.py -q --basetemp .pytest-commander-gate4
```

Esperado:

```text
15 passed
```

Limite consciente deste gate:

- nao abre conexao de rede;
- nao instala driver ClickHouse;
- nao valida Docker/ClickHouse real;
- nao cria schema de findings separado.

## Gate 5: MCP/Tool Contract local

O Gate 5 cria uma camada local de ferramentas, pronta para ser embrulhada por MCP depois.

Novo componente:

- `CommanderToolContract(store)`: dispatcher local em processo.

Tools expostas:

| Tool | Seguranca | O que faz |
| --- | --- | --- |
| `debug_job` | `read_only` | retorna findings e validacoes para um `job_id` |
| `explain_evidence` | `read_only` | retorna a evidencia de telemetria mais recente |
| `evaluate_negative_baseline` | `read_only` | executa o gate de falso positivo para um `job_id` |
| `query_persisted_findings` | `read_only` | retorna findings validados ja persistidos para um `job_id` |
| `recommend_fix` | `read_only` | gera recomendacoes deterministicas a partir dos findings persistidos |
| `preview_recommendation` | `read_only` | gera diff para uma recomendacao selecionada sem alterar arquivo |
| `apply_recommendation` | `guarded_mutation` | aplica a recomendacao somente com token de aprovacao e `apply_root` |
| `verify_recommendation_apply` | `read_only` | verifica o hash final apos apply guardado |
| `compare_job_telemetry` | `read_only` | compara telemetria antes/depois por `job_id` |
| `plan_rerun` | `read_only` | cria plano de reexecucao com token para comando permitido |
| `execute_rerun_and_compare` | `guarded_mutation` | executa comando aprovado e chama `compare_job_telemetry` |
| `preview_fix` | `read_only` | retorna diff unificado sem alterar o arquivo |

Contrato de seguranca:

- `list_tools()` nao expõe `apply_fix`;
- `call_tool("apply_fix", ...)` falha com `unknown_tool`;
- `recommend_fix` nao chama LLM e nao altera arquivo;
- `preview_recommendation` exige `recommendation_id` e preserva o arquivo original;
- `apply_recommendation` exige `approval_token` gerado no preview e `apply_root` configurado;
- `verify_recommendation_apply` compara hash esperado contra hash atual;
- `compare_job_telemetry` le apenas telemetria ja coletada;
- `plan_rerun` exige `rerun_root` e allowlist de comando;
- `execute_rerun_and_compare` exige token do plano e roda sem shell;
- `preview_fix` usa `build_fix_preview` e preserva o arquivo original.

Rodar:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_tool_contract.py tests/test_commander_mcp_contract.py tests/test_commander_fix_preview.py tests/test_commander_negative_baselines.py -q --basetemp .pytest-commander-gate5
```

Esperado:

```text
23 passed
```

Limite consciente deste gate:

- ainda nao ha servidor MCP stdio real;
- `apply_fix` bruto continua ausente;
- escrita so acontece via `apply_recommendation` guardado a partir do Gate 11.

## Gate 6: MCP stdio local read-only

O Gate 6 embrulha o `CommanderToolContract` em um servidor stdio local baseado em JSON-RPC.

Metodos suportados:

| Metodo | O que retorna |
| --- | --- |
| `initialize` | versao de protocolo, capacidades e `serverInfo` |
| `notifications/initialized` | notificacao sem resposta |
| `tools/list` | lista MCP das tools read-only |
| `tools/call` | resultado da tool em `content[0].text` como JSON |

Tools continuam as mesmas do Gate 5:

- `debug_job`
- `explain_evidence`
- `evaluate_negative_baseline`
- `query_persisted_findings`
- `recommend_fix`
- `preview_recommendation`
- `apply_recommendation`
- `verify_recommendation_apply`
- `compare_job_telemetry`
- `plan_rerun`
- `execute_rerun_and_compare`
- `preview_fix`

Rodar:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_mcp_stdio_server.py tests/test_commander_tool_contract.py tests/test_commander_mcp_contract.py -q --basetemp .pytest-commander-gate6
```

Esperado:

```text
32 passed
```

Limite consciente deste gate:

- nao usa SDK MCP externo;
- nao valida contra cliente MCP real;
- nao abre socket de rede;
- nao expoe `apply_fix` bruto;
- nao altera arquivo alvo.

## Gate 7: ClickHouse real local

O Gate 7 valida persistencia real de telemetria em ClickHouse via HTTP, sem driver externo.

Novos componentes:

- `ClickHouseHttpClient`: client HTTP com `command`, `insert` e `query`;
- `tests/test_commander_clickhouse_http_client.py`: valida SQL, Basic Auth, JSONEachRow e parsing sem rede;
- `tests/test_commander_clickhouse_real_integration.py`: valida roundtrip real quando as variaveis de ambiente estao configuradas.

Rodar suite padrao do gate:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_clickhouse_http_client.py tests/test_commander_clickhouse_adapter.py tests/test_commander_clickhouse_real_integration.py -q --basetemp .pytest-commander-gate7
```

Esperado sem ClickHouse real configurado:

```text
8 passed, 1 skipped
```

Rodar contra ClickHouse real local:

```powershell
$env:APEX_CLICKHOUSE_REAL_URL='http://localhost:28123'
$env:APEX_CLICKHOUSE_REAL_USER='<usuario local>'
$env:APEX_CLICKHOUSE_REAL_PASSWORD='<senha local>'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_clickhouse_real_integration.py -q
```

Esperado:

```text
1 passed
```

O teste real:

- cria uma tabela temporaria unica;
- executa `ensure_schema`;
- insere envelope de telemetria;
- consulta por `job_id`;
- roda `diagnose_findings` e `explain_evidence` sobre o store real;
- remove a tabela ao final.

Limite consciente deste gate:

- nao grava credenciais em arquivo;
- nao valida schema separado de findings;
- nao troca o store padrao NDJSON da CLI;
- nao altera branches remotas.

## Gate 8: Findings persistidos no ClickHouse

O Gate 8 adiciona uma trilha auditavel para decisoes do Commander.

Fluxo validado:

```text
telemetry envelope
  -> diagnose_findings
  -> EvidenceValidator
  -> commander_findings
  -> query por job_id
```

Novos componentes:

- `ClickHouseFindingStore`: schema, insert e query de findings;
- `persist_validated_findings`: valida cada finding antes de persistir;
- `tests/test_commander_clickhouse_findings.py`: fake-client tests sem rede;
- `tests/test_commander_clickhouse_findings_real_integration.py`: validacao real opt-in.

Rodar suite padrao do gate:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_clickhouse_findings.py tests/test_commander_clickhouse_findings_real_integration.py tests/test_commander_clickhouse_real_integration.py -q --basetemp .pytest-commander-gate8
```

Esperado sem ClickHouse real configurado:

```text
3 passed, 2 skipped
```

Rodar contra ClickHouse real local:

```powershell
$env:APEX_CLICKHOUSE_REAL_URL='http://localhost:28123'
$env:APEX_CLICKHOUSE_REAL_USER='<usuario local>'
$env:APEX_CLICKHOUSE_REAL_PASSWORD='<senha local>'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_clickhouse_findings_real_integration.py -q
```

Esperado:

```text
1 passed
```

O teste real:

- cria uma tabela temporaria de telemetria;
- cria uma tabela temporaria de findings;
- persiste o envelope;
- calcula findings deterministico;
- valida findings;
- persiste findings validados;
- consulta findings por `job_id`;
- remove as tabelas ao final.

Limite consciente deste gate:

- findings passam a ser expostos no MCP dedicado a partir do Gate 9;
- recomendacoes estruturadas passam a existir a partir do Gate 10;
- apply guardado passa a existir a partir do Gate 11;
- nao altera branches remotas.

## Gate 9: Findings persistidos expostos no MCP read-only

O Gate 9 conecta a trilha auditavel do ClickHouse ao contrato MCP local.

Nova tool:

| Tool | Seguranca | O que faz |
| --- | --- | --- |
| `query_persisted_findings` | `read_only` | consulta findings ja validados e persistidos para um `job_id` |

Contrato:

```json
{
  "job_id": "job-42",
  "status": "found",
  "count": 1,
  "records": [
    {
      "finding": {},
      "validation": {}
    }
  ]
}
```

Se o contrato MCP for iniciado sem um `finding_store`, a tool responde de forma explicita:

```json
{
  "job_id": "job-42",
  "status": "not_configured",
  "count": 0,
  "records": []
}
```

Isso permite manter o servidor MCP local seguro em ambientes sem ClickHouse configurado, sem esconder a ausencia da camada persistida.

Rodar suite padrao do gate:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_tool_contract.py tests/test_commander_mcp_stdio_server.py tests/test_commander_clickhouse_findings.py -q --basetemp .pytest-commander-gate9-mcp-findings
```

Esperado:

```text
34 passed
```

Fluxo atual:

```text
ClickHouseFindingStore
  -> query_by_job_id
  -> query_persisted_findings
  -> CommanderToolContract
  -> MCP tools/call
```

Limite consciente deste gate:

- a tool le apenas findings ja persistidos;
- nao dispara diagnostico novo;
- recomendacao estruturada entra a partir do Gate 10;
- nao aplica patch;
- nao altera branches remotas.

## Gate 10: Recommend/Preview loop

O Gate 10 cria o primeiro loop fechado ate preview, ainda sem aplicar mudanca.

Fluxo:

```text
ClickHouseFindingStore
  -> query_persisted_findings(job_id)
  -> recommend_fix(job_id)
  -> recommendation_id
  -> preview_recommendation(job_id, recommendation_id, path, replacement)
  -> diff read-only
```

Novos componentes:

- `recommend_fix`: gera recomendacoes deterministicas por tipo de finding;
- `preview_recommendation`: valida o `recommendation_id` e gera diff sem alterar arquivo;
- `apex.commander.recommendations.v1`: regra versionada para skew, spill, GC, OOM e AQE;
- testes diretos do recomendador, do contrato local e do MCP stdio.

Contrato de recomendacao:

```json
{
  "job_id": "job-42",
  "status": "found",
  "count": 1,
  "recommendations": [
    {
      "id": "job-42:shuffle_skew_candidate:stage-2:0",
      "finding_kind": "shuffle_skew_candidate",
      "action": "validate_aqe_then_consider_salting_or_repartition",
      "preview": {
        "mode": "manual_replacement",
        "tool": "preview_recommendation",
        "requires_approval_before_apply": true
      }
    }
  ]
}
```

Rodar suite padrao do gate:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_recommendations.py tests/test_commander_tool_contract.py tests/test_commander_mcp_stdio_server.py tests/test_commander_clickhouse_findings.py -q --basetemp .pytest-commander-gate10
```

Esperado:

```text
39 passed
```

Limite consciente deste gate:

- nao aplica patch;
- nao executa re-run automaticamente;
- nao usa LLM para recomendacao basica;
- nao substitui revisao humana;
- nao altera branches remotas.

## Gate 11: Guarded apply/verify

O Gate 11 fecha o loop local ate apply verificado, sem abrir um `apply_fix` bruto.

Fluxo:

```text
preview_recommendation
  -> approval.token
  -> apply_recommendation(..., approval_token)
  -> verify_recommendation_apply
  -> status verified
```

Novos componentes:

- `apply_recommendation`: aplica somente se o token do preview ainda bater;
- `verify_recommendation_apply`: compara o hash atual com o hash esperado;
- `apply_root`: raiz permitida para escrita; sem ela, o apply retorna `apply_root_not_configured`;
- hashes no preview: `before_sha256`, `after_sha256` e `diff_sha256`.

Guardrails:

- se o arquivo mudar depois do preview, o token deixa de bater;
- se o caminho estiver fora de `apply_root`, o apply retorna `outside_apply_root`;
- se o token estiver errado, o apply retorna `invalid_approval_token`;
- o arquivo so e escrito depois dessas verificacoes;
- a verificacao roda depois da escrita.

Rodar suite padrao do gate:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_apply_verify.py tests/test_commander_recommendations.py tests/test_commander_tool_contract.py tests/test_commander_mcp_stdio_server.py tests/test_commander_fix_preview.py -q --basetemp .pytest-commander-gate11
```

Esperado:

```text
41 passed
```

Limite consciente deste gate:

- nao executa Spark re-run automaticamente;
- comparacao de telemetria antes/depois entra a partir do Gate 12;
- nao publica branch remota;
- nao substitui revisao humana.

## Gate 12: Re-run/compare telemetry

O Gate 12 fecha o loop de evidencia: depois de uma mudanca guardada, o usuario pode informar o `job_id` anterior e o `job_id` da reexecucao para comparar telemetria.

Fluxo:

```text
before_job_id
  -> telemetry store / ClickHouse
  -> diagnose_findings
after_job_id
  -> telemetry store / ClickHouse
  -> diagnose_findings
compare_job_telemetry
  -> improved | regressed | unchanged | mixed | not_comparable
```

Nova tool:

| Tool | Seguranca | O que faz |
| --- | --- | --- |
| `compare_job_telemetry` | `read_only` | compara findings e metricas principais entre dois `job_id` |

Metricas comparadas:

- quantidade de findings;
- tipos de findings resolvidos ou novos;
- `max_skew_ratio`;
- `total_spilled_bytes`;
- `max_gc_ratio`;
- `oom_failure_count`;
- `adaptive_execution_updates`.

Rodar suite padrao do gate:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_telemetry_compare.py tests/test_commander_tool_contract.py tests/test_commander_mcp_stdio_server.py tests/test_commander_clickhouse_adapter.py -q --basetemp .pytest-commander-gate12
```

Esperado:

```text
38 passed
```

Limite consciente deste gate:

- nao dispara Spark automaticamente;
- espera que a telemetria do job reexecutado ja tenha sido coletada;
- nao aplica nova correcao automaticamente;
- nao altera branches remotas.

## Gate 13: Automatic re-run orchestration

O Gate 13 adiciona uma reexecucao controlada: o Commander cria um plano, exige token e allowlist, executa o comando sem shell e compara a telemetria antes/depois.

Fluxo:

```text
plan_rerun(before_job_id, after_job_id, command)
  -> approval.token
execute_rerun_and_compare(..., approval_token)
  -> runner.run(command)
  -> compare_job_telemetry(before_job_id, after_job_id)
```

Novas tools:

| Tool | Seguranca | O que faz |
| --- | --- | --- |
| `plan_rerun` | `read_only` | valida `rerun_root`, allowlist, `cwd`, timeout e gera token |
| `execute_rerun_and_compare` | `guarded_mutation` | executa comando aprovado e compara telemetria |

Guardrails:

- sem `rerun_root`, nao executa;
- comando fora da allowlist retorna `command_not_allowed`;
- `cwd` fora de `rerun_root` retorna `outside_rerun_root`;
- token errado retorna `invalid_approval_token`;
- execucao usa lista de argumentos com `shell=False`;
- saida do processo e truncada para evitar payload gigante;
- se a telemetria do `after_job_id` nao existir, a comparacao retorna `not_comparable`.

Rodar suite padrao do gate:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_rerun_orchestrator.py tests/test_commander_telemetry_compare.py tests/test_commander_tool_contract.py tests/test_commander_mcp_stdio_server.py -q --basetemp .pytest-commander-gate13
```

Esperado:

```text
40 passed
```

Limite consciente deste gate:

- nao define ainda um job Spark real padrao do projeto;
- nao faz polling de ClickHouse esperando telemetria chegar;
- nao faz rollback automatico;
- nao altera branches remotas.

## Gate 14: Spark job template + telemetry polling

O Gate 14 torna a reexecucao mais operacional: o Commander passa a montar um comando Spark canonico e pode esperar a telemetria do `after_job_id` aparecer antes de comparar.

Fluxo:

```text
build_spark_submit_rerun_command(app_path, after_job_id)
  -> plan_rerun(before_job_id, after_job_id, command)
  -> approval.token
execute_rerun_poll_and_compare(..., approval_token)
  -> runner.run(command)
  -> poll_telemetry(after_job_id)
  -> compare_job_telemetry(before_job_id, after_job_id)
```

Novas tools:

| Tool | Seguranca | O que faz |
| --- | --- | --- |
| `build_spark_submit_rerun_command` | `read_only` | monta `spark-submit` com `spark.extraListeners` e `spark.apex.jobId` |
| `poll_telemetry` | `read_only` | espera envelopes do `job_id` ficarem visiveis no store |
| `execute_rerun_poll_and_compare` | `guarded_mutation` | executa comando aprovado, aguarda telemetria e compara |

Guardrails:

- o comando Spark e uma lista de argumentos, nao uma string de shell;
- `app_path` fica restrito a `rerun_root` quando configurado;
- `spark.apex.jobId` e `spark.extraListeners` sao definidos pelo template canonico;
- polling tem limite de tentativas e intervalo;
- configuracao invalida de polling bloqueia antes de executar o comando;
- a comparacao so roda quando a telemetria do `after_job_id` aparece;
- se a telemetria nao chegar, retorna `telemetry_not_available` sem inventar resultado;
- MCP marca `execute_rerun_poll_and_compare` como mutacao guardada.

Rodar suite padrao do gate:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_rerun_orchestrator.py tests/test_commander_tool_contract.py tests/test_commander_mcp_stdio_server.py -q --basetemp .pytest-commander-gate14-focused
```

Esperado:

```text
46 passed
```

Limite consciente deste gate:

- ainda nao empacota um `SparkListener` JVM real;
- ainda nao executa um job Spark real em CI;
- ainda nao cria scheduler de reexecucao em producao;
- nao altera branches remotas.
