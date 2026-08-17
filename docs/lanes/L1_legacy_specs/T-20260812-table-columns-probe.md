---
id: T-20260812-table-columns-probe
task: T1.03
lane: serve
leg: L1
effort: S
touches_paths: [serve/src/apex_mcp/ch.py, serve/tests/test_ch.py]
depends_on: []
human_gated: false
---

# T1.03 — Generalize `findings_columns()` → `table_columns(table)`

## 1 · Intent

**Goal.** Let the status tool report contract conformance for all three tables, not just
`findings`.

**Context.** `findings_columns()` (`ch.py:214`) probes `system.columns` for one hardcoded
table so the `findings` SELECT can be built from what is actually present. That probe is
exactly why serve degraded gracefully while the engine's write path was dead — it is the
lane's best idea and it currently applies to one table out of three.

## 2 · Behavior

**B-1** GIVEN `table_columns("spark_events")` WHEN the table exists THEN it returns that
table's column names as a set.

**B-2** GIVEN `findings_columns()` WHEN called THEN it returns exactly what it returns today —
callers and cache behavior unchanged.

**B-3** GIVEN a table name outside the allowlist `{spark_events, findings, plan_transitions}`
WHEN `table_columns` is called THEN it raises `ApexStoreError` **before** any query is issued.

## 3 · Contract

```bash
cd serve
git stash list >/dev/null
uv run --extra dev pytest tests/test_ch.py -q
git diff --stat HEAD -- tests/test_ch.py   # existing additive-column test must be UNMODIFIED
```

**Card.** One method generalized, one thin back-compat caller, one allowlist constant.
Additions only to `tests/test_ch.py`.

**Exit.** The pre-existing additive-column test passes with **zero diff lines against it**;
new tests cover a second table and the allowlist rejection.

## 4 · Guardrails

**Anti-patterns.** Interpolating `table` into SQL — bind it, and gate it on the allowlist
first. Dropping the `lru_cache`/memoization the current probe relies on. Widening the
allowlist to "any table in the apex database".

**No-touch.** `_findings_sql()` and the SELECT-building logic that consumes the probe. Changing
how `findings` behaves is out of scope; this task only widens who can ask.

## 5 · Operations

- **Q. Is the allowlist worth it when the caller is internal?** Yes — `table_columns` becomes
  reachable from a tool argument the moment anyone adds a table parameter downstream. The
  allowlist costs three lines and closes that before it opens. *(resolved)*
- **Q. Cache per-table or one call for all three?** Resolve in build; prefer per-table with the
  existing caching so a missing table degrades one entry, not all of them.

## 6 · Reversal

**Rollback.** `git revert <sha>` — `findings_columns()` is preserved as a caller, so revert
restores the original shape exactly.

**Observability.** T1.19 cross-checks this probe against the gate's independent `DESCRIBE`
at `read_only_gate.py:73`; a divergence between the two means this task regressed.

signed_off: sha256:8fea8e2858068f2f5b66e35dfc398ce4
