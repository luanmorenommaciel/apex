# Gate 11: Guarded Apply/Verify

Date: 2026-07-11
Branch: `gustocezar/feature/codex-desacoplamento-geradores`
Prepared by: Codex

## Goal

Close the local loop from preview to guarded apply and hash verification, without exposing a raw `apply_fix`.

## Scope

- Add preview hashes: `before_sha256`, `after_sha256`, and `diff_sha256`.
- Add an approval token to `preview_recommendation`.
- Add `apply_recommendation` guarded by `approval_token` and `apply_root`.
- Add `verify_recommendation_apply` for final hash verification.
- Expose the new tools through the local contract and MCP stdio.

## Guardrails

- No `apply_root`, no write.
- Path outside `apply_root`, no write.
- Invalid approval token, no write.
- File changed since preview, token mismatch and no write.
- Final hash verification runs after successful write.
- `apply_fix` remains absent.

## Data Flow

```text
preview_recommendation
  -> approval.token
  -> apply_recommendation
  -> write only inside apply_root
  -> verify_recommendation_apply
  -> verified / mismatch
```

## Validation

Run:

```powershell
$env:PYTHONUTF8='1'
uv run --offline --with-requirements requirements.txt python -m pytest tests/test_commander_apply_verify.py tests/test_commander_recommendations.py tests/test_commander_tool_contract.py tests/test_commander_mcp_stdio_server.py tests/test_commander_fix_preview.py -q --basetemp .pytest-commander-gate11-code
```

Expected:

```text
38 passed
```

## Acceptance

- Preview returns approval metadata.
- Apply without `apply_root` is blocked.
- Apply outside `apply_root` is blocked.
- Apply with invalid token is blocked.
- Apply with valid token writes only the target file.
- Verification confirms the final hash.
- MCP marks `apply_recommendation` as non-read-only.
- No remote branch is modified.
