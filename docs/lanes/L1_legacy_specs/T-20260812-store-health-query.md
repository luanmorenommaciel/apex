---
id: T-20260812-store-health-query
task: T1.02
lane: serve
leg: L1
effort: S
touches_paths: [serve/src/apex_mcp/ch.py, serve/tests/test_ch.py]
depends_on: []
human_gated: false
---

# T1.02 — `ReadStore.store_health()`

## 1 · Intent

**Goal.** One read that answers "is there data, and how fresh is it?"

**Context.** `ReadStore` (`ch.py:197`) can fetch stages, findings, plan transitions and search
hits — all keyed by a `job_id`. None of them answers the question a new user actually has.
A connected-but-empty Apex is currently indistinguishable from a broken one.

## 2 · Behavior

**B-1** GIVEN a store holding runs WHEN `store_health()` is called THEN it returns total row
count, distinct `job_id` count, and the maximum `ts` in `apex.spark_events`.

**B-2** GIVEN an empty but reachable `apex.spark_events` WHEN `store_health()` is called THEN
it returns zeros and a null timestamp — **it does not raise**.

**B-3** GIVEN an unreachable store WHEN `store_health()` is called THEN it raises
`ApexStoreError` with the existing sanitized code, exactly as every other read does.

## 3 · Contract

```bash
cd serve
uv run --extra dev pytest tests/test_ch.py -q
python3 - <<'PY'
import re, pathlib
src = pathlib.Path("src/apex_mcp/ch.py").read_text()
sql = re.findall(r'"""\s*\n?\s*SELECT.*?"""', src, re.S)
assert not any("{" in s for s in sql), "interpolation inside a SQL literal"
print(f"{len(sql)} SQL constants, none interpolated")
PY
```

**Card.** One module-level SQL constant beside the existing ones + one `ReadStore` method
(~12 lines) + tests in the existing file.

**Exit.** `test_ch.py` green including a new empty-table case; the interpolation check passes.

## 4 · Guardrails

**Anti-patterns.** Building the SQL with an f-string. Bypassing `_query()` and so losing
`_sanitize()`. `SELECT *`. Any scan not bounded to `apex.spark_events`.

**No-touch.** The four existing `ReadStore` methods and their SQL constants. `models.py`,
`server.py`, `diagnose.py`.

## 5 · Operations

- **Q. Count over all time, or a window?** All time for v1 — `count()` on a MergeTree is
  cheap. Revisit if a cluster makes it slow; the answer belongs in this file when it changes.
- **Q. Does freshness use `max(ts)` or ingestion time?** `max(ts)` — the contract column.
  Note in the docstring that clock skew on the emitter surfaces here.

## 6 · Reversal

**Rollback.** `git revert <sha>`. No caller until T1.04.

**Observability.** A wrong answer becomes visible the moment T1.19 wires this into the live
gate against a real seeded run.

signed_off: sha256:34c6d625696f6d40430685cb42d9cddd
