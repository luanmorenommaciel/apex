# Validação da Raia SERVE - MCP Read-only

## Escopo

Este PR entrega o servidor MCP por `stdio` com duas ferramentas de leitura:

- `analyze_run(job_id)`;
- `compare_runs(baseline_job_id, current_job_id)`.

As ferramentas consultam telemetria e findings já persistidos. Elas não
escrevem em arquivo, Git, Spark ou ClickHouse e não chamam LLM.

## Gates executados nesta branch

```powershell
cd serve
uv run --extra dev pytest
uv run python tools/read_only_gate.py
uv run python tools/mcp_stdio_gate.py
```

Resultados em 2026-07-23:

- `5 passed in 45.92s`;
- gate `C2` passou com `external_llm_calls=0`;
- gate `C2-stdio` passou e listou somente `analyze_run` e `compare_runs`;
- ambas as ferramentas receberam `readOnlyHint=true`.

O fixture do gate mostrou `finding_count` de 1 para 0, razão p99/p50 de 29.5
para 1.0 e spill de 2.097.152 para 0 na comparação before/after.

## Evidência real de referência

O smoke contra ClickHouse real e o processo MCP real estão documentados na
branch de convergência em `evidence/serve-c2-real-mcp-2026-07-22.log` e
`evidence/serve-c2-stdio-mcp-2026-07-22.log`. Esta referência não substitui os
gates locais acima.

## Limites e rollback

- Judge, recomendação, preview, apply e rerun estão fora deste PR.
- Credenciais de ClickHouse são fornecidas pelo operador em variáveis de
  ambiente e não entram no Git.
- Reverter o commit remove somente `serve/` e não muda o contrato.
