# engine/ — ⑤ reason

**Role:** the analysis brain. Five **deterministic SQL watchers** + an **AQE ground-truth watcher** (Tier 1, no LLM) and a **gated** CrewAI correlation/Judger (Tier 2) → `apex.findings`.
**Language:** Python (CrewAI + clickhouse-connect) · **Full brief:** [../docs/lanes/ENGINE.md](../docs/lanes/ENGINE.md) · **Obeys:** [../CONTRACT.md](../CONTRACT.md)

**Exit criterion (met):** `analyze(job_id)` runs the watchers, escalates only `confidence_score < 0.6 AND severity >= critical` through the crew, and inserts validated `Finding` rows. A clean job → **0 rows + 0 LLM calls**.

```bash
cd engine
uv run --extra dev --extra clickhouse pytest            # unit + integration (CH auto-skips if down)
uv run --extra crew --extra dev pytest                  # + the mocked-LLM crew tests
uv run --extra clickhouse python -m apex_engine <job_id> [--dry-run] [--no-crew]
```

## The two tiers

**Tier 1 — deterministic, $0.** `watchers/` holds plain Python functions over parameterized ClickHouse SQL. They are *not* agents, *not* `@tool`-wrapped, and never call an LLM. The per-stage `argMax(col, ts)` reduction comes from [`../infra/sql/005_skew.sql`](../infra/sql/005_skew.sql), minus its 6-hour window, so `analyze(job_id)` is time-independent.

| watcher | fires on |
|---|---|
| `skew` | the closed form (below), ≥4 tasks, ≥1 MiB/task |
| `shuffle` | shuffle ≥ 1 GiB; critical once it spills |
| `memory` | OOM failure · spill ≥ 64 MiB · GC ≥ 10% of executor runtime |
| `cost` | shuffle/input ≥ 50× · read ≫ emitted |
| `code` | `CartesianProduct` / `BroadcastNestedLoopJoin` · source re-scanned ≥ 256 MiB |
| `aqe` | **ground truth** from `apex.plan_transitions` (bonus) |

## Skew: physics, not a threshold (CONTRACT.md rules 1–3)

`005_skew.sql`'s `> 5×` flag is **gone**. It was wrong in both directions and it produced Apex's headline false positive — stage 4 of `app-20260724160310-0000`, shipped as a CRITICAL `SKEW_ON_JOIN` when that stage has no Join node, reads 0 shuffle bytes and moves 278 bytes/task. A skew claim now has to clear four independent tests:

1. **volume** (`bytes_per_task ≥ 1 MiB`, same constant as `verify/`) — under it, a p99/p50 ratio measures JVM warm-up, not data.
2. **the closed form** (`physics.py`): `tail-bound ⟺ p99/p50 > (n_tasks−1)/(slots−1)`. Volume cancels out; the bar is task count over cluster width. 21.62× on 2 slots needs > 49× and is **work-bound** (a perfect fix returns 0.0 ms); 20.70× on 100 tasks / 8 slots beats 14.14 and is real.
3. **plan evidence** (`plans.py`) — `SKEW_ON_JOIN` requires a Join node **and** `shuffle_read_bytes > 0` (join skew lands on the shuffle READ side). A tail without both is `TASK_SKEW`, whose fix never mentions `skewJoin.*`, because that flag only applies to a join.
4. **a measured floor** (`noise.py`) — the predicted win is held against the CV of this shape's own repeated runs *at the same config and scale*. Below it, the number is **withheld** and the finding drops to INFO: noise proves a delta unresolvable, never zero.

`slots` is an **observation**, never a guess: `spark.executor.instances × spark.executor.cores` from `apex.job_conf` (contract v0.4), else `analyze(..., slots=)` / `$APEX_CLUSTER_SLOTS`, else **UNKNOWN** — which caps confidence below the gate and reports the break-even width instead. `spark.sql.shuffle.partitions` is a partition count and is never read as a width. On a standalone cluster the resource keys are usually absent (**0 of 51** `job_conf` rows here carry `instances`), so UNKNOWN is the normal case, not an edge case.

Two consequences worth knowing:

