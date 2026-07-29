# Changelog

All notable changes to Apex. Format loosely follows [Keep a Changelog](https://keepachangelog.com/);
versions follow [Semantic Versioning](https://semver.org/).

This file records not just *what* shipped but *what it cost to learn*, because in a
performance tool the reasoning behind a threshold is the product. Several entries below
are corrections to Apex's own earlier claims.

---

## [0.1.0] — 2026-07-29

First complete release. Eight lanes, one frozen contract, 400 tests.

### Added — the pipeline

- **`contract/`** — the frozen interface every lane obeys: telemetry event shape, ClickHouse
  DDL, `Finding` schema, `job_id` threading, and a host-port map so lanes cannot collide.
  Reached **v0.4** (`spark_events`, `plan_transitions`, `findings`, `job_conf`, `plan_memory`,
  `run_outcomes`, `fix_verifications`).
- **`dev/`** — Spark/Delta pathology lab. Reproducible `skew_join`, `spill`, `bad_shuffle`,
  and `driver_oom` jobs, plus a **balanced control** so a detector can be shown *not* to fire.
  Spark 3.5 and 4.1.2 environments.
- **`jar/`** — Scala Spark plugin. Per-stage `TaskMetrics`, a literal-normalized logical-plan
  fingerprint, AQE runtime decisions, and a resolved-config snapshot, shipped as OTLP spans
  through a bounded `BatchSpanProcessor`. Cross-builds four `(Spark, Scala)` cells:
  3.5/2.12, 3.5/2.13, 4.0/2.13, 4.1/2.13.
- **`collect/`** — config-only OpenTelemetry Collector (`otelcol-contrib` 0.156.0, no custom
  Go build). OTLP `:4318` → `memory_limiter` → PII scrub → ClickHouse, reshaped into contract
  tables by Materialized Views.
- **`infra/`** — ClickStack platform: ClickHouse + HyperDX, contract DDL, and `make apply-ddl`
  / `verify-ddl` as the schema-truth gate.
- **`engine/`** — the brain. Deterministic watchers over ClickHouse with CrewAI gated behind
  a confidence/severity threshold, so a healthy job costs **$0 and zero LLM calls**.
- **`serve/`** — read-only MCP server: `analyze_run`, `compare_runs`, `search_kb`, and a gated
  `suggest_fix`.
- **`memory/`** — cross-job plan memory. Structural plan encoder (200-dim, deterministic, $0),
  two-tier recall (exact fingerprint + cosine-structural), and four honesty gates.
- **`verify/`** — fix verification. Predicts a fix's effect from a makespan bound, replays it
  on the bench, and reports mechanism and runtime as **separate** verdicts.

### Added — tooling

- `LICENSE` / `NOTICE` — **Apache-2.0**. The README had advertised Apex as open while the repo
  was legally all-rights-reserved.
- **`make test`** — one command verifies the whole monorepo. Each lane is a separate project
  with its own dependency set, so a single root `pytest` collects all eight into one
  interpreter and dies; the Makefile shells into each lane with `uv`, which also bootstraps a
  clean clone.
- **CI** (`.github/workflows/ci.yml`) — four Python lanes, the root gate, the jar matrixed over
  **JDK 17 and 21**, collector-config validation, and an assertion that `LICENSE` exists.
- **`scripts/find-jdk.sh`** — locates a Spark-supported JDK with no global machine change.

### Fixed — correctness, and the reasoning behind it

- **Fixed skew thresholds replaced by a closed form.** A stage is tail-bound *iff*
  `p99/p50 > (n_tasks − 1) / (slots − 1)`. The previous 5×/10× constants ignored cluster width
  entirely. Effect over 31 calibrated runs: **127 findings → 65**. Every one of the 64 that
  disappeared sat on a Delta-metadata or map stage; all 14 survivors sit on the one genuinely
  skewed join stage.
- **A fabricated finding type.** `SKEW_ON_JOIN` was emitted on stages with **no Join node** and
  **zero shuffle reads**, recommending `skewJoin.*` flags that only apply to a join. Now
  requires join evidence from `plan_json` *and* `shuffle_read_bytes > 0`.
- **Ratios below 1 MiB/task are not statistics.** 50-task Delta-metadata stages at 97–625
  bytes/task were producing skew findings with ratios up to 10.72×.
- **`serve` contradicted `engine` in one response.** `serve` reads `apex.findings` correctly,
  but also computed an independent `StageSymptom` from fixed ratios — so the P0 stage rendered
  *"CRITICAL skew"* in the same payload where `findings` correctly held nothing. Resolved by a
  distinction rather than a patch: **a symptom is a measurement, a verdict is an
  adjudication.** `serve` states measurements always and verdicts only where it has the data.
- **`REGRESSION_PCT = 0.20` removed, not raised.** It sat *below* the measured shape-level noise
  floor (32–59%), so `compare_runs` was reporting noise as regression. Raising it would move the
  lie to a different scale; the floor is scale-dependent in both directions, so the only honest
  constant is none. Now caller-supplied or silent.
- **Telemetry was silently losing 50–70% of applications.** A runtime container alias present
  in no compose file, plus `collect`'s `clickhouse` alias shadowing `infra`'s on the shared
  network. **Every measurement taken before this fix was on partial data.** Fixed structurally:
  every service carries its globally-unique name as an alias and all internal hops are
  qualified, so a foreign container cannot capture traffic.
- **`argMax(x, ts) AS x` is `ILLEGAL_AGGREGATION`** when referenced in `WHERE` — so every noise
  floor silently read as *unmeasured*.
- **`FixedString(64)` returns bytes**, so `str(value)` produced `"b'11e45…'"` and every shape
  key silently missed. **No exception in either case.** Degraded optional reads now surface in
  `analyze()["store_warnings"]`.
- **Identity must not be derived from something that quietly moves.** Finding dedup keyed on an
  `evidence` string that embedded the measured floor and sample count — both of which *grow* as
  new runs land — so re-analysis inserted duplicate rows. Volatile context moved to
  non-persisted `details`. This was the third instance of one class in a single lane, alongside
  the two bugs above.
- **`skew_split` undercounted.** The plan snapshot has no split count; it lives in Spark's
  `numSkewedPartitions` driver metric, posted separately and only when the skewed read
  executes. Transitions are now parked until that accumulator lands.
- **Two of four cross-build cells had never been executed.** `apex_40` and `apex_41` need JDK
  17+; sbt's forked test JVM inherits sbt's own JVM (`Test / javaHome` is `None` and
  `JAVA_HOME` does **not** override it), so on a JDK 11 sbt they aborted while the 3.5 cells
  passed and the suite reported green. Both pass — they were never broken, only uncovered.
- **`onApplicationStart` cannot capture `spark.sql.*` defaults** — no `SparkSession` exists yet,
  so `adaptive.enabled` would be lost. Config capture moved to the first `onJobStart`.
- **`plan_json` is a redacted Catalyst tree-string, not JSON.** Two independent implementations
  agreed with each other and disagreed with the spec, which meant the **spec** was wrong.

### Contract rules — each discovered by an implementation contradicting the spec

1. **The tail-bound closed form.** A fixed skew threshold is wrong.
2. **The noise floor is scale-dependent and must be measured.** 5.8% → 9.2% → 37.7% on the same
   system. Noise means *unresolvable*, never *zero*.
3. **Attributability.** Fewer than 2 distinct configs ⇒ any spread is variance, not effect.
   Values must be canonicalized: `'5.0'` ≡ `'5'`, but `'8m'` vs `'67108864b'` is a real 8× gap.
4. **`mechanism_confirmed` / `runtime_certified` / `runtime_unresolved` are separate verdicts.**
   On a shared host, repetitions are not independent, so shrinking a standard error measures
   the wrong thing. Corollary: pick a positive control the predictor can actually model.
5. **`skew_split` gating on exchange bytes creates a false-negative class.** Projection pruning
   shrinks the exchange, so absence of a transition is **not** evidence of absence of skew.

### Known limits

- Runtime magnitude cannot be certified at laptop scale (~17–37% floor). Apex reports
  `mechanism_confirmed` + `runtime_unresolved` rather than a fabricated percentage.
- `memory/`'s corpus is a single environment; its confidence is directionally right and
  magnitude-uncertain.
- ZEST cold-start seeding is built but **not seeded** — the upstream dataset returns
  `403 AccessDenied`, verified by a live probe kept in the code so the claim stays falsifiable.
- The live six-lane gate's recorded run (2026-07-24) **predates** the correctness work above,
  including the telemetry-loss fix. See [`docs/e2e/README.md`](docs/e2e/README.md).

[0.1.0]: https://github.com/dataship/apex/releases/tag/v0.1.0
