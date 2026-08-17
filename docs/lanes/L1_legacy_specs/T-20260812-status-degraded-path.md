---
id: T-20260812-status-degraded-path
task: T1.05
lane: serve
leg: L1
effort: S
touches_paths: [serve/src/apex_mcp/diagnose.py, serve/tests/test_status.py]
depends_on: [T-20260812-status-assembler]
human_gated: false
---

# T1.05 — Degraded path: survive an unreachable store

## 1 · Intent

**Goal.** `apex_status` must answer **while ClickHouse is down**. That is the whole point of
the tool; a status call that fails when things are broken is a status call that only works
when you don't need it.

**Context.** `get_client()` is deliberately lazy (`ch.py:302`) so the server finishes
`initialize` and lists its tools with the database down. The consequence today is four
healthy-looking tools that fail on every call. This task is where that inversion gets paid
back — one tool that reports the failure instead of reproducing it.

## 2 · Behavior

**B-1** GIVEN a store whose every query raises `ApexStoreError` WHEN `status()` is called THEN
it returns `ServerStatus(connected=False)` and **does not raise**.

**B-2** GIVEN that same failure WHEN the result is read THEN `degraded_reason` carries the
sanitized code (`clickhouse_unavailable`, `clickhouse_schema_missing`, …) and `remediation`
carries a next action in plain language.

**B-3** GIVEN a store raising a **non**-`ApexStoreError` exception WHEN `status()` is called
THEN that exception propagates — this task swallows the sanitized failure mode only, never an
unexpected bug.

**B-4** GIVEN any degraded response WHEN it is serialized THEN no credential appears in any
field, including `degraded_reason`.

## 3 · Contract

```bash
cd serve
uv run --extra dev pytest tests/test_status.py -q -k degraded
CLICKHOUSE_PASSWORD='sentinel-pw-do-not-leak' uv run --extra dev pytest tests/test_status.py -q
```

**Card.** A `try/except ApexStoreError` around the health reads plus a degraded constructor
(~15 lines) and four tests.

**Exit.** All four behaviors covered; the sentinel password appears in no assertion output and
no returned field.

## 4 · Guardrails

**Anti-patterns.** A bare `except Exception` — that is how B-3 gets violated and a real bug
gets reported as "database down". Re-deriving the remediation text from the exception message
instead of mapping the sanitized code. Retry loops: status reports, it does not repair.

**No-touch.** `_sanitize()` in `ch.py`. Its message set is the contract this task consumes;
changing it belongs to T1.10.

## 5 · Operations

- **Q. Should a partial failure — health works, column probe does not — be `connected=True`?**
  **Yes**, with the failing probe recorded in `degraded_reason`. Connectivity and conformance
  are different questions and collapsing them loses the more useful answer. *(resolved)*

## 6 · Reversal

**Rollback.** `git revert <sha>` — returns `status()` to raising, which T1.06 has not yet
exposed to a client.

**Observability.** The one failure mode that stays invisible in CI: it needs the database
**actually stopped**, not faked. T1.19 covers the live-up case; stopping the container by hand
is the check for this one, and the DoD names it.

signed_off: sha256:b714d9361c7466dc069ea303c48f6537
