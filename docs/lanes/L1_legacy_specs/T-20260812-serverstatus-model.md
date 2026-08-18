---
id: T-20260812-serverstatus-model
task: T1.01
lane: serve
leg: L1
effort: S
touches_paths: [serve/src/apex_mcp/models.py, serve/tests/test_status.py]
depends_on: []
human_gated: false
---

# T1.01 — `ServerStatus` Pydantic model

## 1 · Intent

**Goal.** Define the typed payload `apex_status()` will return, before anything produces one.

**Context.** `models.py` already holds `Diagnosis`, `RunComparison`, `KbHits` and
`FixSuggestion`. FastMCP generates each tool's output schema from its return annotation, and
that schema constraint is one of the lane's stated OWASP mitigations — it lets a client reject
a malformed response and stops free text riding along. A status tool returning a bare dict
would be the single hole in that property.

## 2 · Behavior

**B-1** GIVEN no arguments but `connected=False` WHEN a `ServerStatus` is constructed THEN it
validates, with every remaining field taking a default.

**B-2** GIVEN the class WHEN `model_json_schema()` is called THEN it renders, with `connected`
required and boolean.

**B-3** GIVEN any `ServerStatus` WHEN it is serialized THEN there is no field capable of
carrying a credential — no `user`, no `password`, no `dsn`, no connection URL.

## 3 · Contract

```bash
cd serve
uv run --extra dev pytest tests/test_status.py -q
uv run python -c "from apex_mcp.models import ServerStatus; \
  print(sorted(ServerStatus(connected=False).model_dump().keys()))"
grep -nE '\b(password|dsn|secret|user)\b' src/apex_mcp/models.py   # expect: no hits
```

**Card.** One model in `models.py` (~20 lines) + one new test file. No other file changes.

**Exit.** `tests/test_status.py` green; the printed key list contains `connected`, `database`,
`run_count`, `latest_ingest_age_seconds`, `contract_tables`, `using_defaults`,
`degraded_reason`, `remediation`, `tools`; the grep returns nothing.

## 4 · Guardrails

**Anti-patterns.** Returning `dict[str, Any]` instead of a model. Adding a `dsn` or
`password` field "for debugging". Importing `ch` or `diagnose` into `models.py` — that module
has no intra-package runtime dependency today and must keep none.

**No-touch.** `server.py`, `ch.py`, `diagnose.py`. Do **not** register a tool in this task.

## 5 · Operations

- **Q. Is `latest_ingest_age_seconds` a field or computed by the client?**
  **A. A field.** The client must not have to reason about the server's clock. *(resolved)*
- **Q. Does `contract_tables` report missing columns, present columns, or both?**
  Resolve in build; default to **missing-only** to keep the payload small.

## 6 · Reversal

**Rollback.** `git revert <sha>` — nothing imports `ServerStatus` until T1.04, so the revert
touches no caller.

**Observability.** If the model later drifts from what `apex_status` actually returns,
FastMCP's generated output schema stops matching and the schema-validity assertion in
`tests/test_server_tools.py` fails.

signed_off: sha256:4c7d4774719599a6fbba8028e2bef88a
