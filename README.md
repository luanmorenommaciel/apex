# Apex Codex Round2

Branch: `codex-round2`

Estado: solucao local de diagnostico Spark com gates G0-G5 validados e evidencias em `evidence/`.

## O Que Tem Nesta Branch

Esta branch evoluiu do slice `skew_on_join_30x` v4 para uma esteira de diagnostico e correcao assistida para Spark:

```text
event log -> detector deterministico -> EvidenceValidator -> finding
-> recomendacao -> preview de diff -> apply guardado -> rerun -> compare
```

Ela nao deve ser apresentada como V1 completa ainda. O que ela prova bem e o loop funcional com evidencia: detectar um problema real, gerar uma correcao revisavel, aplicar com seguranca, reexecutar e provar que o finding sumiu.

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
| Docker autônomo paralelo | Fechado localmente | `docker-compose.autonomous.yml`; `evidence/g3-autonomous-diagnosis.json`; `evidence/g5-autonomous-ciclo.log` |
| SparkListener JVM real | Fechado localmente/runtime smoke | `listener-jvm/`; `evidence/g9-listener-jvm-spark-submit.log`; `evidence/g9-listener-jvm-failsafe-spark-submit.log` |
| Crew/Judge policy local | Fechado localmente | `apex/commander/judge_policy.py`; `evidence/g8-agentic-loop-python.log` |
| MCP/IDE subprocess smoke | Fechado localmente | `tools/mcp_ide_subprocess_smoke.py`; `evidence/g6-mcp-ide-subprocess-smoke.jsonl` |
| Autoavaliacao | Fechada | `docs/autoavaliacao.md` |
| Catalogo de issues | Fechado/aberto conforme item | `ISSUES.md` |
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
    RERUN --> CMP["Compare telemetry<br/>rerun_compare.py"]
    CMP --> OUT["Resultado<br/>limpo ou issue aberta"]
```

## Componentes Principais

| Componente | Caminho | Papel |
|---|---|---|
| Detectores deterministicos | `apex/commander/diagnostic_mvp.py` | Detecta skew, GC, shuffle/spill, OOM e cartesian product |
| Validador de evidencia | `apex/commander/evidence_validator.py` | Confere se o finding tem evidencia suficiente |
| Telemetria | `apex/commander/telemetry.py` | Normaliza `job_id`, `app_id`, stages, tasks e plano |
| ClickHouse adapter | `apex/commander/clickhouse_adapter.py` | Store local/fake para testes e persistencia |
| ClickHouse HTTP client | `apex/commander/clickhouse_http_client.py` | Cliente para ambiente ClickHouse real |
| MCP stdio | `apex/commander/mcp_stdio_server.py` | Exposicao local de tools para agente/IDE |
| Recomendacoes | `apex/commander/recommendations.py` | Converte finding em recomendacao |
| Preview de fix | `apex/commander/fix_preview.py` | Gera diff antes de qualquer apply |
| Apply guardado | `apex/commander/apply_verify.py` | Aplica com token, hash, root permitido e verificacao |
| Rerun/compare | `apex/commander/rerun_compare.py` | Compara telemetria antes/depois |
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
| `docs/architecture/llm-solution-validation-framework-2026-07-13.md` | Comparacao entre Codex, Cowork, Kimi, Spike e DataFlint |
| `docs/presentations/apex-codex-solucao-end-to-end-2026-07-14.html` | Apresentacao end-to-end da nossa solucao |
| `docs/presentations/apex-codex-projeto-luan-2026-07-14.html` | Apresentacao executiva para o Luan |
| `docs/presentations/llm-solution-validation-2026-07-13.html` | Apresentacao comparativa das solucoes |

## Apresentacoes

Principais arquivos para apresentar:

```text
docs/presentations/apex-codex-solucao-end-to-end-2026-07-14.html
docs/presentations/apex-codex-projeto-luan-2026-07-14.html
docs/presentations/llm-solution-validation-2026-07-13.html
```

Sugestao:

1. Para falar so da nossa solucao: use `apex-codex-solucao-end-to-end-2026-07-14.html`.
2. Para explicar ao Luan em formato executivo: use `apex-codex-projeto-luan-2026-07-14.html`.
3. Para comparar LLMs/DataFlint: use `llm-solution-validation-2026-07-13.html`.

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
evidence/g7-autonomous-compose-config.log
evidence/g8-agentic-loop-python.log
evidence/g9-listener-jvm-environment.log
```

Suite historica:

```powershell
python -m pytest tests -q
```

Observacao: em Windows, alguns comandos antigos podem precisar de basetemp local por permissao no diretorio temporario do usuario. Isso foi registrado durante G5.

## O Que Ainda Nao Esta Pronto

| Gap | Impacto |
|---|---|
| SparkListener JVM real fail-safe | Fechado no smoke runtime: JAR carregado via `spark-submit --jars`, NDJSON emitido e falha interna nao derruba job |
| `docker compose up` autonomo da branch | Fechado localmente: compose autonomo sobe, grava event log em S3A/MinIO e repetiu G3/G5 sem plat-v0 |
| Crew.ai/Judge | Politica local de escalonamento existe; Crew.ai/LLM real segue futuro e opcional |
| IDE real | MCP stdio subprocess estilo cliente externo passa com transcript; ainda precisa smoke GUI em Cursor/VS Code/Claude Code |
| G6 oraculo/drift | Falta agendamento/validacao continua sintetico vs real |

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
| IDE real | Parcial, subprocesso JSON-RPC validado; GUI pendente |
| SparkListener real | Cumpre localmente/runtime smoke |
| Crew.ai/Judge | Parcial, politica local criada sem LLM |
| Plataforma Docker standalone | Cumpre localmente, G3/G5 autonomos passaram; ressalva Spark 4.0.0 vs plat-v0 |

## Proximos Passos Recomendados

1. Fazer smoke GUI real em Cursor/VS Code/Claude Code usando a tool `apply_fix`.
2. Promover o G3/G5 autonomo para regressao automatizada.
3. Integrar o JAR do SparkListener no job template oficial, agora que o smoke `--jars` e G3/G5 autonomos passaram.
4. Promover ADRs formais para decisoes centrais.
5. Criar G6: oraculo agendado e controle de drift.
6. So depois expandir camada Crew.ai/Judge.

## Estado De Publicacao

Esta branch tem historico publicado em `campeonato/codex-round2`. Antes de publicar novas mudancas, confirme:

```powershell
git status --short --branch
git log --oneline --decorate -5
```

Nao faca push de alteracoes novas sem revisao quando a branch remota estiver sendo avaliada.
