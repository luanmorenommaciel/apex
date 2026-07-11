# Gate 9: MCP Read-Only For Persisted Findings

Date: 2026-07-11
Branch: `gustocezar/feature/codex-desacoplamento-geradores`
Prepared by: Codex

## Goal

Expose findings persisted in ClickHouse through the local Commander MCP contract without adding mutation, network requirements, or remote publication.

## Scope

- Add a read-only `query_persisted_findings(job_id)` tool.
- Keep `debug_job` as the deterministic recomputation path.
- Keep persisted findings as the audited historical path.
- Return an explicit `not_configured` status when no finding store is attached.
- Validate the behavior through fake stores and MCP JSON-RPC tests.

## Out Of Scope

- No `apply_fix`.
- No automatic file mutation.
- No mandatory ClickHouse service in the default suite.
- No remote branch update.
- No external MCP SDK certification yet.

## Data Flow

```text
ClickHouseFindingStore
  -> query_by_job_id(job_id)
  -> query_persisted_findings
  -> CommanderToolContract.call_tool
  -> MCP tools/call
  -> IDE/client receives JSON text content
```

## Validation

Run:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_tool_contract.py tests/test_commander_mcp_stdio_server.py tests/test_commander_clickhouse_findings.py -q --basetemp .pytest-commander-gate9-mcp-findings-code
```

Expected:

```text
29 passed
```

## Acceptance

- `tools/list` includes `query_persisted_findings`.
- All exposed Commander tools remain `read_only`.
- `tools/call` can return persisted finding records by `job_id`.
- Missing finding store returns `not_configured` instead of silently failing.
- The default test path remains local and offline.
