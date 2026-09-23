# L4 · Correlate — proposal, not a plan

> **Status: PROPOSAL.** No Task-Specs were written for L4. Two of its three features
> are blocked on emission the `jar` lane does not do yet, and specifying them now would
> produce units that are blocked on arrival.
> **Leg:** L4 of [`SERVE-LEGS.md`](SERVE-LEGS.md) · **Written:** 2026-08-20

L4 is the north star — *"which line of my code did this?"* — and the thinnest part of the
lane. This file says exactly what is missing, what it would cost, and what is already
buildable, so the next person does not rediscover it.

## The finding that changes the shape of this leg

**F4.3 is not blocked.** Contract **v0.4** added [`apex.job_conf`](../../contract/job_conf.ddl.sql):

```sql
conf Map(String, String)   -- allowlisted spark.* key -> RESOLVED value (SQL defaults included)
```

The allowlist includes `spark.sql.shuffle.partitions`. serve already narrates what AQE did
at runtime, in `diagnose._apply_ground_truth`. It has never read the configuration AQE
overrode — `grep -c job_conf serve/src/apex_mcp/ch.py` returns **0**.

So *"AQE coalesced your shuffle partitions at runtime; `spark.sql.shuffle.partitions` is
set to 2000 and this data needs far fewer"* is buildable in serve **today**, with no
contract change and no other lane's help. It is a read layer, a model and one narration
function — roughly the size of L2's read layer.

**Recommendation: promote F4.3 out of L4 and ship it as its own small leg.** It is the
most actionable sentence Apex can currently say, and it is being held hostage by two
features that genuinely are blocked.

## What is actually blocked, and by what

### F4.2 — per-`stage_id` plan-transition linkage

`apex.plan_transitions` is keyed `(job_id, execution_id)`. This proposal predates
the v0.6 producer change: an `apex.stage` payload may now include optional
`execution_id`, which ingestion retains in `spark_events.attributes`. That is
not yet a public execution-to-stage map: a read-side consumer and runtime proof
are still required.

The corresponding wording in `CONTRACT.md` still describes the older
`onJobStart` route. Because the contract is ratified authority, reconcile that
wording only through a contract decision; this proposal does not amend it.

**Remaining work:** define and test the read-side boundary. Shape of the work:

| Step | Lane | Size |
|---|---|---|
| Read `spark_events.attributes['execution_id']` with explicit missing/conflict states | `engine` | small |
| Prove the linkage with Spark SQL and a control workload | `jar` + `engine` | medium |
| Surface only proven mappings on read | `serve` | small |

This is the cheaper of the two blocked features and unlocks *"AQE split stage 4"* instead
of *"AQE split something in this execution"* — which is the distinction commit `70f5714`
was made to protect. Worth doing.

### F4.1 — stage → source line or notebook cell

This is the actual thesis, and the largest piece. **Nothing emits it.**
`grep -icE 'call_site|source_line|notebook|stack' contract/spark_events.ddl.sql` → **0**,
and the `jar` lane captures no call site.

Spark does hold it: `SparkListenerStageSubmitted` carries `StageInfo.details` (a stack
trace) and RDD/SQL operations carry a `callSite`. Getting from there to a useful answer
needs decisions nobody has taken:

- **What is a call site in a notebook?** Databricks cells are synthetic files; a line
  number without a cell identity is not actionable.
- **Redaction.** A stack trace is source paths and possibly usernames. The `collect` lane
  already scrubs `file_path` — a call site is the same class of data and needs the same
  treatment, or L4 becomes a PII leak.
- **Stability.** A call site is a physical location. It moves when the file is edited,
  which makes it a poor join key across runs — the same problem `plan_fingerprint` was
  introduced to solve for plans.

**This deserves an ADR before any spec.** The repo already has
`docs/architecture/ADR-001` and `ADR-002`; this is the same class of decision.

## Suggested sequencing

| Order | Work | Blocked on |
|---|---|---|
| 1 | **F4.3 as its own leg** — read `job_conf`, narrate AQE-vs-config | nothing |
| 2 | **F4.2** — consume v0.6 `execution_id`, prove the mapping, then surface it | read-side implementation + runtime evidence |
| 3 | **ADR for call-site correlation** — identity, redaction, stability | a decision, not code |
| 4 | **F4.1** — implement whatever the ADR settles | the ADR |

## Why no specs

A Task-Spec is a contract whose evals must be able to discriminate real work from a stub.
For F4.1 and F4.2 the evals would assert against columns that do not exist, so every unit
would fail for the wrong reason — the eval being unsatisfiable rather than the work being
undone. `taskspec gate` would still pass them as "delegate-safe", which is exactly how a
blocked backlog gets mistaken for a ready one.

F4.3 is a different case: it is specifiable today, and should be, as soon as someone
confirms it belongs on its own rather than waiting for the rest of L4.
