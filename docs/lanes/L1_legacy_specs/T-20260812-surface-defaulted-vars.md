---
id: T-20260812-surface-defaulted-vars
task: T1.12
lane: serve
leg: L1
effort: S
touches_paths: [serve/src/apex_mcp/diagnose.py, serve/src/apex_mcp/server.py, serve/tests/test_status.py]
depends_on: [T-20260812-serverstatus-model, T-20260812-resolve-settings-extract]
human_gated: false
---

# T1.12 — Surface defaulted vars in `ServerStatus`

## 1 · Intent

**Goal.** Let `apex_status` say *"`CLICKHOUSE_HOST` was never set; defaulting to 127.0.0.1"*.

**Context.** The single most common way Apex looks broken is being pointed at a default
endpoint the user never chose — and because every variable has a working local default, this
failure is completely silent. `resolve_settings().defaulted` (T1.09) already computes the
answer; this task carries it to the surface.

## 2 · Behavior

**B-1** GIVEN no `CLICKHOUSE_*` set WHEN `apex_status()` is called THEN `using_defaults` lists
all six variable names.

**B-2** GIVEN all six set WHEN `apex_status()` is called THEN `using_defaults` is empty.

**B-3** GIVEN `using_defaults` is non-empty **and** the store is empty WHEN the result is read
THEN `remediation` connects the two — a default endpoint with no data is the classic
"pointed at the wrong ClickHouse", and saying so is the entire value of this task.

**B-4** GIVEN any response WHEN it is serialized THEN `using_defaults` contains variable
**names** only, never their values.

## 3 · Contract

```bash
cd serve
env -u CLICKHOUSE_HOST -u CLICKHOUSE_PORT -u CLICKHOUSE_USER \
    -u CLICKHOUSE_PASSWORD -u CLICKHOUSE_DATABASE -u CLICKHOUSE_SECURE \
  uv run --extra dev pytest tests/test_status.py -q -k defaults
uv run --extra dev pytest -q
```

**Card.** One field populated in the assembler + the wiring in the tool body + four tests.

**Exit.** All four behaviors covered; the full suite green.

## 4 · Guardrails

**Anti-patterns.** Including values — `CLICKHOUSE_PASSWORD` is one of the six names, and
emitting its value would be a credential leak dressed as a diagnostic. Treating defaults as an
error: a local dev stack legitimately runs on all six, so this is information, never a failure.

**No-touch.** `resolve_settings()` itself — consume it, do not extend it.

## 5 · Operations

- **Q. Is `CLICKHOUSE_PASSWORD` safe to name in the list?** Yes. The **name** is public — it is
  documented in the README table and committed in `.mcp.json`. Only the value is secret.
  *(resolved)*

## 6 · Reversal

**Rollback.** `git revert <sha>` — the field stays on the model, empty. Harmless.

**Observability.** T1.19 asserts the live gate sees `using_defaults` consistent with the
environment the gate itself ran under.

signed_off: sha256:f5ad431d3641572182e5045ec787427b
