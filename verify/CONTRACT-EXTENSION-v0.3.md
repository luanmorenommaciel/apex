# Proposed CONTRACT extension v0.3 — `apex.fix_verifications`

**Status:** ✅ **RATIFIED as contract v0.3** (CONTRACT.md changelog, commit 5c19173). The table is canonical; `infra` owns applying it to the store (per CONTRACT.md, "infra owns application, contract owns the schema").
**Proposed by:** `verify` lane · **Kind:** purely **additive** (one new table; no existing column renamed, retyped or repurposed)
**Canonical DDL:** [`ddl/fix_verifications.ddl.sql`](ddl/fix_verifications.ddl.sql)
**Affects:** `verify` (writes) · `serve` (reads, optional) · `infra` (creates the table) · `engine` (unaffected) · `jar`/`collect`/`dev` (unaffected)

---

## Why a new table instead of columns on `findings`

A finding is **one row per detected issue**. A verification is **one row per (finding × proposed_config × attempt)** — the same finding can be verified against several candidate configs, re-verified after a bench change, and carries both a prediction and an optional measurement. That is a different cardinality, so it is a different table. Widening `findings` would either denormalise (repeat the whole finding per candidate config) or force one blessed config per finding, which is exactly the "single confident guess" failure mode this lane exists to remove.

`findings` stays untouched. Consumers that never read `fix_verifications` behave exactly as today.

## Proposed schema

See [`ddl/fix_verifications.ddl.sql`](ddl/fix_verifications.ddl.sql) for the authoritative version with per-column comments. Shape:

| Group | Columns |
|---|---|
| identity | `verification_id`, `finding_id`, `job_id`, `app_id` |
| what was evaluated | `proposed_config` (canonical JSON of the Spark conf overlay), `method`, `predictor` |
| prediction | `predicted_delta_pct`, `predicted_low_pct`, `predicted_high_pct` |
| measurement | `measured_delta_pct`, `baseline_ms`, `treatment_ms`, `noise_floor_pct`, `replay_reps`, `bench`, `shape_fidelity` |
| safety | `safe`, `safety_verdict`, `safety_detail` |
| verdict | `confidence`, `confidence_score`, `evidence`, `caveats` |
| provenance | `verify_version`, `verified_at` |

`ORDER BY (job_id, finding_id, verified_at)` — `serve.suggest_fix` is called with `job_id` (+ optional `finding_id`), so that is the access path. `PARTITION BY toYYYYMM(verified_at)`, matching `findings` and `spark_events`.

## Four decisions that need your explicit sign-off

**1. `Nullable` for the measured columns — a deliberate departure from house style.**
`findings.ddl.sql` uses `DEFAULT ''` / `DEFAULT 0` and no `Nullable`. Here that would be a correctness bug: `measured_delta_pct = 0` means *"we replayed it and it changed nothing"* — a real, valuable, hard-won result — while *"we never replayed it"* is a different statement entirely. Collapsing both to `0` destroys the distinction this lane is built to preserve. So `measured_delta_pct`, `baseline_ms`, `treatment_ms`, `noise_floor_pct` are `Nullable`; everything else follows house style. **If you want zero `Nullable` in the contract, the alternative is a `measured UInt8` presence flag — say which you prefer.**

**2. Signed percentages, negative = faster.** `predicted_delta_pct = -38.0` means "38% faster". This matches how `findings.impact` already reads (`"-38% runtime"`). Alternative is unsigned + a direction column; signed is fewer moving parts.

**3. `method = 'refused'` is a first-class outcome, not an error.** A row with `method='refused'`, `predicted_delta_pct=0`, `confidence='HIGH'` is the honest encoding of *"this fix is already active in the observed run, it will do nothing, and we are confident about that."* Rejecting `refused` at write time would push the lane back toward fabricating a number. It needs to persist.

**4. `noise_floor_pct` is load-bearing, not decorative.** It is the run-to-run coefficient of variation of the **baseline arm**. Rule: **when `|measured_delta_pct| < noise_floor_pct`, no consumer may render the measured number** — it must render "indistinguishable from zero". Encoding that as data rather than prose is what stops a −4% measurement on a ±6% bench from being quoted as a −4% win. I would like this stated in `CONTRACT.md` as a consumer obligation, not just as a column.

## The conf source — RESOLVED by contract v0.4

The **no-op gate** (§ above, and the single most valuable thing this lane found) needs the observed run's effective `SparkConf`. **Contract v0.4 (`apex.job_conf`) now captures it**: one row per `job_id` with the resolved, allowlisted `spark.*` subset, emitted by the jar at first `onJobStart`.

`verify/src/apex_verify/config_source.py` implements the source chain: **ClickHouse `apex.job_conf` is PRIMARY** (the gate now works on any platform that ships Apex telemetry), the **History Server REST API is the FALLBACK** for runs that predate conf capture or ran with `spark.apex.conf.enabled=false`. The three pluggable states — `known` / `unknown` / `unavailable` — are kept, and **`unknown` still caps confidence at MEDIUM** with the caveat *"cannot rule out that this fix is already active."*

One v0.4 caveat the lane honours explicitly: resource keys (`spark.executor.instances`/`cores`) land in `job_conf` **only if explicitly set**, so cluster width (`slots`) may be undeterminable even with a KNOWN conf. `slots_from_conf` returns `None` rather than guessing, and `predict(slots=None)` withholds the makespan bound with confidence capped (contract rule 1).

## Migration

Additive `CREATE TABLE`. No `ALTER`, no backfill, no reader changes required. `serve` should probe for the table's existence exactly the way it already probes for `app_id` / `confidence_score` (per `serve/README.md`, "Additive contract columns are probed, not assumed") so a cluster that has not applied it still serves.

## Write target

Ratified as v0.3, so `verify` may write canonical `apex.fix_verifications` once `infra` applies the DDL (per CONTRACT.md, infra owns application). Until the table exists in the target cluster, the lane falls back to a **local** database (`apex_verify_local`, override with `APEX_VERIFY_DATABASE`) and reads canonical `apex` read-only. Nothing in this lane writes to any other `apex.*` table.
