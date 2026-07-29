# Canonical E2E gate — recorded run

`scripts/e2e_six_lanes.py` validates one **already-submitted** Spark application across all six
lanes: `DEV → JAR → COLLECT → INFRA → ENGINE → SERVE`.

It fails when there is no telemetry, more than one `app_id`, a non-deterministic ENGINE path, a
validator rejection, a findings-persistence divergence, or a SERVE response that is not read-only
or disagrees with ENGINE. Repeat runs are **idempotent**: existing findings must carry the same
signature and are never duplicated.

Entry points and their layering: [`README.md`](README.md).

---

## Recorded run — 2026-07-29 · `app-20260729180235-0044`

**Result: PASSED, exit 0.** Machine-readable evidence:
[`evidence/six-lane-gate-app-20260729180235-0044.json`](evidence/six-lane-gate-app-20260729180235-0044.json)

Environment: Spark 4.1.2 standalone (1 master, 1 worker), `apex.ApexPlugin`, OTLP Collector
0.156.0, ClickHouse 24.8, MCP over stdio. Job: `make c4-aqe-skewsplit` — `skew_join` with AQE
forced to split a skewed partition.

### Lane results

| Lane | Observed |
|---|---|
| **dev** | `submitted_job_observed: true` — `apex-skew_join-aqe`, 10,000,000 joined rows |
| **jar** | 20 canonical stage events · 20 plan fingerprints |
| **collect** | 20 OTLP stage rows transported |
| **infra** | 20 ClickHouse stage rows |
| **engine** | `deterministic` · **`llm_calls: 0`** · 2 accepted findings · 0 validator rejections · `already_present` (idempotent) |
| **serve** | `analyze_run` · **`read_only: true`** · 20 stages · 2 findings, matching engine |

### Transport arithmetic — nothing lost, nothing invented

Baseline captured before the run, re-counted after:

| Table | Before | After | Δ |
|---|---|---|---|
| `otel_traces` | 130 | 152 | **+22** |
| `spark_events` | 121 | 141 | +20 |
| `plan_transitions` | 3 | 4 | +1 |
| `job_conf` | 6 | 7 | +1 |
| `findings` | 0 | 2 | +2 (engine) |

The 22 raw spans decompose exactly: **20 `apex.stage` + 1 `apex.plan_transition` + 1
`apex.job_conf`**, each reshaped by its Materialized View into the matching contract table. Every
span accounted for.

### Ground truth captured

```
transition_type : skew_split          execution_id : 11
detail          : AQEShuffleRead skewed x1
before          : 0 skewed            after : 1 skewed
confidence      : HIGH
```

Spark's own runtime re-planning decision — not inferred from a p99/p50 tail.

Resolved config captured into `apex.job_conf` (8 keys), including
`spark.sql.adaptive.skewJoin.enabled: 'true'` — which is what lets the no-op gate know the
recommended fix is *already active*. Note there is **no `spark.executor.instances`**, so cluster
width is UNKNOWN for this run: the honest-unknown path, exercised for real.

### Discrimination — the point of the whole system

Five stages carried a raw p99/p50 tail. Engine reported a skew finding on **none** of them:

| Stage | ratio | bytes/task | tasks | Engine verdict |
|---|---|---|---|---|
| 6 | **10.97×** ← highest | 427 | 50 | **no finding** — below the 1 MiB/task floor; scheduler noise |
| 29 | 10.48× | 996,772 | 114 | **no finding** — 5% under the floor (see caveat) |
| 33 | 7.68× | 6,837 | 100 | **no finding** — below floor |
| 11 | 7.19× | 4,268,400 | 2 | **no finding** — 2 tasks is not a distribution |
| 4 | 5.35× | 625 | 50 | **no finding** — below floor |

