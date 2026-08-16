# Six-lane E2E gate — real evidence, 2026-08-11/12

Primeira vez que a cadeia completa (dev → jar → collect → infra → engine →
serve) rodou de ponta a ponta nesta sessão, contra `origin/main` (branch
`candidate/fix-mv-bootstrap-ordering`, sem nenhum código fork-only).

## Topologia real usada

- `infra/docker-compose.yml`: clickhouse + mongodb + otel-collector (hyperdx
  pulado, não necessário para este teste).
- `collect/docker-compose.yml` + `docker-compose.c3-infra.yml`: otel-collector
  real, roteado para `apex-infra-clickhouse` (confirmado via `docker compose
  config`).
- `dev/docker-compose.yml` + `docker-compose.c3-otlp.yml`: spark-master/worker
  anexados à `apex-collect-net`, DNS resolvendo `apex-otel-collector` de
  verdade (confirmado via `getent hosts`).
- DDL aplicado com `infra/scripts/apply_ddl.sh` já corrigido (guarda do #72),
  14 arquivos, sem erro.

## Job real

`skew_join.py`, plugin `apex.ApexPlugin` anexado, endpoint OTLP real
(`http://apex-otel-collector:4318`), 10M linhas via join real sobre Delta/S3A.

```
APEX_JOB skew_join aqe=False app_id=app-20260812002731-0000 joined_rows=10000000 grand_total=4999507894.6
exitCode 0
```

## Telemetria — chegada real via OTLP (não SQL manual)

```sql
SELECT count() FROM apex.otel_traces WHERE SpanAttributes['job_id']='app-20260812002731-0000';
-- 20

SELECT stage_id, task_count, task_duration_p50_ms, task_duration_p99_ms,
       round(task_duration_p99_ms/nullIf(task_duration_p50_ms,0),2) AS skew_ratio
FROM apex.spark_events WHERE job_id='app-20260812002731-0000' ORDER BY stage_id;
-- 20 linhas, incluindo stage 21: task_count=100, skew_ratio=19.18
```

20/20 spans propagaram pela MV real (`mv_spark_events`), sem perda.

## ENGINE — análise determinística real

```
uv run --extra clickhouse python -m apex_engine app-20260812002731-0000 --dry-run --no-crew
```

```
stages analyzed: 20  (plan_transitions: 0)
mode           : deterministic   crew: not_needed   llm_calls: 0
findings       : 3  rejected: 0

[ warning] SKEW_ON_JOIN       stage 21   conf=LOW(0.50) via skew_watcher
           evidence: p99/p50 = 19.18x on stage 21 (100 tasks) ...
[ warning] MEMORY             stage 8    conf=LOW(0.45) via memory_watcher
[ warning] SPILL              stage 21   conf=MEDIUM(0.75) via memory_watcher
```

## SERVE — gate MCP real via stdio client

```
APEX_GATE_JOB_ID=app-20260812002731-0000 uv run python tools/mcp_stdio_gate.py
```

```json
{
  "gate": "serve-stdio-mcp",
  "status": "passed",
  "analyze_run": {"status": "degraded", "worst_stage_id": 21, "primary_symptom": "disk_spill"},
  "suggest_fix": {"applied": false, "requires_human_approval": true, "confidence": 0.7,
                   "source": "spark_events_heuristic", "gated": true},
  "tools": [4 tools contratados, readOnlyHint correto em cada um]
}
```

## Conclusão

Six-lane gate real passou de ponta a ponta contra `main` como está hoje —
nenhuma mudança de código foi necessária para este teste específico
(diferente de #71/#72, que exigiram fix). Primeira evidência real, nesta
sessão, de que dev → jar → collect → infra → engine → serve funcionam
encadeados com dados reais, não testados isoladamente.
