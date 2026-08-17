---
id: T-20260812-resolve-settings-extract
task: T1.09
lane: serve
leg: L1
effort: S
touches_paths: [serve/src/apex_mcp/ch.py, serve/tests/test_ch.py]
depends_on: []
human_gated: false
---

# T1.09 — Extract `resolve_settings()` out of `get_client()`

## 1 · Intent

**Goal.** Make the resolved configuration inspectable without opening a connection.

**Context.** The six `os.getenv` calls live inline inside the `lru_cache`d factory
(`ch.py:302-324`). Nothing can ask "what host did we resolve to, and which of these were
defaults?" without constructing a client — which is exactly the question you need answered
when the client cannot be constructed. This extraction unblocks T1.10, T1.11 and T1.12.

## 2 · Behavior

**B-1** GIVEN no `CLICKHOUSE_*` variables WHEN `resolve_settings()` is called THEN it returns
today's defaults — `127.0.0.1`, `8123`, `apex`, `apex` — and `defaulted` lists all six.

**B-2** GIVEN every variable set WHEN `resolve_settings()` is called THEN it reflects them and
`defaulted` is empty.

**B-3** GIVEN `CLICKHOUSE_SECURE` in `{1, true, yes}` in any case WHEN resolved THEN `secure`
is `True`; any other value is `False` — matching current behavior exactly.

**B-4** GIVEN `get_client()` WHEN called THEN it behaves as before, now via `resolve_settings()`.

## 3 · Contract

```bash
cd serve
uv run --extra dev pytest tests/test_ch.py -q
git diff HEAD -- tests/test_ch.py | grep '^-' | grep -v '^---'   # expect: no deletions
```

**Card.** One frozen dataclass + one function (~20 lines); `get_client()` shrinks to a caller.
Tests added, none rewritten.

**Exit.** All four behaviors covered; no existing test line was deleted to make it pass.

## 4 · Guardrails

**Anti-patterns.** Putting `password` on the returned dataclass. It is needed **only** by
`get_client()`, and once it is a field it will end up rendered by T1.11 or T1.12 by accident —
read it separately at the point of use. Caching `resolve_settings()`: the env can change
between a client build and a status call, and a stale answer is worse than none.

**No-touch.** The `lru_cache` on `get_client()`, the default values themselves, and
`_sanitize()` (that is T1.10).

## 5 · Operations

- **Q. Is `port` an `int` or a `str`?** `int`, converted here, so a non-numeric
  `CLICKHOUSE_PORT` fails at resolution with a clear message rather than deep in the driver.
  *(resolved)*
- **Q. Does `defaulted` mean "unset" or "set to the default value"?** **Unset.** Someone who
  deliberately set `127.0.0.1` should not be told they forgot. *(resolved)*

## 6 · Reversal

**Rollback.** `git revert <sha>` — pure refactor, `get_client()`'s observable behavior is
unchanged either way.

**Observability.** Any drift between resolved settings and the real connection shows up in
T1.11's startup banner, printed from this same function.

signed_off: sha256:2a32529428caa0633b20634bec2c342f
