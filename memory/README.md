# memory/ — ⑦ recall

**Role:** cross-job **plan memory**. Every other lane reasons about one run in
isolation; this one answers *"I have seen this plan shape N times before, and
here is the configuration that actually worked."*
**Language:** Python (stdlib + pydantic; `clickhouse-connect` only at the
boundary) · **Obeys:** [../CONTRACT.md](../CONTRACT.md) (v0.4)

**Exit criterion (met):** given a `job_id` in ClickHouse, `recall()` returns its
similar historical runs, a config recommendation and a predicted delta, each
backed by citable evidence rows — and reports **LOW** confidence when history is
thin.

```bash
cd memory
uv sync --extra clickhouse --extra dev
uv run --extra dev pytest                                    # 40 tests, no infra needed
uv run --extra clickhouse python -m apex_memory index        # build the index
uv run --extra clickhouse python -m apex_memory recall --job <job_id>
uv run --extra clickhouse python tools/recall_gate.py        # live gate
```

## Why this beats DataFlint

DataFlint enriches **one** job's logs per query and hands them to an LLM. It has
no cross-job memory because it has nowhere to keep one. Apex already computes a
literal-normalised `plan_fingerprint` and stores every run in an open,
queryable ClickHouse — the exact substrate [ZEST](https://arxiv.org/abs/2503.03826)
needs. That is architectural, not a feature gap.

## The method, and where it departs from ZEST

ZEST embeds a Spark logical plan as text, retrieves the top-k most similar
historical plans by cosine similarity, and averages their tuned configurations —
reaching 93.3% of one-execution tuning's gain with **zero executions**. The
architecture is preserved exactly. Three things are not:

**1. The encoder.** ZEST embeds raw plan text with `jina-embeddings-v3`. Apex's
`plan_json` is redacted in-JVM before egress (CONTRACT § Redaction), so every
column arrives as `none#0` and every literal as `null`. A text embedder pointed
at that spends its capacity on placeholder tokens identical across all plans.
What survives redaction — operators, multiplicity, join types, tree topology,
function names — is exactly what predicts performance, so it is encoded directly:
199+ dimensions, deterministic, $0, no model, no network, and every dimension
nameable when someone asks *why* two plans matched. `encoder_version` +
`embedding_kind` exist so a text embedding can be indexed alongside and compared.

**2. Abstention.** ZEST averages its k neighbours whether or not any resemble the
query; the paper describes no similarity threshold and no fallback. Apex gates on
similarity rather than rank — three honest neighbours beat ten where seven are
unrelated — and refuses to answer at all when the evidence will not carry it.

**3. Pooling.** ZEST averages because it has a per-query Optuna optimum for each
neighbour. Apex has observed runs, so it uses whichever method the evidence
supports: **A/B** when history contains two or more configurations with real
support (report the config that actually won, verbatim — a blend that was never
executed can sit between two good settings at a bad one), and **ZEST Algorithm 1**
when it does not (parameter-wise mean, plus majority vote for booleans, which the
paper does not cover since it tunes only numeric parameters).

## The two tiers

| Tier | Match | Strength |
|---|---|---|
| `exact` | `plan_fingerprint` equality | Same literal-normalised logical plan — the historical run did the same work |
| `structural` | cosine over the encoder vector | Weaker: indistinguishable *after redaction*, not necessarily the same query |

**Known limit, measured not theorised.** Six distinct fingerprints in the live
store encode to cosine exactly `1.0000`. Their redacted texts genuinely differ
(six MD5s, all 1011 chars) but they share operators, functions **and** edges —
redaction erased the difference at source, so no encoder reading this column can
separate them. That is why the exact tier exists, why a `1.0` structural hit
means "structurally indistinguishable" rather than "the same query", and why
`n_distinct_fingerprints` is reported alongside the run count.

## The honesty gates

The confidence scoring **is** the product. A retrieval system that always answers
launders a guess into a number someone will act on.

`predicted_delta` passes four gates, in order of how badly each would mislead:

1. **Attributability** (contract v0.4, cross-lane rule 3). Fewer than 2 distinct
   configurations in history → no observed difference is creditable to tuning.
   This gate exists because of a real case: four runs of one shape with
   byte-identical shuffle (10,852,769 B) and spill (390,465 B) still ranged
   2708–4347 ms. That **18.65%** clears any plausible noise floor. *The floor
   alone does not catch it.*
2. **Group support.** The comparison uses a config group's **median** over ≥2
   runs, never the single fastest run — `min()` over N noisy samples is a biased
   estimator that drifts lower as N grows, so a "best config" chosen that way
   looks better the more history you accumulate. Backwards.
3. **Comparability.** An improvement measured on materially less input is not an
   improvement.
4. **The noise floor**, measured rather than assumed (below).

Confidence needs the rule tier *and* the score tier to agree; the stricter wins.
`n_*` counts **distinct jobs**, never rows — one job contributing seventeen
stages is one observation.

## What the noise floor actually is

The verify lane measured **5.8% (1σ)** job-level across three byte-identical
runs. That figure does **not** transfer to the per-shape `task_time_ms` this lane
compares. Measured on the calibrated corpus (2026-07-28): 65 cells of ≥3 runs
sharing an identical plan shape, identical canonical config **and** identical
`input_bytes`, covering 308 runs →

| | 1σ CV |
|---|---|
| median | **15.9%** |
| p90 | 76.4% |
| max | 114.8% |

Two explanations ruled out: it is **not** JVM warmup (dropping each cell's first
run leaves the median at 16.2%) and **not** a small-sample artefact (15.4% for
cells ≤8 tasks vs 15.1% for >100 tasks — more tasks does not average it out). The
corpus was collected on a shared developer host, so background load is the likely
driver.

Because a distribution whose p90 is five times its median is badly described by
any single number, `recall()` measures **each shape's own** within-config
variance and uses that, falling back to 15.9% only when no group is large enough.
Every delta reports which basis it used.

## Cold start: not seeded, and why

ZEST released 19,360 TPC-H/TPC-DS executions with tuned configs. The paper calls
them public; the location in the companion repo is `s3://l6lab/sparktune/raw`.
**It is not anonymously readable** — probed 2026-07-27, `AccessDenied` on both
`aws s3 ls --no-sign-request` and plain HTTP (bucket exists, `us-east-1`).

So `seed/zest.py` is a **drop-in loader, and Apex is not seeded**.
`probe_zest_dataset()` re-runs that check on demand so the claim stays
falsifiable, and the live gate asserts zero `zest-seed` rows exist. If the bucket
opens, seeded rows land in the same six typed columns with
`outcome_source='zest-seed'`, reachable only through the structural tier (their
plans never went through Apex's hasher) and excluded from delta prediction
(different hardware, different scale — the absolute runtimes would mislead).

## Contract surface (v0.3, ratified)

Two additive tables, DDL in [`sql/`](sql/). Four deliberate deviations from the
v0.2 house pattern, each ratified:

- **`plan_memory` has no `PARTITION BY`** — it is a dimension keyed by
  fingerprint, not a time series; monthly partitioning would shatter one logical
  row and defeat the `ReplacingMergeTree` collapse.
- **`ORDER BY (plan_fingerprint, job_id)`** — fingerprint first, the inverse of
  `spark_events`; the hot path is "every run of this shape".
- **TTL 365 days vs `spark_events`' 90** — memory must outlive the events it came
  from. At day 91 the stage rows are gone; the learned shape and its outcome
  remain.
- **`Nullable` config columns, never a 0 sentinel** — "not captured" ≠ "set to
  0". Collapsing them would drag every mean toward zero.

Config comes from **`apex.job_conf`** (v0.4). Only 8 of 13 allowlisted keys reach
standalone runs — `spark.executor.*`/`spark.driver.*` appear only when explicitly
set. **Absent is treated as absent, never as a default.**

## Notes worth knowing

- **Values are canonicalised before comparison.** `skewedPartitionFactor` is
  `'5.0'` on 40 runs and `'5'` on 11 — one setting, two spellings; counting them
  as two would invent variation and unlock a suppressed delta claim. Meanwhile
  `advisoryPartitionSizeInBytes` is `'8m'` vs `'67108864b'` — a real 8× gap that
  a naive `int()` would crash on. See [`conf.py`](src/apex_memory/conf.py).
- **`MIN_PLAN_NODES = 2`.** A single-operator plan has no structure to compare.
  The store's fixture jobs contribute 52 fingerprints that all render as
  `Scan parquet`; unfiltered they became 52 perfect-similarity neighbours. The
  filter is on *information content*, not fingerprint shape — a real SHA-256 may
  legitimately begin with zeroes. Excluded plans stay in `run_outcomes`, so the
  exact tier still serves them at full confidence.
- **Edge hashing uses `zlib.crc32`, not `hash()`.** Python randomises string
  hashing per process, so an index built before a restart would not match queries
  encoded after one. A test enforces this across a real subprocess.
- **Aggregate aliases never shadow source columns.** `argMax(plan_json, ts) AS
  plan_json` makes ClickHouse resolve the `WHERE` reference to the *alias* and
  fail with `ILLEGAL_AGGREGATION`. Columns inside outer aggregates are qualified
  (`latest.task_count`) for the same reason.
- **Brute-force `cosineDistance`, no ANN index.** Verified live on 24.8.14.39:
  `vector_similarity` accepts only the 2-arg form and needs an experimental flag,
  and an ANN index would make results approximate. At this scale an exact scan is
  correct and cheaper. The exact `ALTER` is documented in
  [`sql/030_plan_memory.sql`](sql/030_plan_memory.sql) for when volume justifies it.
- **Recall is read-only.** The indexer is the only writer.
- **Untrusted text is declared.** `plan_json` and finding text are written by the
  observed Spark job, not by Apex; every response lists its `untrusted_fields`,
  matching serve/'s convention.

Layout: `pyproject.toml` · `sql/` · `src/apex_memory/` (`config` · `conf` ·
`schema` · `encoder` · `clickhouse` · `indexer` · `confidence` · `recall` ·
`seed/` · `cli`) · `tests/` · `tools/recall_gate.py`.
