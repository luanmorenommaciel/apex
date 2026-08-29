---
id: T-20260812-root-mcp-json
task: T1.17
lane: serve
leg: L1
effort: S
touches_paths: [.mcp.json, serve/tests/test_config_parity.py]
depends_on: []
human_gated: false
---

# T1.17 — Root `.mcp.json` + drift test

## 1 · Intent

**Goal.** Make project-scope config work without a manual copy step.

**Context.** `serve/.mcp.json` documents that it *"must be copied (or symlinked) to the
repository root to activate it for everyone working in the repo"* — and nothing performs that
copy. Clients look at the root. As written, project scope is a instruction nobody executed.

## 2 · Behavior

**B-1** GIVEN a fresh clone WHEN a client opens the repo THEN `.mcp.json` at the root is found
and the `apex` server is offered — no manual step.

**B-2** GIVEN both files WHEN parsed THEN their `mcpServers` blocks are **identical**; only the
`_comment` key may differ.

**B-3** GIVEN either file edited alone WHEN the suite runs THEN the parity test fails and names
both paths.

**B-4** GIVEN the root file WHEN inspected THEN it is a **regular file**, not a symlink —
Codex on Windows and some client sandboxes do not follow symlinks.

## 3 · Contract

```bash
cd /opt/projects/dataship/git/apex
test -f .mcp.json && test ! -L .mcp.json && echo "regular file OK"
python3 - <<'PY'
import json, pathlib
a = json.loads(pathlib.Path(".mcp.json").read_text())
b = json.loads(pathlib.Path("serve/.mcp.json").read_text())
assert a["mcpServers"] == b["mcpServers"], "drift between root and serve/"
print("mcpServers identical")
PY
cd serve && uv run --extra dev pytest tests/test_config_parity.py -q
```

**Card.** One new root file + one new test file (~25 lines).

**Exit.** `regular file OK`, `mcpServers identical`, parity test green.

## 4 · Guardrails

**Anti-patterns.** A symlink (B-4). Generating the root file at build time — it must exist in a
fresh clone, before anything has run. Letting the two copies diverge "temporarily"; the test
exists because this repo already carries **two hand-maintained copies of one schema** in
`infra/sql/` and `collect/ddl/`, and W0 is the bill for that pattern going unchecked.

**No-touch.** The `mcpServers` content itself — env var names, defaults and the `${VAR:-default}`
expansion are settled. This task duplicates and guards; it does not redesign.

## 5 · Operations

- **Q. Which file is the source of truth?** `serve/.mcp.json` — the lane owns it, and the root
  copy is the published artifact. Say so in the root file's `_comment`. *(resolved)*
- **Q. Could a generator replace the duplication?** Yes, and it would be a better answer at
  repo scale — the same argument applies to `infra/sql/` vs `collect/ddl/`. Out of scope here;
  the test buys the same safety for 25 lines.

## 6 · Reversal

**Rollback.** `git revert <sha>` removes the root file. Users fall back to the documented
manual copy, exactly as today.

**Observability.** The parity test is the guard. Without it, drift between the two copies is
silent until a developer's client loads stale config — the same failure shape as W0.

signed_off: sha256:49143737daa1af1d6a8e9f2e3c8d69af
