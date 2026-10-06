# Changelog

All notable changes to Apex. Format loosely follows [Keep a Changelog](https://keepachangelog.com/);
versions follow [Semantic Versioning](https://semver.org/).

This file records not just *what* shipped but *what it cost to learn*, because in a
performance tool the reasoning behind a threshold is the product. Several entries below
are corrections to Apex's own earlier claims.

---

## [Unreleased]

### Changed

- The frozen contract has advanced through additive v0.5 and v0.6 extensions.
  v0.6 permits an optional Spark SQL `execution_id` on an `apex.stage` payload;
  it is producer-side correlation data, not yet a public execution-to-stage map.
- `apex-mcp` now exposes eight tools: `list_runs`, `analyze_run`,
  `explain_stage`, `compare_runs`, `search_kb`, `recall_similar_runs`,
  `verify_fix`, and `suggest_fix`.

### Fixed — the console reads the same rows through either door

Found by sweeping `apex-api` (PR #129) after its review fixes landed. The API
exists so the console can stop querying ClickHouse from the browser; that only
holds if a row is the same row whichever way it arrived. It was not, in four
places, and the unit suite could not see any of them because a fake returns
whatever rows it is handed — the projection lives in the SQL.

- **An unindexed run rendered a measured zero.** Both run rollups read
  `ifNull(s.task_time_ms, -1)` over a `LEFT JOIN` to `run_outcomes`, and
  ClickHouse fills a missed join with each column's DEFAULT, never NULL. The
  `ifNull` never fired: a run the memory lane had not reached came back as
  `task_time_ms 0`, `shaped_stage_count 0` and a blank `config_source`. The
  `shapes` CTE now emits `1 AS indexed` and the outer SELECT reads that.
  `SETTINGS join_use_nulls = 1` was not an option — `apex_ro` is `readonly = 1`.
  Confirmed live by putting the old statement back: `browser -1 != api 0`.
- **One timestamp, three shapes.** Every time column is `DateTime64(3)`. The
  browser read `2026-09-20 10:00:00.123`; the API emitted whatever Python's
  `isoformat()` made of the driver's value — six fractional digits, or **none**
  when the milliseconds were zero. There is one wire format now, the API's:
  ISO 8601 with a `T`, UTC, millisecond precision, no offset. All three console
  repositories return it, and a serve test reads the pattern out of the
  TypeScript so the two hosts cannot drift.
- **Four screens rendered a failed query as an empty store.** `useAsync`
  returned the error and RunDetail, Compare, Memory and Finding never read it.
  With the http source a wrong `APEX_API_TOKEN` looked like a connected console
  with nothing in it, and the API's `memory_unavailable` — *there is no table* —
  became "nothing indexed yet" — *there is no history*. One `QueryFailure`
  molecule now renders before any empty state.
- **The header named the wrong source.** `NavBar` branched two ways, so the http
  source wore the fixtures badge while every row came from the API. The label is
  an exhaustive map over `Repository["kind"]`.
- **The canonical six-lane gate failed every job.** `scripts/e2e_six_lanes.py`
  called `analyze_run` with no `detail`; serve's `summary` default trims the
  stages and findings it then counted, so every job ended
  `mcp_stage_count_mismatch:0!=N`. The probe asks for `detail=full`; a test pins it.
- **Spark executors were refused on the dev lane's C3 overlay.** Two networks,
  one advertised hostname, one bound interface — executors connected to an
  address nothing listened on and the job never scheduled. The `c3-*`/`c4-*`
  targets and `tests/e2e/run.sh` now pass `spark.driver.host` and
  `spark.driver.bindAddress`, as `e2e_canonical.sh` always had.

### Added

- **`serve/tools/console_parity_gate.py`** — a live gate that issues every
  console statement twice, as the browser does (ClickHouse HTTP, as `apex_ro`)
  and through the API, and fails unless both return the same rows. Status codes
  are what passed while three routes returned the wrong projection; this cannot
  be satisfied by one. `--job-id` writes nothing and reports a check the data
  cannot exercise as `NOT EXERCISED`, never as passed. Each of the five defects
  it exists for was put back in a scratch copy and named by it.
- **A control for the class of defect, not the instance.** Five times a console
  method was mapped onto a `ReadStore` method *by name* and served a projection
  the console does not read. `test_every_console_field_is_projected` reads eight
  row interfaces from the TypeScript and fails when the statement that serves
  one omits a field.
- **The console's http mode from the repo's own entry points.** `docker compose`,
  `make prod` and the README can now run it; before, only `serve/RUNBOOK.md`
  could, by hand.
- **`tests/e2e/console_reflection.sh`** — the fourth end-to-end entry point,
  and the first to reach the console: one job already in the store goes
  engine → memory → apex-api → the real App, every screen read against what
  the API returned. Recorded on three jobs, two of them generated by the Spark
  plugin in the same session (`serve/VALIDATION.md`).

### What it cost to learn

- This branch and the base fixed `findings`, `transitions` and `auto`
  **independently and on the same day**, and disagreed twice: the base keeps the
  v0.2 additive-column probe this work proposed to drop, and treats a 401 on
  `/v1/health` as "the API is there" where this work fell back to ClickHouse.
  The base prevailed on both and the branch was rebuilt on top of it. Two
  people solving the same defect without a claimed task is the cost; the
  TaskSpec leaves were never transitioned, so nothing said the work was taken.
- The first version of the gate **crashed** on the very defect it was written to
  name — a findings row with no `ts` raised `KeyError` instead of reporting.
  Found only because the gate was mutation-checked rather than trusted for
  passing.
- The local dev image was **74 minutes older** than the jar's `job_conf`
  emission and silently produced runs with no configuration: `config_source
  unknown`, a blind no-op gate, `0/5 runs with config` — all correct readings
  of an incomplete run. Nothing in the pipeline said the image predated the
  jar. The orchestrator warns now; the general lesson is that a baked-in jar
  needs a build-stamp the store can see.

### Known limits

- The verify lane has not been run end to end, so every `/verify` screen shows
  the honest absence and `fix_verifications` parity is proven on "no row" only.
- The diagnostics tier keeps the MCP tools' own timestamp fields; the wire
  format covers the resource tier and `/v1/health`.
- `/ask` is still a scripted mockup. The pieces exist — eight tools over `/v1`,
  an `HttpRepository` — and what is missing is a product decision on what Ask
  does with them, recorded as `D-2026-09-23-ask-consumer`.

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
6. **Rule 1 is vacuous when `n_tasks ≤ slots`.** `bar = (n−1)/(slots−1) ≤ 1` exactly when
   `n ≤ slots`, and `p99/p50 ≥ 1` always — so every such stage passes unconditionally, including
   a perfectly uniform one. Live: stage 25 at ratio **1.03**, stage 2 at **1.00**, both
   "tail-bound." Exclude them rather than passing them.
7. **A threshold on post-intervention telemetry measures the healed state.** Stage 29's exchange
   was **1.084 MiB/task** over its original 100 partitions — above the floor — but AQE split it
   into 114 tasks, giving 0.951 MiB/task, below. It was disqualified by the dilution its own fix
   produced. Detect the reshape (`task_count > shuffle.partitions`, joinable via `job_conf`);
   do **not** soften a measurability bound to compensate for a timing artifact.

### Fixed — found by the live end-to-end run

- **`serve` promoted skew symptoms stage-blind.** A `skew_split` is **execution-scoped** —
  contract v0.2 keys transitions by `(job_id, execution_id)` and carries no execution→stage map —
  yet every skew symptom was promoted to `critical` + `adjudicated=True` whenever one existed
  anywhere in the job. Live consequence: stage 25, a **1.03× ratio** (perfectly balanced),
  reported as *"critical skew, confirmed by Spark itself."* It also inflated `suggest_fix`
  confidence to 0.9. Fixed by removing promotion entirely: the split is now an execution-scoped
  note stating its own scope. Attaching it to "the stage it came from" was **rejected** —
  nothing in the contract ties an execution to a stage, and fabricating that tie is the same
  class of bug one layer down. `findings[]` was never affected, which is why the gate passed.

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
