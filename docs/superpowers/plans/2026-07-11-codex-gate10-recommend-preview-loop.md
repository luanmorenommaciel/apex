# Gate 10: Recommend/Preview Loop

Date: 2026-07-11
Branch: `gustocezar/feature/codex-desacoplamento-geradores`
Prepared by: Codex

## Goal

Create a local closed loop up to preview:

```text
persisted validated finding -> deterministic recommendation -> preview diff
```

This gate must not apply changes, push branches, or require an LLM for the baseline path.

## Scope

- Add deterministic recommendation rules for Commander finding kinds.
- Expose `recommend_fix(job_id)` as a read-only tool.
- Expose `preview_recommendation(job_id, recommendation_id, path, replacement)` as a read-only tool.
- Keep `preview_fix` as the lower-level compatibility tool.
- Keep `apply_fix` absent.

## Finding Coverage

- `shuffle_skew_candidate`
- `shuffle_spill_candidate`
- `gc_pressure_candidate`
- `oom_candidate`
- `plan_aqe_replan_candidate`
- unknown finding kinds fall back to manual review.

## Data Flow

```text
ClickHouseFindingStore
  -> query_by_job_id(job_id)
  -> recommend_fix
  -> recommendation_id
  -> preview_recommendation
  -> unified diff
```

## Validation

Run:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_recommendations.py tests/test_commander_tool_contract.py tests/test_commander_mcp_stdio_server.py tests/test_commander_clickhouse_findings.py -q --basetemp .pytest-commander-gate10-code
```

Expected:

```text
30 passed
```

## Acceptance

- `recommend_fix` returns structured recommendations only from accepted validations.
- `preview_recommendation` verifies the selected `recommendation_id`.
- Preview returns a diff and preserves the target file.
- MCP `tools/list` exposes both tools as read-only.
- `apply_fix` remains rejected as `unknown_tool`.
- No remote branch is modified.
