# End-to-end verification — the three entry points, and what has actually been observed

Apex has three end-to-end scripts. They are **layers, not alternatives** — each proves
something the others do not, and the naming does not make that obvious. This page is the map.

```
        ┌─────────────────────────────────────────────────────────────┐
        │  dev/scripts/e2e_canonical.{sh,ps1}                         │
        │  GENERATE — 4 pathologies through plugin → OTLP → collect    │
        │  → infra. Produces real telemetry at volume.                 │
        └────────────────────────────┬────────────────────────────────┘
                                     │  emits  APEX_SESSION job_id=…
                                     ▼
        ┌─────────────────────────────────────────────────────────────┐
        │  scripts/e2e_six_lanes.py     ← THE CANONICAL GATE           │
        │  VERIFY — one already-submitted job across all six lanes,    │
        │  including engine's findings and serve's MCP response.       │
        │  make verify-e2e JOB=<app-id>                                │
        └─────────────────────────────────────────────────────────────┘

        ┌─────────────────────────────────────────────────────────────┐
        │  tests/e2e/run.sh                                            │
        │  PLUMBING — brings up infra, runs ONE pathology, asserts     │
        │  rows land. Covers dev → jar → collect → infra only.         │
        │  Does NOT touch engine or serve.                             │
        └─────────────────────────────────────────────────────────────┘
```

| Script | Scope | Starts infrastructure? | Use it when |
|---|---|---|---|
| `scripts/e2e_six_lanes.py` | **all six lanes** | no — validates what already exists | **This is the gate.** Proving the system agrees with itself on one job. |
| `dev/scripts/e2e_canonical.{sh,ps1}` | dev → jar → collect → infra, ×4 pathologies | keeps collect/infra running | Generating the telemetry the gate will then check. |
| `tests/e2e/run.sh` | dev → jar → collect → infra, ×1 pathology | yes, including network glue | Smoke-testing the plumbing from cold, e.g. after a compose change. |

**The normal sequence is generate → verify:** run `e2e_canonical`, take the `job_id` it prints,
then run the gate against it.

For an opt-in, pre-submit custody chain for a particular E2E run, see
[Pre-submit provenance](PRE_SUBMIT_PROVENANCE.md).

## What the canonical gate asserts

`scripts/e2e_six_lanes.py` validates one already-submitted Spark application. It does **not**
start Docker, delete telemetry, invoke an LLM, or print credentials. It fails when:

- no telemetry exists for the `job_id`
- more than one `app_id` is present
- the engine path is not deterministic (`mode != deterministic` or `llm_calls != 0`)
- the evidence validator rejected any finding
- persisted findings diverge from a fresh analysis
- the MCP `analyze_run` tool is not read-only, or its findings disagree with engine's

Repeat runs are **idempotent**: existing findings must carry the same signature and are not
duplicated.

## Two operational traps

**1. Cluster-width drift produces a false `persisted_finding_mismatch`.**
Finding severity depends on cluster width, and width comes from `apex.job_conf`,
`$APEX_CLUSTER_SLOTS`, or is UNKNOWN. The same stage grades `warning` at unknown width and
`critical` at `slots=8`. So if findings were persisted under one width and the gate later runs
under another, it fails — from **environment drift, not a code bug**.

> Run the gate against a `job_id` with **no pre-existing `apex.findings` rows**, or hold
> `$APEX_CLUSTER_SLOTS` constant across everything that persists for that job.

`make verify-e2e` prints this warning inline for exactly this reason.

**2. The contract fixture is older than the table TTL.**
`spark_events` carries a 90-day TTL on the event `ts`, and `contract/sample_event.json` is dated
2024-06 — so a raw fixture replay TTL-expires *on insert*. The sample scripts default `ts` to
now. Production events are near-real-time, so this is a test-only concern.

## Status — what has actually been observed live

**PASSED against current code: 2026-07-29, `app-20260729180235-0044`, exit 0.**

All six lanes green on a freshly-submitted real Spark job. Committed evidence:
[`evidence/six-lane-gate-app-20260729180235-0044.json`](evidence/six-lane-gate-app-20260729180235-0044.json)
· full narrative in [`CANONICAL_GATE.md`](CANONICAL_GATE.md).

| Lane | Observed |
|---|---|
| dev | `submitted_job_observed: true` — 10,000,000 joined rows |
| jar | 20 stage events · 20 plan fingerprints |
| collect | 20 OTLP stage rows |
| infra | 20 ClickHouse stage rows |
| engine | `deterministic` · **`llm_calls: 0`** · 2 findings · 0 rejections · idempotent |
| serve | `analyze_run` · **`read_only: true`** · agrees with engine |

Transport arithmetic balances exactly: **+22 raw spans = 20 `apex.stage` + 1
`apex.plan_transition` + 1 `apex.job_conf`**, each reshaped into its contract table by a
Materialized View. Nothing lost, nothing invented.

`make verify-ddl` was green immediately before the run — all 7 contract tables matching their DDL
sources exactly.

**Two non-blocking findings** came out of the run (a stage-blind AQE promotion in serve's advisory
`symptoms[]`, and a volume floor that excluded the genuinely-skewed stage by a 5% margin). Neither
touches `findings[]` or the gate's assertions. Both are written up in
[`CANONICAL_GATE.md`](CANONICAL_GATE.md#findings-from-this-run--two-open-neither-blocking-the-gate).

The earlier 2026-07-24 run is **superseded** — it predated the telemetry-loss fix (so it was
measured on partial data), engine's threshold rewrite, serve's symptom/verdict split, contract
v0.4, and the `memory` and `verify` lanes.