- Where the closed form cannot discriminate — width unknown, or `slots ≥ n_tasks` making the bar ≤ 1 so any jitter passes — the claim rests on the size of the win, so it needs the measured floor, or failing that must show the tail **dominates** the stage (> 50% of its wall time). Nothing below that is asserted without a reference measurement.
- Where it can, the tail-bound verdict is a deduction and stands on a single run; only the predicted *number* is caveated. So a first-ever run still reports its skew.

**NO-OP check.** Before recommending a config change, the fix text reads the observed run's `job_conf`. `skewJoin.enabled` is already `true` in **51 of 51** rows in this store — recommending it there was the original false positive, so engine now says so instead. `verify/` owns the full gate; engine's job is not to emit the recommendation in the first place. Rule 3 rides along: a fix that history cannot attribute (< 2 distinct configs) says so in its own text.

**Tier 2 — CrewAI, gated.** `crew/` runs correlation (Sonnet) → adversarial Judger (Opus), `Process.sequential` with `context=[correlate_task]` and `output_pydantic=Finding`. The Judger's verdict is **merged onto** the Tier-1 finding, never substituted for it: identity and measured evidence stay as measured, so the model can recalibrate or reject a finding but cannot invent one. Models are `anthropic/`-prefixed (the prefix is mandatory); a crew failure keeps the finding at its Tier-1 confidence rather than losing it.

## The AQE signal (why this beats DataFlint)

Competitors aggregate `TaskEnd` *symptoms*. `aqe.py` reads Spark's own runtime *decisions* — and distinguishes them, because they do not mean the same thing:

- `skew_split` → **ground-truth skew.** It corroborates the p99/p50 heuristic, upgrading an ambiguous candidate so it emits **free instead of costing an LLM call**. It cannot, however, supply a cluster width: a corroborated finding whose width is unknown stops at MEDIUM and keeps its severity, because a `skew_split` proves the skew exists, not what fixing it is worth.
- `coalesce` → **not skew** — over-sized `spark.sql.shuffle.partitions`, reported as a partition-sizing finding. (Contract v0.2 makes this interpretation authoritative.)
- `join_switch` → a stale-statistics signal.

Only `confidence = HIGH` transitions count as ground truth; `BEST_EFFORT` is corroboration, not proof. These findings carry `stage_id = -1`, the job-level sentinel, because v0.2 keys transitions by `(job_id, execution_id)` and has no execution→stage map yet.

## Notes

- **Both confidence forms are persisted** (contract v0.2): `confidence_score` (raw 0–1, drives the gate) and `confidence` (`LOW`/`MEDIUM`/`HIGH`, drives display). Either may be supplied; the other is derived, so a stored row can never contradict itself. The `LOW` boundary *is* the gate threshold.
- **Re-analysis converges.** `apex.findings` is a plain MergeTree with no dedup, so `analyze()` inserts only findings the job does not already have.
- `plan_json` is a redacted Catalyst **tree-string, not JSON**. It is matched as opaque data and never echoed into `evidence` or into a prompt.
- **Only one Tier-1 path can currently escalate**: a critical GC ratio computed against the `task_count × p50` *proxy* denominator (`executor_run_time_ms` is not a contract column). Every other rule is confident when severe, or not severe when unsure — so no job in the store today reaches the crew. That is the gate being tight, not broken. Skew never escalates any more either: what used to make it ambiguous (the 5–10× band) is now settled by the closed form, and where it *is* unsettled the missing input is a cluster width, which no model can supply.
- **Optional reads degrade loudly.** `apex.job_conf` and the shape-history read are best-effort (a deployment may not have applied v0.4), but a failure is recorded in `analyze()["store_warnings"]`. Silent degradation once cost every finding its noise floor with no symptom.
- `TASK_SKEW` is an engine-emitted value on the contract's open `type String` column — additive, no DDL change. Consumers that key on `SKEW_ON_JOIN` simply do not match it, which is the intent: it is not a join finding.

Layout: `pyproject.toml` · `src/apex_engine/` (`config` · `schema` · `physics` · `noise` · `jobconf` · `plans` · `context` · `clickhouse` · `watchers/` · `gate` · `crew/` · `validation` · `pipeline` · `cli`) · `tests/`.
