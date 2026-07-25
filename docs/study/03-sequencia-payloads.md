# Fase 3 - Sequencia, payloads e protocolos

## Caso de uso: skew em join

O exemplo abaixo usa uma chave quente no cenario `skew_join`. A deteccao pode
vir da razao p99/p50 e pode ser corroborada por uma transicao AQE `skew_split`.

```mermaid
sequenceDiagram
    participant Dev as DEV job
    participant Jar as ApexPlugin/JAR
    participant Col as OTel Collector
    participant CH as ClickHouse
    participant Eng as ENGINE
    participant Mcp as SERVE MCP
    participant Human as Engenheiro

    Dev->>Jar: SparkListener callbacks\nTaskMetrics + plano logico
    Jar->>Jar: agrega por stage_id/stage_attempt\ncalcula p50, p99 e fingerprint
    Jar->>Col: OTLP/HTTP Protobuf\nSpanName=apex.stage
    Jar->>Col: OTLP/HTTP Protobuf\nSpanName=apex.plan_transition (AQE)
    Col->>Col: memory_limiter, redacao, drop PII
    Col->>CH: insert otel_traces em lote
    CH->>CH: MV -> spark_events / plan_transitions
    Eng->>CH: SELECT parametrizado por job_id
    Eng->>Eng: watchers + EvidenceValidator\n0 chamadas LLM no Tier 1
    opt candidato LOW + critical/blocker
      Eng->>Eng: Crew correlator/Judge com evidencia limitada
    end
    Eng->>CH: INSERT apex.findings validado
    Mcp->>CH: analyze_run(job_id) read-only
    Mcp-->>Human: Diagnosis JSON + finding + evidencia
    Human->>Mcp: suggest_fix(job_id)
    Mcp-->>Human: diff proposto, applied=false
```

## Payload principal: `apex.stage`

O span transporta campos de contrato, incluindo:

| Grupo | Campos exemplares | Uso posterior |
|---|---|---|
| Correlacao | `job_id`, `app_id`, `app_name`, `stage_id`, `stage_attempt`, `ts` | une todas as raias |
| Custo/movimento | `shuffle_read_bytes`, `shuffle_write_bytes`, `input_bytes`, `output_bytes` | watchers shuffle e cost |
| Memoria | `spill_disk_bytes`, `spill_mem_bytes`, `gc_time_ms`, `peak_execution_mem_bytes` | watcher memory |
| Tempo | `task_count`, `task_duration_p50_ms`, `task_duration_p99_ms` | watcher skew |
| Plano | `plan_fingerprint`, `plan_json` | compara execucoes; texto e tratado como nao confiavel |

`plan_json` e texto de plano redigido, apesar do nome. Ele nao deve ser
executado nem tratado como instrucao por nenhum agente.

## Payload complementar: `apex.plan_transition`

| Campo | Exemplo | Significado |
|---|---|---|
| `transition_type` | `skew_split` | AQE dividiu uma particao enviesada |
| `transition_type` | `coalesce` | AQE reduziu particoes; nao prova skew |
| `transition_type` | `join_switch` | plano trocou estrategia de join |
| `confidence` | `HIGH` ou `BEST_EFFORT` | qualidade da classificacao estrutural |

## Resposta MCP

O MCP opera por JSON-RPC sobre stdio. As quatro ferramentas atuais sao:

| Ferramenta | Proposito | Mutacao |
|---|---|---|
| `analyze_run` | diagnostico de uma execucao | nenhuma |
| `compare_runs` | antes/depois por fingerprint | nenhuma |
| `search_kb` | busca evidencia/remediacao persistida | nenhuma |
| `suggest_fix` | retorna diff e texto de PR | nenhuma; `applied=false` |