A ratio-ranking tool reports stage 6 first as *"10.97× critical skew."* It moves **427 bytes per
task**. Engine's single skew finding is **job-level** (`stage_id: -1`), sourced from the AQE
transition at HIGH (0.97) confidence, and its fix text obeys the no-op gate — *"**Keep**
`skewJoin.enabled=true`, then remove the skew at the source"* — rather than recommending a flag
that is already on.

### Idempotency, verified live

```
run 1 → written_rows: 2  (inserted,       skipped_existing=0)
run 2 → written_rows: 0  (already_present, skipped_existing=2)
```

This exercises the finding-signature fix (`496e10d`): identity is no longer derived from an
`evidence` string containing a measured floor that grows as history accumulates.

### Schema truth

`make verify-ddl` green immediately before the run — all **7** contract tables match their DDL
sources exactly: `spark_events` (20 cols), `findings` (14), `plan_transitions` (9), `job_conf`
(5), `plan_memory` (18), `run_outcomes` (32), `fix_verifications` (26).

---

## Findings from this run — two open, neither blocking the gate

**1. `serve` symptom promotion is stage-blind.** `diagnose.py:268-276` promotes **every** skew
symptom to `critical` + `adjudicated=True` whenever a `skew_split` exists anywhere in the job.
But a `skew_split` is **execution-scoped**, not stage-scoped: it proves skew occurred *somewhere
in that execution*, not that a given stage is skewed. On this run the only symptom clearing the
volume floor was **stage 25 at a 1.03× ratio** — perfectly balanced — and it was promoted to
"critical skew, confirmed by Spark itself." The emitted evidence text even contradicts its own
severity, reading `critical` alongside *"unadjudicated measurement… is engine's call."*

Engine gets this right by placing its AQE finding at `stage_id: -1`. **This does not affect
`findings[]`**, which serve reads from `apex.findings` and passes through unchanged — the gate
compares those and passed. It affects the advisory `symptoms[]` surface only.

**2. The 1 MiB/task volume floor excluded the genuinely skewed stage.** Stage 29 carried 114
tasks (= 100 + 14 AQE subpartitions — it is *the stage AQE actually split*) at **996,772
bytes/task**, which is **95% of 1 MiB**. It missed the floor by 5% and was dropped. Same family as
contract rule 5's false-negative class: a byte threshold silencing a real signal. Worth deciding
whether the floor should be a hard cut or a confidence input.

Neither is a data-integrity defect and neither failed the gate.

---

## Reproduce

```bash
# 1. store
cd infra && make apply-ddl && docker compose up -d --wait && make verify-ddl

# 2. a real instrumented job (prints APEX_SESSION job_id=…)
cd ../dev && make c4-aqe-skewsplit

# 3. reason over it
cd ../engine && CLICKHOUSE_HOST=127.0.0.1 CLICKHOUSE_PASSWORD=<local-secret> \
  uv run --extra clickhouse python -m apex_engine <job_id> --no-crew

# 4. the gate
cd .. && CLICKHOUSE_HOST=127.0.0.1 CLICKHOUSE_PASSWORD=<local-secret> \
  make verify-e2e JOB=<job_id>
```

> **Operational trap.** Use a `job_id` with **no pre-existing `apex.findings` rows**, or hold
> `$APEX_CLUSTER_SLOTS` constant across everything that persists for that job. Severity is
> width-dependent, so environment drift alone produces `persisted_finding_mismatch` — a failure
> that looks like a code bug and is not. `make verify-e2e` prints this inline.

Never commit ClickHouse credentials. The gate does not start Docker, delete telemetry, call an
LLM, or print secrets.

---

## Superseded run — 2026-07-24

An earlier gate run passed against `app-20260724014653-0000` (17 events, 3 findings, 0 LLM calls)
along with all four pathologies. **Those numbers are obsolete** and are retained only as evidence
that the gate mechanism has worked across multiple environments. That run predates the
telemetry-loss fix (it was measured on partial data), engine's 127 → 65 threshold rewrite,
serve's symptom/verdict split, contract v0.4, and the `memory` and `verify` lanes. The 2026-07-29
run above supersedes it.
