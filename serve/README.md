# serve/ — ⑥ interface

**Role:** Apex MCP server. Exposes Spark diagnosis to Claude Code / Cursor / Codex over stdio.
**Language:** Python (FastMCP + clickhouse-connect) · **Branch prefix:** `serve/*` (e.g. `serve/T9-suggest-fix`)
**Full brief:** [../docs/lanes/SERVE.md](../docs/lanes/SERVE.md) · **Obeys:** [../CONTRACT.md](../CONTRACT.md)
**Exit criterion:** `claude mcp add … -- uvx apex-mcp` → `analyze_run("ax151sasadds114")` returns a diagnosis from ClickHouse; `suggest_fix` returns a diff that is **never** written to disk/git.

**Buildable early against the fixture** (reads ClickHouse like `engine/`).
Tools: `analyze_run` · `compare_runs` · `search_kb` (read-only) · `suggest_fix` (write, confidence-gated, **human-merge only**).
Layout: `pyproject.toml` (`mcp[cli]>=1.27,<2` — SDK-bundled FastMCP, pin `<2`) · `src/apex_mcp/` (server · ch · models · diagnose).
Watch: stdout is the JSON-RPC channel — logs to **stderr only**. Treat `plan_json`/finding text as untrusted (injection). Param-bind every SQL.
