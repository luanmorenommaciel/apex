# L1 · Connect — task index

> **Leg:** L1 of [`SERVE-LEGS.md`](SERVE-LEGS.md) · **Lane:** [`SERVE.md`](SERVE.md) · **Contract:** [`../../CONTRACT.md`](../../CONTRACT.md)
> **Branch:** `serve/l1-connect` · **Plan:** [`../../tasks/.plans/l1-connect.yaml`](../../tasks/.plans/l1-connect.yaml)
>
> Each unit is a signed Task-Spec v3. This file is the **authority for ordering** —
> see the warning under *Dispatch order* before consuming `_state.yaml`.

## Exit criterion

A user who has never run Apex types **one command**, restarts the client, calls
**`apex_status()`**, and gets a truthful answer to *"is this working, and if not, what do I
change?"* — **including when ClickHouse is down**.

## Progress — 2 of 23 accepted

| | Unit | Effort | Depends on |
|---|---|---|---|
| ✅ | [`serverstatus-model`](../../tasks/done/T-20260817-serverstatus-model.md) | S | — |
| ✅ | [`store-health-query`](../../tasks/done/T-20260817-store-health-query.md) | S | — |
| ▶︎ | [`cursor-codex-config`](../../tasks/T-20260817-cursor-codex-config.md) | XS | — |
|  | [`drop-from-path`](../../tasks/T-20260817-drop-from-path.md) | M | pypi-publish, root-mcp-json, four-to-five-doc-ripple |
|  | [`five-tools-assertion`](../../tasks/T-20260817-five-tools-assertion.md) | XS | register-apex-status |
|  | [`four-to-five-doc-ripple`](../../tasks/T-20260817-four-to-five-doc-ripple.md) | M | register-apex-status, gate-status-assert, stdio-gate-five-tools, cursor-codex-config |
|  | [`gate-status-assert`](../../tasks/T-20260817-gate-status-assert.md) | S | register-apex-status, surface-defaulted-vars |
|  | [`graphify-rebuild`](../../tasks/T-20260817-graphify-rebuild.md) | XS | four-to-five-doc-ripple |
|  | [`name-endpoint-in-error`](../../tasks/T-20260817-name-endpoint-in-error.md) | S | resolve-settings-extract |
| ▶︎ | [`pypi-metadata`](../../tasks/T-20260817-pypi-metadata.md) | XS | — |
|  | [`pypi-publish`](../../tasks/T-20260817-pypi-publish.md) | XS | testpypi-rehearsal |
|  | [`register-apex-status`](../../tasks/T-20260817-register-apex-status.md) | XS | status-assembler, status-degraded-path, store-health-query, table-columns-probe |
|  | [`resolve-settings-extract`](../../tasks/T-20260817-resolve-settings-extract.md) | S | table-columns-probe |
| ▶︎ | [`root-mcp-json`](../../tasks/T-20260817-root-mcp-json.md) | S | — |
|  | [`startup-stderr-banner`](../../tasks/T-20260817-startup-stderr-banner.md) | S | resolve-settings-extract, status-store-down-e2e |
| ▶︎ | [`status-assembler`](../../tasks/T-20260817-status-assembler.md) | S | serverstatus-model |
|  | [`status-degraded-path`](../../tasks/T-20260817-status-degraded-path.md) | S | status-assembler |
|  | [`status-store-down-e2e`](../../tasks/T-20260817-status-store-down-e2e.md) | XS | register-apex-status, five-tools-assertion |
|  | [`stdio-gate-five-tools`](../../tasks/T-20260817-stdio-gate-five-tools.md) | XS | register-apex-status |
|  | [`surface-defaulted-vars`](../../tasks/T-20260817-surface-defaulted-vars.md) | M | serverstatus-model, resolve-settings-extract, status-assembler, status-degraded-path, startup-stderr-banner |
| ▶︎ | [`table-columns-probe`](../../tasks/T-20260817-table-columns-probe.md) | S | store-health-query |
|  | [`testpypi-rehearsal`](../../tasks/T-20260817-testpypi-rehearsal.md) | XS | wheel-content-check, four-to-five-doc-ripple |
|  | [`wheel-content-check`](../../tasks/T-20260817-wheel-content-check.md) | S | pypi-metadata |

`✅` accepted and transitioned to `done` · `▶︎` startable now, no unmet dependency

## Dispatch order

**`tasks/_state.yaml` `ready_queue` is not a dispatch order.** It lists every unit whose
`status` is `ready`, without consulting `depends_on` — so it currently offers all
21 units including ones whose prerequisites are unbuilt. Use the *Depends on*
column above, or the plan manifest, to choose what to run.

**Startable now:** `cursor-codex-config`, `pypi-metadata`, `root-mcp-json`, `status-assembler`, `table-columns-probe`

## Consuming a unit

```bash
cd /opt/projects/dataship/git/apex-l1
taskspec gate --stamp tasks/T-20260817-<slug>.md    # authorize; Tier 1 needs the repo signing key
# ...build...
taskspec accept --stamp tasks/T-20260817-<slug>.md  # re-runs evals, checks blast radius, verifies HMAC
taskspec transition T-20260817-<slug> done "accepted Tier 1"
```

Specs are **signed one at a time, at dispatch**, never in bulk: `gate` re-checks the evals
against current code, so a batch signature would authorize unbuilt work.

## Definition of done for L1

```bash
cd serve
uv run --extra dev pytest                  # green; count recorded in VALIDATION.md
uv run python tools/read_only_gate.py      # status: passed, includes the status_tool block
uv run python tools/mcp_stdio_gate.py      # five tools, annotations correct
uv build && uvx twine check dist/*         # PASSED
cd .. && taskspec validate tasks/T-*.md tasks/done/*.md
```

Plus two checks no automated gate can make:

1. **Stop ClickHouse and call `apex_status()`.** It must answer, with `connected=false` and a
   remediation. Every gate above runs with the database up.
2. **`grep -rniE 'four tools' serve/ docs/`** returns nothing.

## Known blockers

| Unit | Blocked on |
|---|---|
| `gate-status-assert` | a live ClickHouse; none is running |
| `testpypi-rehearsal`, `pypi-publish` | registry credentials |

## Superseded

The hand-rolled specs this leg started from are kept for provenance in
[`L1_legacy_specs/`](L1_legacy_specs/), outside `tasks/` so the backlog scanner does not
ingest them as active work. They are **not** consumable: their `seal.py` digest scheme was
replaced by `taskspec gate --stamp`, which is the only thing that may write `signed_off*`.
