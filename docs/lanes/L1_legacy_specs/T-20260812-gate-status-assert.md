---
id: T-20260812-gate-status-assert
task: T1.19
lane: serve
leg: L1
effort: M
touches_paths: [serve/tools/read_only_gate.py]
depends_on: [T-20260812-register-apex-status, T-20260812-surface-defaulted-vars]
human_gated: false
---

# T1.19 — `read_only_gate.py` asserts `apex_status`

## 1 · Intent

**Goal.** Prove the status tool against a **real** ClickHouse, not a fake.

**Context.** The unit suite runs on fakes by design — the diagnosis layer is pure. The live
gate exists for the claims only a real database can settle: that the DDL is applied, that
server-side binding survives the real parser, that `argMax` really picks the latest attempt.
`apex_status` reports on exactly those things, so a fake cannot validate it: a `FakeClient`
returns whatever column set the test author typed.

## 2 · Behavior

**B-1** GIVEN a live store with the gate's seeded rows WHEN `apex_status()` is called THEN
`connected=True` and `run_count` is greater than zero.

**B-2** GIVEN the same call WHEN `contract_tables` is read THEN it **agrees with the gate's own
independent `DESCRIBE`** at `read_only_gate.py:73` for all three tables. Two paths, one answer
— that cross-check is the point.

**B-3** GIVEN freshly seeded rows WHEN status reports THEN `latest_ingest_age_seconds` is small
and positive, consistent with the fixture timestamps.

**B-4** GIVEN the gate completes WHEN it prints its JSON THEN a `status` block is included and
the overall result is `"status": "passed"`.

## 3 · Contract

```bash
cd serve
uv run python tools/read_only_gate.py | tee /tmp/gate.json
python3 -c "
import json; g = json.load(open('/tmp/gate.json'))
assert g['status'] == 'passed', g
s = g['status_tool']
assert s['connected'] and s['run_count'] > 0, s
assert s['contract_tables'] == g['describe_missing'], (s['contract_tables'], g['describe_missing'])
print('status block agrees with DESCRIBE')"
```

**Card.** One assertion block in the existing gate + its JSON output section. No source change.

**Exit.** Gate prints `"status": "passed"` with a `status_tool` block; the cross-check against
`DESCRIBE` passes.

## 4 · Guardrails

**Anti-patterns.** Building the expected column set from `table_columns()` — that is the code
under test, and comparing it to itself proves nothing. Use the gate's independent `DESCRIBE`.
Leaving fixture rows behind: the gate deletes only its own rows and verifies none remain, and
this addition must not weaken that.

**No-touch.** The existing contract-conformance, `argMax` and injection assertions. This task
**adds** a block; it rewrites none.

## 5 · Operations

- **Q. Does `run_count > 0` hold when the gate runs against an otherwise-empty cluster?** Yes —
  the gate seeds its own rows first. Order the assertion after seeding. *(resolved)*
- **Q. Should the gate also assert the degraded path?** No. It needs the database **stopped**,
  which a gate that connects to it cannot arrange. That stays the manual check named in the
  L1 definition of done.

## 6 · Reversal

**Rollback.** `git revert <sha>`. Gate-only; the tool itself is unaffected.

**Observability.** This gate **is** the observability for the live claims. Its recorded output
belongs in `VALIDATION.md` via T1.21.

signed_off: sha256:9cf397b62582247bf892653b26e281ff
