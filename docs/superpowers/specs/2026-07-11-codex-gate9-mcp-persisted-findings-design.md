# Gate 9 Design: MCP Read-Only Access To Persisted Findings

Date: 2026-07-11
Branch: `gustocezar/feature/codex-desacoplamento-geradores`
Prepared by: Codex

## Decision

Expose persisted Commander findings through a new read-only MCP tool named `query_persisted_findings`.

## Reason

Gate 8 already persists validated findings in ClickHouse. The next useful local step is to let an IDE or MCP client read that audited evidence by `job_id`, without recalculating diagnosis and without changing files.

## Components

- `ClickHouseFindingStore`: persists and queries validated findings.
- `query_persisted_findings(finding_store, job_id)`: normalizes the read response.
- `CommanderToolContract`: accepts an optional `finding_store`.
- `mcp_stdio_server`: exposes the new tool through existing `tools/list` and `tools/call`.

## Safety

- Tool is read-only.
- No `apply_fix` is exposed.
- Missing `finding_store` returns `not_configured`.
- No ClickHouse credentials are stored.
- No remote branch is updated.

## Output Contract

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

## Validation

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_tool_contract.py tests/test_commander_mcp_stdio_server.py tests/test_commander_clickhouse_findings.py -q --basetemp .pytest-commander-gate9-mcp-findings-code
```

Expected:

```text
29 passed
```

## Next Decision

Gate 10 starts the closed loop carefully:

```text
persisted finding -> recommendation -> preview diff -> explicit approval -> apply -> verify
```
