# Gate 12: Re-Run/Compare Telemetry

Date: 2026-07-11
Branch: `gustocezar/feature/codex-desacoplamento-geradores`
Prepared by: Codex

## Goal

Compare telemetry before and after a guarded apply using two collected `job_id` values.

This gate does not run Spark automatically. It assumes the after-run telemetry already exists in the configured telemetry store.

## Scope

- Add `compare_job_telemetry(before_job_id, after_job_id)`.
- Support NDJSON and ClickHouse-style stores.
- Compare deterministic findings before and after.
- Compare key metrics with explicit deltas.
- Expose the comparison through the local tool contract and MCP stdio.

## Metrics

- `finding_count`
- `max_skew_ratio`
- `total_spilled_bytes`
- `max_gc_ratio`
- `oom_failure_count`
- `adaptive_execution_updates`

## Status Values

- `improved`
- `regressed`
- `unchanged`
- `mixed`
- `not_comparable`

## Validation

Run:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_telemetry_compare.py tests/test_commander_tool_contract.py tests/test_commander_mcp_stdio_server.py tests/test_commander_clickhouse_adapter.py -q --basetemp .pytest-commander-gate12-code
```

Expected:

```text
38 passed
```

## Acceptance

- Before skew and after healthy telemetry returns `improved`.
- Before healthy and after skew telemetry returns `regressed`.
- Missing telemetry returns `not_comparable`.
- Fake ClickHouse adapter works.
- MCP exposes `compare_job_telemetry` as read-only.
- No remote branch is modified.
