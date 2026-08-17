---
id: T-20260812-status-store-down-e2e
task: T1.08
lane: serve
leg: L1
effort: S
touches_paths: [serve/tests/test_server_tools.py]
depends_on: [T-20260812-register-apex-status]
human_gated: false
---

# T1.08 — End-to-end: status answers while the store is down

## 1 · Intent

**Goal.** Prove the promise through the **tool boundary**, not just the pure function.

**Context.** T1.05 proves `diagnose.status()` survives a dead store. That is not the same
claim: between the function and the client sit `create_server`, `_fail()` (`server.py:40`) and
FastMCP's serialization, any of which could turn a graceful degraded response back into an
error. The claim users depend on is the end-to-end one.

## 2 · Behavior

**B-1** GIVEN a `FakeClient` that raises on every query WHEN `apex_status` is invoked through
the built server THEN it returns schema-valid `ServerStatus` with `connected=False`.

**B-2** GIVEN the same call WHEN the response is inspected THEN no `ApexStoreError` reached the
client as a tool error — the failure arrived as **data**.

**B-3** GIVEN `CLICKHOUSE_PASSWORD` set to a sentinel WHEN the degraded response is serialized
THEN the sentinel appears nowhere in it.

## 3 · Contract

```bash
cd serve
uv run --extra dev pytest tests/test_server_tools.py -q
CLICKHOUSE_PASSWORD='sentinel-pw-do-not-leak' uv run --extra dev pytest -q
```

**Card.** One fixture (a raising `FakeClient` variant) + three assertions. Test file only.

**Exit.** Both runs green; the sentinel appears in no captured output.

## 4 · Guardrails

**Anti-patterns.** Asserting on the exact remediation wording — pin the shape (`connected`,
non-empty `remediation`), not the prose, or every copy edit is a test failure. Reaching into
`diagnose.status()` directly: this task's whole value is going through the server.

**No-touch.** Source. `conftest.py`'s existing `FakeClient` behavior — extend it, do not
repoint the fixtures the other suites rely on.

## 5 · Operations

- **Q. Does this belong in `test_server_tools.py` or a new `test_status_e2e.py`?** Resolve in
  build. Preference: `test_server_tools.py` — it already owns "the tool surface behaves",
  and a fifth test file for three assertions fragments that.

## 6 · Reversal

**Rollback.** `git revert <sha>`. Test-only; nothing downstream.

**Observability.** Covers the faked outage. The **real** outage — container actually stopped —
stays a manual check and is named in the L1 definition of done.

signed_off: sha256:3869d130ad3bfd21eb0f4cd4833e3182
