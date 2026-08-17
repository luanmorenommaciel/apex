# L1 · Connect — task index

> **Leg:** L1 of [`SERVE-LEGS.md`](SERVE-LEGS.md) · **Lane:** [`SERVE.md`](SERVE.md) · **Contract:** [`../../CONTRACT.md`](../../CONTRACT.md)
> **Baseline:** branch `feat/base-project-e2e` · head `093c677` · `uv run --extra dev pytest` → **87 passed**
>
> This file is the **index**. Each task is a six-zone task-spec under [`../../tasks/`](../../tasks/) —
> a contract, not a mention. Format and seal rules: [`../../tasks/README.md`](../../tasks/README.md).

## Exit criterion for L1

A user who has never run Apex types **one command**, restarts the client, calls
**`apex_status()`**, and gets a truthful answer to *"is this working, and if not, what do I
change?"* — **including when ClickHouse is down**.

## Ripple warning — "exactly four tools" is asserted in 10 places

L1 adds a **fifth** tool. This is a deliberate breach of a frozen assertion; every site must
move or the suite and the gates go red.

| Site | What it says |
|---|---|
| `serve/tests/test_server_tools.py:1` | docstring — "exactly four tools" |
| `serve/tests/test_server_tools.py:38` | `assert [t.name for t in _tools(server)] == [...4 names...]` |
| `serve/src/apex_mcp/server.py:7` | module docstring — "Four tools:" |
| `serve/tools/mcp_stdio_gate.py:5` | "it lists exactly the four contracted tools" |
| `serve/README.md:5,11,38` | prose, table heading, install comment |
| `serve/VALIDATION.md:9,67` | scope table, stdio-gate bullet |
| `docs/lanes/SERVE.md:9` | mission statement |
| `docs/lanes/SERVE.md:73` | T11 accept — "lists exactly 4 tools" |

`T1.07` (test) and `T1.21` (docs) exist solely to close this. They are **not** folded into
`T1.06`, so the commit that changes the tool surface is legible in `git log`.

## Task index

| ID | Spec | Effort | Depends on |
|---|---|---|---|
| **A — `apex_status()`** | | | |
| T1.01 | [`serverstatus-model`](../../tasks/T-20260812-serverstatus-model.md) | S | — |
| T1.02 | [`store-health-query`](../../tasks/T-20260812-store-health-query.md) | S | — |
| T1.03 | [`table-columns-probe`](../../tasks/T-20260812-table-columns-probe.md) | S | — |
| T1.04 | [`status-assembler`](../../tasks/T-20260812-status-assembler.md) | M | T1.01 |
| T1.05 | [`status-degraded-path`](../../tasks/T-20260812-status-degraded-path.md) | S | T1.04 |
| T1.06 | [`register-apex-status`](../../tasks/T-20260812-register-apex-status.md) | S | T1.02–T1.05 |
| T1.07 | [`five-tools-assertion`](../../tasks/T-20260812-five-tools-assertion.md) | S | T1.06 |
| T1.08 | [`status-store-down-e2e`](../../tasks/T-20260812-status-store-down-e2e.md) | S | T1.06 |
| **B — actionable configuration errors** | | | |
| T1.09 | [`resolve-settings-extract`](../../tasks/T-20260812-resolve-settings-extract.md) | S | — |
| T1.10 | [`name-endpoint-in-error`](../../tasks/T-20260812-name-endpoint-in-error.md) | S | T1.09 |
| T1.11 | [`startup-stderr-banner`](../../tasks/T-20260812-startup-stderr-banner.md) | S | T1.09 |
| T1.12 | [`surface-defaulted-vars`](../../tasks/T-20260812-surface-defaulted-vars.md) | S | T1.01, T1.09 |
| **C — PyPI packaging** | | | |
| T1.13 | [`pypi-metadata`](../../tasks/T-20260812-pypi-metadata.md) | S | — |
| T1.14 | [`wheel-content-check`](../../tasks/T-20260812-wheel-content-check.md) | S | T1.13 |
| T1.15 | 🔒 [`testpypi-rehearsal`](../../tasks/T-20260812-testpypi-rehearsal.md) | S | T1.14 |
| T1.16 | 🔒 [`pypi-publish`](../../tasks/T-20260812-pypi-publish.md) | S | T1.15, T1.17 |
| **D — client config parity** | | | |
| T1.17 | [`root-mcp-json`](../../tasks/T-20260812-root-mcp-json.md) | S | — |
| T1.18 | [`cursor-codex-config`](../../tasks/T-20260812-cursor-codex-config.md) | S | — |
| **E — gates and docs** | | | |
| T1.19 | [`gate-status-assert`](../../tasks/T-20260812-gate-status-assert.md) | M | T1.06, T1.12 |
| T1.20 | [`stdio-gate-five-tools`](../../tasks/T-20260812-stdio-gate-five-tools.md) | S | T1.06 |
| T1.21 | [`four-to-five-doc-ripple`](../../tasks/T-20260812-four-to-five-doc-ripple.md) | S | T1.06, T1.19, T1.20 |
| T1.22 | [`graphify-rebuild`](../../tasks/T-20260812-graphify-rebuild.md) | S | T1.21 |

**Startable now, in parallel:** T1.01, T1.02, T1.03, T1.09, T1.13, T1.17, T1.18 — seven specs
with no unmet dependency.

**Critical path:** T1.01 → T1.04 → T1.05 → T1.06 → T1.19 → T1.21 → T1.22.

## Open questions that block, and who owns them

Zone 5 of each spec carries its own questions. Three escape the spec that raised them:

| Question | Raised in | Blocks | Owner |
|---|---|---|---|
| Is the distribution name `apex-mcp` free on PyPI? | T1.13 | T1.16 — a claimed name is permanent | **unassigned** |
| Which license, and who owns the PyPI project? | T1.13, T1.16 | T1.16 | **unassigned** |
| Do Cursor and Codex support `${VAR:-default}`? | T1.18 | correctness of the shared `.mcp.json` (T1.17) | **unassigned** |

The first two are the only things in L1 an agent cannot finish alone.

## Definition of done

```bash
cd serve
uv run --extra dev pytest                  # green; count recorded in VALIDATION.md
uv run python tools/read_only_gate.py      # status: passed, includes the status_tool block
uv run python tools/mcp_stdio_gate.py      # five tools, annotations correct
uv build && uvx twine check dist/*         # PASSED
cd .. && python3 tasks/seal.py check tasks/*.md   # no spec has drifted from its seal
```

Plus two checks no automated gate can make:

1. **Stop ClickHouse and call `apex_status()`.** It must answer, with `connected=false` and a
   remediation. This is L1's actual promise and every gate above runs with the database up.
2. **`grep -rniE 'four tools' serve/ docs/`** returns nothing.
