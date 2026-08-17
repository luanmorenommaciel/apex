---
id: T-20260812-name-endpoint-in-error
task: T1.10
lane: serve
leg: L1
effort: S
touches_paths: [serve/src/apex_mcp/ch.py, serve/tests/test_injection_hardening.py]
depends_on: [T-20260812-resolve-settings-extract]
human_gated: false
---

# T1.10 — Name the resolved endpoint in `clickhouse_unavailable`

## 1 · Intent

**Goal.** Tell the user which endpoint failed, without telling them anything secret.

**Context.** The message says *"Check the `CLICKHOUSE_*` environment of the MCP server"*
(`ch.py:283`) and names no value, so the user cannot tell whether the server tried the host
they meant. **This task pulls against the security rail** — `_sanitize()` exists precisely to
keep driver internals away from the model. The distinction being drawn: the *endpoint* is
configuration the user supplied and can see; the *credential* is not. Only the first moves.

## 2 · Behavior

**B-1** GIVEN a connection failure against `10.0.0.5:9000/apex` WHEN the error surfaces THEN
the message contains host, port and database.

**B-2** GIVEN `CLICKHOUSE_PASSWORD` set to a sentinel WHEN **any** sanitized error is produced
THEN the sentinel appears in none of them.

**B-3** GIVEN a connection failure WHEN the message is read THEN `CLICKHOUSE_USER` does not
appear — a username is a credential half.

**B-4** GIVEN a driver exception carrying a full DSN in its own text WHEN sanitized THEN none
of that original text is forwarded; the message is still built from **our** resolved values.

## 3 · Contract

```bash
cd serve
uv run --extra dev pytest tests/test_injection_hardening.py -q
CLICKHOUSE_PASSWORD='sentinel-pw-do-not-leak' CLICKHOUSE_USER='sentinel-user' \
  uv run --extra dev pytest -q
```

**Card.** One message template in `_sanitize()`; tests land in the injection/disclosure suite
because that is the property at risk.

**Exit.** All four behaviors covered; both sentinels absent from every sanitized message.

## 4 · Guardrails

**Anti-patterns.** Interpolating `str(exc)` into the returned message — B-4 is the whole point;
driver text is where the DSN lives. Adding the username "since it isn't the password".
Widening the same treatment to `clickhouse_query_failed`: a query failure is not a
configuration problem and does not need an endpoint.

**No-touch.** The stderr log line in `_sanitize()` — it keeps the full exception, and that is
correct; stderr is the operator's channel, not the model's.

## 5 · Operations

- **Q. Should the endpoint appear in `clickhouse_schema_missing` too?** Yes — "which database
  is missing the schema" is the same class of question. Keep it out of the generic
  `clickhouse_query_failed`. *(resolved)*
- **Q. Reviewer sign-off?** This one changes a security-relevant message. Flag it for a second
  reader; record who reviewed it here when merged.

## 6 · Reversal

**Rollback.** `git revert <sha>` restores the opaque message. Safe to revert at any point —
nothing depends on the added detail.

**Observability.** The sentinel tests are the standing guard: they run on every suite
invocation, so a later edit that reintroduces a credential fails immediately.

signed_off: sha256:726f7dee51f7aa0bac160487f01836bb
