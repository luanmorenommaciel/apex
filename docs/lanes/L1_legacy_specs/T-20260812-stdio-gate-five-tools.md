---
id: T-20260812-stdio-gate-five-tools
task: T1.20
lane: serve
leg: L1
effort: S
touches_paths: [serve/tools/mcp_stdio_gate.py]
depends_on: [T-20260812-register-apex-status]
human_gated: false
---

# T1.20 — `mcp_stdio_gate.py` asserts five tools

## 1 · Intent

**Goal.** Confirm the new tool over a **real MCP client on real stdio**.

**Context.** `test_server_tools.py` calls `list_tools()` in-process. That skips JSON-RPC
framing, the client handshake, and the serialization path — precisely where a stray stdout byte
or a schema the client rejects would show up. The stdio gate is the only check that exercises
the protocol as a user's client will.

## 2 · Behavior

**B-1** GIVEN the server spawned over stdio WHEN the official `mcp` client lists tools THEN it
sees exactly five, `apex_status` among them.

**B-2** GIVEN that listing WHEN annotations are read THEN `apex_status` carries
`readOnlyHint=true` and `openWorldHint=false`.

**B-3** GIVEN `apex_status` invoked through the client WHEN the response returns THEN it is
schema-valid structured output.

**B-4** GIVEN the whole session WHEN it completes THEN no framing error occurred — proof that
nothing wrote to stdout outside the JSON-RPC channel.

## 3 · Contract

```bash
cd serve
uv run python tools/mcp_stdio_gate.py
npx @modelcontextprotocol/inspector uvx --from . apex-mcp   # manual cross-check, optional
```

**Card.** Update the contracted-tool list at `mcp_stdio_gate.py:5` and its assertions. No source
change.

**Exit.** Gate passes; five tools listed with correct annotations; `apex_status` returns
schema-valid output.

## 4 · Guardrails

**Anti-patterns.** Softening the assertion to "contains `apex_status`". The gate's value is
that it pins the **exact** surface a client sees; a subset check would miss a tool that should
not be there. Skipping the annotation assertion because "it is read-only anyway" — the
annotation is what the client acts on.

**No-touch.** The `suggest_fix` assertions, which pin `applied=false` and
`requires_human_approval=true` over the wire. Those are the lane's headline safety claims.

## 5 · Operations

- **Q. Does the tool order over the wire match the in-process order T1.07 pins?** Verify during
  the run. If FastMCP does not guarantee ordering across transports, this gate asserts a **set**
  while T1.07 asserts the ordered list in-process — and that difference gets written down here.

## 6 · Reversal

**Rollback.** `git revert <sha>` alongside T1.06.

**Observability.** This gate is the closest thing to a user's own client. It is manual — run it
before any release, and record the result in `VALIDATION.md`.

signed_off: sha256:54929fe2f4e7768f3dae35d473fbb8b7
