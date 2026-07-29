# verify/ — ⑧ refute

**Role:** decide whether a recommended fix would actually work — and say so honestly when it
would not, or when the answer cannot be certified at this scale.
**Obeys:** [`../CONTRACT.md`](../CONTRACT.md) (v0.4) · **Full brief:** [`../docs/lanes/VERIFY.md`](../docs/lanes/VERIFY.md)
**Extension:** [`CONTRACT-EXTENSION-v0.3.md`](CONTRACT-EXTENSION-v0.3.md) (`apex.fix_verifications`, ratified)
**Exit criterion (met):** predicts a fix's effect analytically, replays it on the bench, and
emits `mechanism_confirmed` / `runtime_certified` / `runtime_unresolved` as separate verdicts —
including a live refutation of Apex's own headline finding. **105 tests.**

## Why this lane exists

Every other lane makes Apex *find* more. This one makes Apex *wrong less often*, which is worth
more: a confidently bad recommendation costs a user hours and costs the product its credibility.

The lane's first act was to refute Apex's own marquee finding — `189e3495…`, `SKEW_ON_JOIN`,
stage 4 of `app-20260724160310-0000`, *"critical 21.62×"*. It failed **all four** guardrails
simultaneously:

| Guardrail | What it found |
|---|---|
| **a. no-op gate** | the recommended `spark.sql.adaptive.skewJoin.enabled=true` was **already `true`** in the observed run |
| **b. bound analysis** | stage 4 is **work-bound** on 2 slots, so a *perfect* skew fix returns **0.0 ms** |
| **c. noise floor** | "21.62×" is 21.62 / 24.71 / 24.53 across three **byte-identical** runs; job CV is 5.8% |
| **d. mechanism check** | the stage moves **278 bytes/task** and its plan contains **no Join node** — it is Delta transaction-log processing |

That is DataFlint's published SimilarWeb failure (a confidently-suggested `repartition(20000)`
that left a 3-hour job at 3 hours) reproduced inside Apex. **Refusing beats guessing**, so
refusal is a first-class output — and every guardrail runs on data Apex already has, at zero
execution cost.

## The three stages

### ① PREDICT — `predict.py`, zero execution

The core model is a **makespan bound**, not a regression. For `n` tasks on `slots` concurrent
slots, list-scheduling gives `T ≈ max(p99, W/slots)`. A skew fix *redistributes* work rather
than removing it, so total work `W` is conserved and a perfect fix yields `T_after = W/slots`:

```
Δ_stage  =  W/slots − max(p99, W/slots)
```

which is **exactly zero whenever `W/slots ≥ p99`**. That is the work-bound regime, and it is the
single most useful thing this module computes — *"even a perfect fix returns nothing"* from two
order statistics and a core count.

Rearranged, the same bound gives the contract's rule 1:

```
tail-bound  ⟺  p99/p50 > (n_tasks − 1) / (slots − 1)
```

Volume cancels out. There is no tunable constant.

`W` is **not measured**: `executor_run_time_ms` exists in engine's in-memory `StageEvent` but is
**not** a column in `apex.spark_events` (verified against `system.columns`). So `W` is bracketed
between two task-distribution models and the prediction is reported as an **interval** — when
both ends agree, the verdict is safe to quote.

### ② REPLAY — `replay.py`, two-arm measurement

A prediction is an extrapolation; a replay is a measurement. Two sets of timed runs — a
**baseline** arm at the observed configuration and a **treatment** arm at the proposed one —
become a `Measurement` a consumer may quote. Three contract rules are enforced in code, not
prose:

- **Rule 1 (tail-bound).** The bench must be one where a skew fix *can* matter. The shipping
  bench is dev's calibrated `skew_join`: n=100 on 8 slots, p99/p50 = 17.7–20.6 against a
  threshold of `(100−1)/(8−1) = 14.14`. (2 slots is provably never tail-bound; 4 fails; 6 passes
  at ~1.1× margin; 8 is the default.)
- **Rule 2 (noise floor).** Measured from the baseline arm's **own** samples at the level and
  scale being compared, never inherited. The same system produced 5.8%, 9.2%, and 37.7% — a
  number carried across levels is wrong by up to 6.5×. Below `MIN_REPS_FOR_FLOOR` samples the
  floor is UNMEASURED and **no delta may be quoted at all**.
- **Rule 4 (separate verdicts).** Mechanism and magnitude are certified independently.

### ③ SAFETY GATE — `safety.py`, nothing reaches an executor without passing

Derived from [OptiSpark](https://pypi.org/project/optispark/) 0.2.0, with two corrections the
source verified:

- OptiSpark's **primary** defense is an AST `ReadOnlyValidator` that raises *before* `exec()` —
  not the size check. It blocks `.write`, `.save()`, `.saveAsTable()`, `.insertInto()`,
  `.drop()`, `.delete()`, `.truncate()`, and `DROP/DELETE/TRUNCATE/INSERT/UPDATE/CREATE` tokens
  inside `spark.sql()` strings. For Apex's *never touch customer data* rule this matters more
  than the size gate, so it runs first and **cannot be skipped**.
- OptiSpark's `optimizedPlan().stats().sizeInBytes()` check is **conditional** (only for
  high-risk ops, 50 MB default). Apex applies it **unconditionally** — "could this OOM the
  bench?" is not conditional on the operator.

