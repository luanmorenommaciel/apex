# C10 - Augusto branch E2E readiness (2026-07-24)

## Scope

This is the current readiness record for `base-project-e2e-augusto`. It does
not modify, supersede, or claim approval for `feat/base-project-e2e`.

## Verified locally

| Surface | Command scope | Result |
|---|---|---|
| Canonical six-lane gate | `tests/test_e2e_six_lanes.py` | `4 passed` |
| SERVE | `serve/tests` | `87 passed` |
| ENGINE deterministic and Crew gate | `engine/tests`, excluding ClickHouse integration | `75 passed` |
| DEV canonical assertions | `dev/tests/test_canonical_e2e_assert.py` | `7 passed` |

The post-consolidation E2E correction is commit `52a36da`. It normalizes
finding type/severity casing across ENGINE, persisted ClickHouse rows, and
MCP JSON, so a transport representation difference cannot produce a false
cross-lane mismatch.

## Existing live evidence

[`../e2e/CANONICAL_GATE.md`](../e2e/CANONICAL_GATE.md) records the four real
Spark 4.1.2 pathology runs from 2026-07-24: `skew_join`, `spill`,
`bad_shuffle`, and `driver_oom`. The six-lane gate was observed for the skew
run with deterministic ENGINE and read-only SERVE.

## Remaining operational validation

1. Restore a responsive Docker daemon.
2. Run `dev/scripts/e2e_canonical.ps1 -StartDev` with the local ClickHouse
   password supplied by the operator.
3. Run `scripts/e2e_six_lanes.py` for each emitted `job_id`.
4. Re-run the real MCP client for `analyze_run`, `compare_runs`, `search_kb`,
   and `suggest_fix`; confirm the proposal remains non-mutating.
5. Run the external Crew/Judge smoke only with an operator-provided Anthropic
   key; never persist a key, token, or environment dump.

The Docker daemon was not responsive during the latest local attempt. This is
an environment blocker for a fresh run, not a claim that the code path failed.

## Commander decisions still required

- Approve or adjust the `LOW + critical|blocker` escalation policy.
- Confirm that `suggest_fix` remains a human-approved proposal only.
- Choose an approved integration path; this branch must not merge itself into
  the Luan-owned base.
