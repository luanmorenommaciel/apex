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

**Tier 1 — deterministic, $0.** `watchers/` holds plain Python functions over parameterized ClickHouse SQL. They are *not* agents, *not* `@tool`-wrapped, and never call an LLM. `skew.py` is [`../infra/sql/005_skew.sql`](../infra/sql/005_skew.sql) lifted — the same `argMax(col, ts)`-per-stage reduction, the same `nullIf(p50, 0)` guard, the same `> 5×` flag — minus its 6-hour window, so `analyze(job_id)` is time-independent.

| watcher | fires on |
|---|---|
| `skew` | `p99/p50 > 5×` (`> 10×` critical), ≥4 tasks |
| `shuffle` | shuffle ≥ 1 GiB; critical once it spills |
| `memory` | OOM failure · spill ≥ 64 MiB · GC ≥ 10% of executor runtime |
| `cost` | shuffle/input ≥ 50× · read ≫ emitted |
| `code` | `CartesianProduct` / `BroadcastNestedLoopJoin` · source re-scanned ≥ 256 MiB |
| `aqe` | **ground truth** from `apex.plan_transitions` (bonus) |

**Tier 2 — CrewAI, gated.** `crew/` runs correlation (Sonnet) → adversarial Judger (Opus), `Process.sequential` with `context=[correlate_task]` and `output_pydantic=Finding`. The Judger's verdict is **merged onto** the Tier-1 finding, never substituted for it: identity and measured evidence stay as measured, so the model can recalibrate or reject a finding but cannot invent one. Models are `anthropic/`-prefixed (the prefix is mandatory); a crew failure keeps the finding at its Tier-1 confidence rather than losing it.

## The AQE signal (why this beats DataFlint)

Competitors aggregate `TaskEnd` *symptoms*. `aqe.py` reads Spark's own runtime *decisions* — and distinguishes them, because they do not mean the same thing:

- `skew_split` → **ground-truth skew.** It corroborates the p99/p50 heuristic, upgrading an ambiguous 5–10× candidate to HIGH so it emits **free instead of costing an LLM call**.
- `coalesce` → **not skew** — over-sized `spark.sql.shuffle.partitions`, reported as a partition-sizing finding. (Contract v0.2 makes this interpretation authoritative.)
- `join_switch` → a stale-statistics signal.

Only `confidence = HIGH` transitions count as ground truth; `BEST_EFFORT` is corroboration, not proof. These findings carry `stage_id = -1`, the job-level sentinel, because v0.2 keys transitions by `(job_id, execution_id)` and has no execution→stage map yet.

## Notes

- **Both confidence forms are persisted** (contract v0.2): `confidence_score` (raw 0–1, drives the gate) and `confidence` (`LOW`/`MEDIUM`/`HIGH`, drives display). Either may be supplied; the other is derived, so a stored row can never contradict itself. The `LOW` boundary *is* the gate threshold.
- **Re-analysis converges.** `apex.findings` is a plain MergeTree with no dedup, so `analyze()` inserts only findings the job does not already have.
- `plan_json` is a redacted Catalyst **tree-string, not JSON**. It is matched as opaque data and never echoed into `evidence` or into a prompt.
- **Only one Tier-1 path can currently escalate**: a critical GC ratio computed against the `task_count × p50` *proxy* denominator (`executor_run_time_ms` is not a contract column). Every other rule is confident when severe, or not severe when unsure — so no job in the store today reaches the crew. That is the gate being tight, not broken.

Layout: `pyproject.toml` · `src/apex_engine/` (`config` · `schema` · `clickhouse` · `watchers/` · `gate` · `crew/` · `validation` · `pipeline` · `cli`) · `tests/`.