> **The `Long.MaxValue` trap.** `stats().sizeInBytes()` falls back to
> `spark.sql.defaultSizeInBytes`, which is `Long.MaxValue` (8 EiB) when Catalyst has **no
> statistics** for the relation. A naive `size > budget` therefore blocks *everything* while
> looking like a working gate. The sentinel means **"stats absent"**, not "8 exabytes."

## Verdicts

`mechanism_confirmed` and `runtime_certified` are **independent** (contract rule 4):

| Verdict | Means | Requires |
|---|---|---|
| `mechanism_confirmed` | the fix provably fired | observable mechanism change (e.g. an AQE `skew_split` in `apex.plan_transitions`, a tail-ratio collapse beyond the ratio floor) — **does not** require clearing the runtime floor |
| `runtime_certified` | and here is what it saved | `\|Δ\| ≥ measured floor` **and** ≥ 2 distinct configs |
| `runtime_unresolved` | the mechanism fired; magnitude is deferred, not denied | the honest verdict when the floor swallows the effect |

**Live result on the real finding** (`app-20260728211208-0042`, stage 21: 100 tasks, p50 = 100 ms,
p99 = 2033 ms → 20.3× against 14.14, tail-bound on the plugin's own statistic):

> **MECHANISM CONFIRMED, RUNTIME UNRESOLVED** — the AQE `skew_split` transition fired (3/3);
> tail ratio 19.4× → 10.4× (−46.4%) beyond its ±13.7% floor. But the measured **+8.1%** is inside
> the **±57.5%** floor on `dev:skew_join`: magnitude deferred, not denied. Confidence HIGH (0.90).

The coherence check matters more than the number: the analytic predictor, running blind on the
same stage, independently said **−0.7% [−1.5 .. 0.0]** — *"almost nothing recoverable at 8
slots."* The makespan model and the replay reached the same conclusion by different routes. The
lane agrees with itself.

## The positive control, and why it was left failing

A verification lane needs a control that *should* show an effect — otherwise "no effect detected"
is unfalsifiable. The first control **failed twice**, and it was kept armed and failing rather
than tuned green.

Diagnosis: it was **mis-specified**, not mis-scaled. AQE's `skew_split` coalesced 100 partitions
→ 17 and median task time went 61–92 ms → 508–792 ms, so **`W` was not conserved** — it was a
repartitioning, not a pure tail redistribution. It tested a fix class `classify_fix` is
deliberately designed to refuse.

The re-specified control holds partition count constant (106 tasks = 100 + split subpartitions),
conserving `W`, and **passes**. It still cannot clear the runtime floor — which per rule 4's
corollary is the honest conclusion, not a failure: **laptop scale cannot certify small runtime
effects.** That limit is documented in the code and in the control's own output rather than
smoothed away.

## Where the observed config comes from — `config_source.py`

Contract v0.4 made ClickHouse the **primary** source: *"was `skewJoin.enabled` true on this
run?"* is answerable from `apex.job_conf` alone, so the no-op gate works on any platform shipping
Apex telemetry — not only deployments with a Spark History Server. The History Server REST API
remains a **fallback** for runs predating conf capture.

Every fetch resolves to one of three states:

| State | Meaning | Effect |
|---|---|---|
| `KNOWN` | a conf was retrieved | the no-op gate may deduce from it |
| `UNKNOWN` | source reachable, holds nothing for this run | confidence capped at MEDIUM, caveat *"cannot rule out that this fix is already active"* |
| `UNAVAILABLE` | source unreachable | same cap |

**Slots caveat (contract v0.4, explicit):** resource keys land in `apex.job_conf` **only if
explicitly set** — the jar never synthesises a default, because a fabricated default poisons
*"the config that worked."* So `slots_from_conf` returns `None` rather than a guess.

## Layout

```
verify/
├── src/apex_verify/
│   ├── predict.py         ① makespan bound; the work-bound test
│   ├── replay.py          ② two-arm measurement; rules 1, 2, 4 in code
│   ├── safety.py          ③ AST ReadOnlyValidator + unconditional size gate
│   ├── guardrails.py      the four zero-cost vetoes
│   ├── config_source.py   apex.job_conf primary, History Server fallback
│   └── models.py          Prediction · Measurement · Verdict
├── ddl/fix_verifications.ddl.sql   ratified v0.3; APPLIED BY infra/
├── scripts/run_replay.py           the replay + positive control runner
└── tests/                          105 tests
```

## Run it

```bash
make test-verify                      # from the repo root — 105 tests, no infrastructure
cd verify && uv run --extra dev python scripts/run_replay.py --help
```

## Lane boundaries

- **This lane never writes to customer data.** The safety gate is not advisory; it raises before
  `exec()`.
- **`apex.fix_verifications` is ratified here but applied by [`infra/`](../infra/)** — that lane
  owns DDL application. `verify` deliberately does not create it.
- **`plan_json` is written by the observed Spark job, not by Apex.** It is treated as untrusted
  input throughout (the indirect-injection vector documented in
  [`serve/README.md`](../serve/README.md)).
- **A verdict this lane cannot support is not emitted.** "Unresolved" is a shipped answer, not a
  bug to be fixed by loosening a threshold.
