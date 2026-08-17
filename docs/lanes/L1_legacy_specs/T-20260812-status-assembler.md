---
id: T-20260812-status-assembler
task: T1.04
lane: serve
leg: L1
effort: M
touches_paths: [serve/src/apex_mcp/diagnose.py, serve/tests/test_status.py]
depends_on: [T-20260812-serverstatus-model]
human_gated: false
---

# T1.04 — `diagnose.status()` pure assembler

## 1 · Intent

**Goal.** Turn raw health numbers into the sentence a user can act on.

**Context.** Every other diagnosis in this lane is computed by a pure function in
`diagnose.py` and handed I/O from outside — that is why `analyze()` and `compare()` are
testable without a database. Status must follow the same shape, or it becomes the one piece
of logic that needs ClickHouse to test.

## 2 · Behavior

**B-1** GIVEN health numbers, per-table column sets, resolved settings and a tool list WHEN
`status()` is called THEN it returns a `ServerStatus` and performs **no I/O**.

**B-2** GIVEN a latest ingest four minutes old WHEN `status()` runs THEN
`latest_ingest_age_seconds` is approximately 240 and `connected` is `True`.

**B-3** GIVEN `findings` missing `confidence_score` WHEN `status()` runs THEN
`contract_tables["findings"]` lists that column and `remediation` names both the column and
the infra lane as the place to fix it.

**B-4** GIVEN a reachable store with zero rows WHEN `status()` runs THEN `connected` is `True`
and `remediation` says the store is empty — **not** that it is broken.

## 3 · Contract

```bash
cd serve
uv run --extra dev pytest tests/test_status.py -q
grep -nE '(get_client|clickhouse_connect|ReadStore\()' src/apex_mcp/diagnose.py  # expect: no hits
```

**Card.** One function (~35 lines) + tests. `diagnose.py` gains no import from `ch` beyond the
`ApexStoreError` type already needed by T1.05.

**Exit.** All four behaviors covered by named tests; the I/O grep returns nothing.

## 4 · Guardrails

**Anti-patterns.** Calling `get_client()` or a `ReadStore` from inside `status()`. Emitting a
remediation string built from observed data — remediation text is **Apex's own**, and the
injection suite asserts observed text never appears in strings Apex generates. Reporting
`connected=True` on the strength of the process being alive rather than a query returning.

**No-touch.** `analyze()`, `compare()`, `suggest_fix()` and their helpers.

## 5 · Operations

- **Q. What age counts as stale?** Report the number, do not judge it — a nightly batch and a
  streaming job disagree, and a false "stale" is worse than none. *(resolved)*
- **Q. Where does the required-column set live?** `read_only_gate.py:33-59` already encodes it.
  Resolve in build: lift it to one shared constant rather than writing a second copy — a second
  copy is precisely the drift W0 is about.

## 6 · Reversal

**Rollback.** `git revert <sha>`. No tool is registered until T1.06, so nothing user-facing
changes.

**Observability.** A wrong age or a false remediation shows up in T1.19 against live data,
where the numbers are checkable by hand.

signed_off: sha256:4153a4be18ec923d0b71cecf82a6e87f
