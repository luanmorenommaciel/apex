---
id: T-20260812-register-apex-status
task: T1.06
lane: serve
leg: L1
effort: S
touches_paths: [serve/src/apex_mcp/server.py]
depends_on: [T-20260812-status-assembler, T-20260812-status-degraded-path, T-20260812-store-health-query, T-20260812-table-columns-probe]
human_gated: false
---

# T1.06 — Register the `apex_status` tool

## 1 · Intent

**Goal.** Expose the fifth tool.

**Context.** This is the commit where the lane stops having four tools. Everything before it
was additive and invisible; from here the surface has changed and the assertions that pin it
must move (T1.07 for the test, T1.21 for the docs). Those are deliberately separate commits so
the breach of a frozen guarantee is legible in `git log` rather than buried in a refactor.

## 2 · Behavior

**B-1** GIVEN a built server WHEN `list_tools()` is called THEN `apex_status` is present with
`readOnlyHint=True` and `openWorldHint=False`.

**B-2** GIVEN `apex_status()` is invoked WHEN the store is reachable THEN it returns
schema-valid structured output matching `ServerStatus`.

**B-3** GIVEN the server module WHEN its docstring is read THEN it describes five tools, and
still states that stdout is the JSON-RPC channel.

**B-4** GIVEN the tool WHEN it runs THEN it issues `SELECT`s only — it inherits `READ_ONLY`,
not `PROPOSAL_ONLY`.

## 3 · Contract

```bash
cd serve
uv run --extra dev pytest -q                      # T1.07 not yet done → the four-tools test FAILS
uv run python -c "
import asyncio
from apex_mcp.server import create_server
from tests.conftest import FakeClient
from apex_mcp.ch import ReadStore
s = create_server(ReadStore(FakeClient()))
print([(t.name, t.annotations.readOnlyHint) for t in asyncio.run(s.list_tools())])"
```

**Card.** One `@mcp.tool` block (~15 lines) + a docstring edit. `server.py` only.

**Exit.** The printed list has five entries with `apex_status` read-only. **The suite is
expected to be red on exactly one assertion** — `test_exactly_the_four_contracted_tools`. Any
other failure means this task broke something it should not have.

## 4 · Guardrails

**Anti-patterns.** Fixing the failing test in this commit — that is T1.07, and merging them
hides the surface change. Annotating with `PROPOSAL_ONLY`. Adding parameters: `apex_status()`
takes none in v1, so there is no user-influenced input and no new injection surface.

**No-touch.** The four existing tool bodies, `READ_ONLY` / `PROPOSAL_ONLY`, `_fail()`.

## 5 · Operations

- **Q. Should this also be an MCP `resource` (`apex://status`)?** Not here. Resources are an L2
  concern and mixing the first resource into the fifth tool's commit muddies both. *(resolved)*
- **Q. Tool name — `apex_status`, `status`, or `health`?** `apex_status`: tool names are flat
  across all servers a client has loaded, and a bare `status` collides. *(resolved)*

## 6 · Reversal

**Rollback.** `git revert <sha>` restores the four-tool surface. If T1.07 already landed,
revert both — that pair is atomic in effect even though it is two commits.

**Observability.** `claude mcp list` and `/mcp` show the tool count; T1.20 pins it in the stdio
gate.

signed_off: sha256:3214d35b16db682f90d6f1c11c5c3979
