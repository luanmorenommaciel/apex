---
id: T-20260812-startup-stderr-banner
task: T1.11
lane: serve
leg: L1
effort: S
touches_paths: [serve/src/apex_mcp/server.py, serve/tests/test_server_tools.py]
depends_on: [T-20260812-resolve-settings-extract]
human_gated: false
---

# T1.11 — Startup stderr banner

## 1 · Intent

**Goal.** Answer "which ClickHouse did the client actually spawn me against?" without a round
trip.

**Context.** MCP servers are spawned as subprocesses by a client whose config the user may not
have written. When Apex looks empty, the first thing anyone needs is proof of which endpoint
it resolved. One stderr line at startup gives that away for free — and stderr is safe, because
**stdout is the JSON-RPC channel** and a single stray byte there corrupts framing.

## 2 · Behavior

**B-1** GIVEN the server starts WHEN it initializes THEN one line on **stderr** names host,
port, database and `secure`.

**B-2** GIVEN the server starts WHEN it is launched with immediate EOF THEN **stdout receives
zero bytes**.

**B-3** GIVEN `CLICKHOUSE_PASSWORD` is set WHEN the banner is written THEN the password does
not appear, in any form, redacted placeholder or not.

**B-4** GIVEN `APEX_LOG_LEVEL=WARNING` WHEN the server starts THEN the banner is suppressed
along with other INFO output — it is a log line, not a `print`.

## 3 · Contract

```bash
cd serve
uv run --extra dev pytest tests/test_server_tools.py -q
CLICKHOUSE_PASSWORD='sentinel-pw-do-not-leak' \
  uv run apex-mcp </dev/null >/tmp/apex-stdout.bin 2>/tmp/apex-stderr.txt; \
  test ! -s /tmp/apex-stdout.bin && echo "stdout: 0 bytes OK"; \
  grep -q 'sentinel-pw' /tmp/apex-stderr.txt && echo "LEAK" || echo "no leak OK"; \
  cat /tmp/apex-stderr.txt
```

**Card.** One `log.info` in `main()`/`_configure_logging()` + one subprocess test following the
existing stdout-cleanliness pattern.

**Exit.** All four behaviors covered; the manual run prints `stdout: 0 bytes OK` and
`no leak OK`.

## 4 · Guardrails

**Anti-patterns.** `print()` — anywhere in `src/apex_mcp/`, for any reason. Logging the
`password` field even masked; do not read it here at all. Emitting the banner from module
import rather than `main()`, which would fire during unit tests and in any tool importing the
package.

**No-touch.** The logging configuration's stderr-only stream handler. `stdout` in every sense.

## 5 · Operations

- **Q. One line or a block?** One. This is orientation, not a report — `apex_status()` is the
  report. *(resolved)*
- **Q. Include the resolved `defaulted` list?** Resolve in build. Leaning yes, compactly
  (`defaults: host,port`) — it is the cheapest possible hint for the most common misconfiguration.

## 6 · Reversal

**Rollback.** `git revert <sha>`. Log-only; no behavior depends on it.

**Observability.** The banner **is** observability. Its own risk — a stray byte on stdout — is
covered by B-2 and by the pre-existing subprocess test.

signed_off: sha256:ec3aa03bc6fc4dd239d3b60b6f4a1459
