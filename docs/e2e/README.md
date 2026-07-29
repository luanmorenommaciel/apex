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

**Recorded run: 2026-07-24.** All four pathologies passed and the six-lane gate passed against
`app-20260724014653-0000` — 17 events and fingerprints, 3 deterministic findings, **0 LLM
calls**, `analyze_run` confirmed read-only. Full detail in
[`CANONICAL_GATE.md`](CANONICAL_GATE.md).

**That evidence is stale for v0.1, and deliberately labelled as such.** It predates:

- **the telemetry-loss fix** — a container-alias collision was silently dropping 50–70% of
  applications, so that run was measured on **partial data**
- **engine's threshold rewrite** — 127 findings → 65; the finding counts in the recorded run are
  from the superseded fixed-threshold logic
- **serve's symptom/verdict split** — the recorded run could render a symptom contradicting its
  own findings
- **the `memory` and `verify` lanes**, which did not exist
- **contract v0.4** and cross-lane rules 1–5

The gate itself is unchanged in contract and has 4 unit tests covering its invariants
(`make test-root`), and every hop it exercises is independently green. But **a re-run against
the current code is required before v0.1 is signed off**, and the numbers in `CANONICAL_GATE.md`
should be read as "the gate mechanism works," not as "these are Apex's current findings."

Re-running it is the last outstanding item for v0.1:

```bash
cd infra && make apply-ddl && docker compose up -d --wait
cd ../dev  && ./scripts/e2e_canonical.sh          # note the emitted job_id
cd ..      && make verify-e2e JOB=<that-job-id>
```

`CANONICAL_GATE.md` is currently written in Portuguese and uses PowerShell examples; it will be
replaced by the output of that re-run.
