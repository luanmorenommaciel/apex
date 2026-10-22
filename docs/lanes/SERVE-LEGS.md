# SERVE lane — legs

> **Companion to [`SERVE.md`](SERVE.md).** `SERVE.md` is the frozen build brief for what
> already shipped (T1–T14). This file is the **forward plan**: the lane
> decomposed into six legs of user-facing work, each broken into candidate features.
> **Snapshot:** 2026-08-12 · branch `feat/base-project-e2e` · head `093c677` · 87 tests green.
> **Updated:** 2026-10-22 · `main` @ `c3c3ea3` — adds [L7 · Pair](#l7--pair--every-ui-action-has-an-mcp-twin),
> the task list that pairs each console action with an MCP tool.

## What the lane is today

| | |
|---|---|
| **Shipped** | `apex-mcp` — stdio MCP server, eight tools (`analyze_run`, `explain_stage`, `compare_runs`, `list_runs`, `search_kb`, `recall_similar_runs`, `verify_fix`, `suggest_fix`) and one resource (`apex://runs`) |
| **Proven** | contract DDL conformance, `argMax` latest-attempt, param binding vs `' OR 1=1 --`, injection hardening, `applied=False` as `Literal[False]`, cross-validated `21.62x` skew against the engine lane's independent watcher |
| **Code** | `src/apex_mcp/{server,ch,models,diagnose}.py` — 1832 LOC · tests 1133 LOC · two live gates |

## The user we are building for

A Spark/data engineer whose job got slow, working inside an MCP client (Claude Code /
Cursor / Codex). Apex's promise is **non-intrusive code↔execution correlation**. Every
feature below is judged against one question:

> *Does this shorten the distance between "this job is slow" and "this line is why"?*

## Two structural facts that shape every leg

1. **`create_server()` registers eight `@mcp.tool` and one MCP resource.** The
   tools are listed above; `apex://runs` is the resource. Apex still defines no
   prompts.
2. **Every tool takes a `job_id` the user must already possess.** `ReadStore` exposes
   `stages` / `findings` / `plan_transitions` / `search` (`ch.py:206-254`) — there is no
   "list runs", no lookup by `app_name` or time. **The lane can diagnose a run but cannot
   help you find one.**

```mermaid
flowchart LR
    L1["L1 · Connect<br/>is Apex alive?"]:::a
    L2["L2 · Discover<br/>which run?"]:::hot
    L3["L3 · Understand<br/>what is wrong?"]:::a
    L4["L4 · Correlate<br/>which line of my code?"]:::star
    L5["L5 · Fix<br/>what do I change?"]:::b
    L6["L6 · Learn<br/>has this happened before?"]:::c

    L1 --> L2 --> L3 --> L4 --> L5 --> L6
    L6 -.->|"prior fixes inform the next diagnosis"| L3
    L5 -.->|"verify_fix reports apex.fix_verifications"| L2

    classDef a fill:#26343a,stroke:#83a598,color:#ebdbb2;
    classDef b fill:#3a2a1a,stroke:#fe8019,color:#ebdbb2;
    classDef c fill:#32302f,stroke:#d3869b,color:#ebdbb2;
    classDef hot fill:#3a3220,stroke:#fabd2f,color:#ebdbb2;
    classDef star fill:#2a3a2a,stroke:#b8bb26,color:#ebdbb2;
```

---

## L1 · Connect — "is Apex alive?"

**Today:** five env vars; `uvx --from <path>` because the package is not on PyPI; a
deliberately lazy client (`ch.py:302`) so the server finishes `initialize` and lists its
tools even when ClickHouse is down. Correct for protocol reasons — and it means a
misconfigured user sees eight healthy-looking tools that fail on every call.

| # | Feature | Note |
|---|---|---|
| F1.1 | `apex_status()` — connected, database, run count, latest ingest age, contract columns present | the first call any user makes; today there isn't one |
| F1.2 | Publish to PyPI → plain `uvx apex-mcp` | removes `--from`; listed as a known limit in `VALIDATION.md` |
| F1.3 | Connection errors that name the missing setting | `_sanitize()` (`ch.py:274`) correctly hides the password — it also hides the fix |
| F1.4 | Root `.mcp.json` + Cursor/Codex parity | the file exists in `serve/`, not at the repo root where clients look |

→ Broken into atomic tasks in [`L1_tasks.md`](L1_tasks.md).

---

## L2 · Discover — "which run?"  ✅ **DELIVERED** (branch `serve/l2-discover`)

**Was:** nothing. Every entry point demanded a `job_id` that had to come from outside
Apex. This was the single highest-leverage leg: no other leg was reachable without it.

| # | Feature | Delivered as |
|---|---|---|
| F2.1 | `list_runs(limit, since, app_name?, status?)` | ✅ `list_runs(limit, since_hours, app_name)` |
| F2.2 | `find_run(app_name)` | ✅ **subsumed** — `list_runs(app_name=…)` |
| F2.3 | `latest_run()` | ✅ **subsumed** — `list_runs(limit=1)` |
| F2.4 | `apex://runs` as an MCP **resource** | ✅ the lane's first resource |
| F2.5 | Auto-baseline: same `app_name` + `plan_fingerprint` | ✅ `compare_runs` with `baseline_job_id` optional |

**Why three features became one tool.** `find_run` and `latest_run` differ from
`list_runs` only by a `WHERE` clause and a `LIMIT`. Tool names are flat across every
server a client has loaded, and each tool is another user-influenced surface on
something a model can call. One filtered tool expresses all three; three tools would
have been API bloat bought with three injection surfaces.

**Auto-baseline refuses rather than guesses.** With no prior run sharing the current
plan shape, `compare_runs` returns `not_comparable` and says why. Comparing across a
plan change measures the plan, not the regression, and a silently wrong baseline
produces a confident wrong answer — the exact failure this lane exists to prevent.

**Safety.** `app_name` is set by the observed Spark job and now reaches both a `WHERE`
clause and the model's context. It binds server-side, is echoed only inside typed
fields, and never into a string Apex composes. Proven live: `' OR 1=1 --` returns 0 rows.

**What the live gate caught that no fake could.** Two defects survived a green unit
suite — a SQL alias collision that made every filtered query fail, and a
`datetime`/`str` mismatch that made every real row fail validation. `FakeClient` does
not parse SQL and every fake supplied string timestamps. See
[`serve/VALIDATION.md`](../../serve/VALIDATION.md).

**Follow-up:** `RUNS_SQL` does not carry `plan_fingerprint`, so auto-baseline costs up
to 10 extra stage queries. Adding it collapses that to one.

---

## L3 · Understand — diagnosis readability

**Was:** `analyze_run` was already strong — `status="not_found"` distinct from
`"healthy"`, AQE ground truth narrated, `untrusted_fields` marking observed text as
data. The UX problem was **volume**: the real P0 run returned 17 stages plus every
finding in one payload.

| # | Feature | Delivered as |
|---|---|---|
| F3.1 | `detail` level — `summary` / `stages` / `full` | ✅ `analyze_run(job_id, detail="summary")`, defaulting to the verdict |
| F3.2 | Coverage + freshness in the payload | ✅ `Diagnosis.coverage` on every verdict path |
| F3.3 | `explain_stage(job_id, stage_id)` | ✅ the lane's sixth tool |
| F3.4 | Critical-path framing | ✅ `StageView.tail_share` + `Diagnosis.tail_dominant_stage_ids` |

**One analysis, three widths.** `diagnose.trim()` narrows an already-computed
`Diagnosis`; it never re-analyses. Two callers asking at different detail levels
therefore cannot be handed different verdicts for the same run, and `full` is
literally the identity, so the widest payload cannot drift from `analyze()`'s own
output.

**A trimmed array is not an empty one.** Every narrowed level appends a note naming
what was dropped and how much of it there was. Without it, `findings: []` at summary
reads as "engine found nothing" — the opposite of the truth for the run that motivated
the work. `coverage` survives every level for the same reason.

**"Healthy" now says what it saw.** `Diagnosis.coverage` reports stages observed,
findings observed, transitions observed and the age of the newest event. That closes
W1, where a dropped `job_id` and a genuinely clean run produced the same confident
verdict. The age is **reported and never judged**: a nightly batch and a streaming job
disagree about what an hour means, so Apex owns no staleness threshold and a false
"stale" would be worse than no claim.

**Share of tail, not a critical path.** `analyze()` already summed `p99_ms` to rank
stages and then threw the shape away. It is surfaced as each stage's share of the tail
plus the smallest set owning most of it — and deliberately **not** called a critical
path, in the field descriptions and in the note. Stages overlap, and `p99` is a
per-task percentile standing in for stage wall time the contract does not carry. A
flat run names nothing rather than nominating whichever stage came first in a tie.

**Follow-up:** `STAGES_SQL` resolves each column with `argMax(col, ts)` and projects no
`ts`, so `coverage.newest_event_age_seconds` is `null` on the live path today. Null
reads UNKNOWN, not fresh, and the payload says so. Projecting a `ts` in `ch.py` closes
it — outside the write surface of the unit that surfaced it.

---

## L4 · Correlate — "which line of my code did this?"

The north star, and the thinnest part of the lane. serve is where the correlation
*surfaces*, but the linkage is earned upstream in the jar and contract lanes.

| # | Feature | Note |
|---|---|---|
| F4.1 | Stage → source line / notebook cell | the actual Apex thesis |
| F4.2 | Per-`stage_id` plan-transition linkage | transitions remain keyed by `(job_id, execution_id)`; v0.6 emits optional `execution_id` on stage payloads, but the store/read path and runtime proof still need to establish the mapping |
| F4.3 | "AQE did X, your config says Y" | `_apply_ground_truth()` (`diagnose.py:224`) already knows the difference |

**Blocked on:** F4.1 remains contract work outside this lane. F4.2 needs a
read-side consumer and runtime proof; F4.3 is independently buildable from
`apex.job_conf`. Do not sequence all three as one final leg.

---

## L5 · Fix — close the loop  *(shipped 2026-08-20, branch `serve/l5-fix`)*

> **Read this before touching L5.** The original plan below assumed serve would build
> `verify_fix` itself, as a thin framing over `compare_runs`. **That was wrong, and
> building it would have duplicated an entire lane.** The [`verify/`](VERIFY.md) lane
> already predicts, replays and safety-gates proposed fixes — 105 tests — and already
> writes its verdicts to **`apex.fix_verifications`** (contract v0.3, additive; DDL owned
> by verify, applied by infra). L5 is the **MCP surface over that table**, not a second
> implementation of the judgement it holds.

**The integration surface is `apex.fix_verifications`, not an import.** serve reads the
verify lane's verdicts exactly the way it reads the engine lane's findings out of
`apex.findings`: through ClickHouse. `serve/pyproject.toml` still depends only on `mcp`,
`clickhouse-connect` and `pydantic`, and a test greps the package to keep it that way.

**What shipped:**

| # | Feature | Status |
|---|---|---|
| F5.1 | `verify_fix(job_id, finding_id?)` → `FixVerdict` | **done** — reads `apex.fix_verifications`; reports the predicted range, any replayed measurement, the safety verdict and the confidence. Read-only. It reports a judgement; it does not make one |
| F5.2 | Surface confidence provenance | **done** — `suggest_fix` now carries the verification for its finding. A fix the verify lane **refused** leads the warnings and gets **no diff**: proposing a fix verify refused is the worst output this lane can produce |
| F5.3 | Ranked candidate fixes | still one recipe |
| F5.4 | MCP **prompts** → `/apex:diagnose`, `/apex:fix` | not started |

**Three distinctions the surface must keep** (collapsing any of them loses the point):

- `status="not_assessed"` ≠ "the fix is fine". No row means nothing was predicted and
  nothing was measured — an absence of evidence.
- `blocked=true` ≠ low confidence. A safety block is a refusal to **execute**; it is its
  own field and it leads the summary.
- `measured_delta_pct = null` ≠ `0.0`. Null means never replayed; `0.0` means replayed
  and unchanged.

**Deltas are SIGNED and negative means FASTER**, per the v0.3 DDL. The interval bounds are
ordered numerically, so `predicted_low_pct` is the *most* improvement. Every delta field
states the convention in its published JSON-schema description, because that description
is what a client actually reads. `diagnose._delta_phrase()` is the only place the sign is
turned into words.

`apex.fix_verifications` is additive, so `ReadStore.table_exists()` probes it once and a
pre-v0.3 cluster degrades to `not_assessed` instead of failing the call.

**Still open:** neither live gate has been run against a cluster with the v0.3 DDL
applied, so `VERIFICATIONS_SQL` has not yet met a real ClickHouse parser — the same class
of defect that L2 only found live.

---

## L6 · Learn — memory across runs  ✅ **DELIVERED** (branch `serve/l6-learn`)

**Was:** every tool on this server reasoned about exactly one run. `search_kb` is
LIKE/token search over `findings` + redacted `plan_json`, which finds *text*, not
*shapes* — it cannot answer "have we run this plan before, and what did it do".

**The correction this leg records.** The earlier plan for L6 read *"implement the
embedding backend"*. That work already exists, in the **memory lane**: a
structural encoder, an L2-normalised embedding table, a measured similarity
threshold and a measured per-shape noise floor. Building a second one here would
have duplicated a lane with 47 tests and produced a second, disagreeing answer to
the same question. **L6 is an MCP surface over the memory lane, not a
reimplementation.**

| # | Feature | Delivered as |
|---|---|---|
| F6.1 | Implement the embedding backend | ❌ **withdrawn** — the memory lane owns encoding; serve reads its output |
| F6.2 | "This happened before, here is what fixed it" | ✅ `recall_similar_runs(job_id, top_k, noise_floor_pct?)` |
| F6.3 | Fleet view: recurring symptoms across apps | deferred — needs run volume, and the read layer it would sit on now exists |

**The integration surface is the contract, not an import.** serve reads
`apex.plan_memory` (one row per plan shape, carrying an L2-normalised
`embedding` and the decoded features that let a human say *why* two plans
matched) and `apex.run_outcomes` (one row per shape per run: the six typed
config columns, the wall clock, and how it went). It imports nothing from the
memory lane, so this package still depends only on `mcp`, `clickhouse-connect`
and `pydantic`. Similarity is computed **in ClickHouse** — the embedding is
already normalised, so `1 - cosineDistance` is the cosine similarity and serve
needs no encoder of its own. The embedding width is read from the queried
shape's own `dim` rather than assumed; the encoder's width is the memory lane's
to change.

**Both tables are contract v0.3 ADDITIVE**, so a cluster that has not applied
them is a normal older deployment. Every read degrades to empty and the tool
answers `memory_unavailable` — *no history to read*, which is a different fact
from *no history*. Only a missing schema degrades: a store that is **down**
still raises, because answering "no prior runs" for an unreachable ClickHouse
would be a lie in the one place this lane cannot afford one.

**The floor rule is the whole leg.** Cross-run memory is worth having only if it
distinguishes *this config is better* from *this run happened to be faster*.
Rank a shape's prior runs by wall clock and the top row **looks** like the best
configuration when nothing of the sort has been measured. So prior runs are
reported as measurements, and `better` is reachable only through a
caller-supplied `noise_floor_pct` measured for this shape at this scale
(CONTRACT.md rule 2) — and then only when the history holds two distinct
**captured** configurations to credit the difference to (rule 3). Below the
floor the answer is "indistinguishable from run-to-run variation", which is not
"no change".

**Honest provenance.** `config_source` never defaults to `observed`. Apex
captures no SparkConf today — the v0.3 DDL says so explicitly — so most
`run_outcomes` rows are `unknown` and carry a `config_unavailable` note instead
of six nulls a reader could skim as "defaults". Closing that gap is a jar-lane
change, not this lane's.

**Retrieval is two-tiered and says which tier it used.** EXACT
`plan_fingerprint` equality needs no embedding at all and is the strongest
evidence available; STRUCTURAL similarity means the plans are indistinguishable
after redaction, which is weaker and is labelled. Neighbours below the
similarity threshold are dropped rather than returned as the nearest available
thing — when nothing matches, the honest answer is that nothing matches.

**Follow-up:** the tool takes `noise_floor_pct` from the caller. The memory lane
already computes a per-shape floor from its own history; wiring serve to read it
would close the last manual step, and needs a contract surface for the figure.

---

## L7 · Pair — every UI action has an MCP twin

**Decision (Crew A sync, 2026-09-15):** a FastAPI layer sits between ClickHouse and
every consumer. Claude / Codex / Cursor reach Apex through `apex-mcp`; the console
reaches it through FastAPI; **the MCP routes its queries through that same API**
instead of opening its own ClickHouse connection. The console and the MCP are two
front doors onto one product, so anything a user can do by clicking must be
something an agent can do by calling a tool — and both must get the same answer.

**Where main stands (`c3c3ea3`):**

- `serve/src/apex_api` is merged: 11 resource routes (raw rows) + 8 diagnostic
  routes (one per MCP tool) under `/v1`, behind a token.
- The console (`front/`) reads only the **resource** routes and computes its
  verdicts in TypeScript (`front/src/contract/rules.ts`).
- `apex-mcp` still opens ClickHouse directly (`ch.py` → `clickhouse_connect`) and
  computes verdicts in Python (`diagnose.py`).
- `serve/tools/console_parity_gate.py` proves the console's rows match across *its*
  two doors (browser→ClickHouse vs browser→API). **Nothing yet proves the console
  and the MCP agree on a verdict** — two implementations of the seven rules can
  drift, which is the contradiction class the contract exists to close.
- `AskScreen` is a scripted mockup with no backend.

### Pairing map

| Screen · action | Console reads today | MCP twin | Gap |
|---|---|---|---|
| Health badge | `GET /v1/health` | `apex_status` — **not registered** (L1) | finish L1; same payload both doors |
| Runs · recent list | `GET /runs?limit=50` — no time window | `list_runs` — defaults `limit=20`, `since_hours=168` | different defaults: a run older than 7 days, or the 21st–50th, shows in the console only |
| Runs · search job_id / app_name / fingerprint | client-side filter | `list_runs(app_name)` | no `job_id` or `plan_fingerprint` filter |
| Runs · "findings only" | client-side filter | — | no `has_findings` filter |
| Run detail · verdict, stages, findings, transitions | `/runs/{id}`, `/stages`, `/findings`, `/transitions` + `rules.ts` | `analyze_run(detail)` | two verdict engines; no cross-door check |
| Run detail · stage drill-down | in-page, from rows | `explain_stage` | console never calls `/stages/{id}/diagnosis` |
| Run detail · conf tab | `/runs/{id}/conf` | — | job_conf not exposed to MCP (ties to F4.3) |
| Run detail · plan sample | `/plans/{fp}/sample` | — | not exposed to MCP |
| Run detail · "compare to baseline" | → Compare | `compare_runs` | see Compare |
| Run detail · "ask about this run" | → Ask (mock) | — | MCP prompt `/apex:diagnose` (F5.4) |
| Run detail · "propose fix" | → Verify | `suggest_fix` | MCP prompt `/apex:fix` (F5.4) |
| Finding detail | findings + `fixVerification` + `shapeRuns` | `verify_fix(job_id, finding_id)` (partial) | no single-finding lookup by `finding_id` |
| Compare · pick baseline | `/runs/{id}/baseline-candidates` | `compare_runs` auto-baseline | MCP cannot list candidates; console ignores `/comparison` |
| Memory · plan shapes + runs per shape | `/plans`, `/plans/{fp}/runs` | `recall_similar_runs` (per job only) | no shape-level listing (F6.3 fleet view) |
| Verify · proposal + two verdicts | `fix_verifications.proposed_config`, projected as `proposed_diff` | `verify_fix` + `suggest_fix` (generates a diff and carries `proposed_config`) | two representations of one proposal — confirm they cannot disagree |
| Verify · copy diff | clipboard | n/a — `applied=False` | paired by design ✅ |
| Ask · natural-language question | scripted mock | all tools | no backend at all |
| — | — | `search_kb` | no console surface |

### Tasks

Sizes follow the taskspec scale. "Owner" is a suggestion from the 09-15 sync.

| # | Task | Size | Depends on | Owner |
|---|---|---|---|---|
| P7.1 | **MCP over HTTP.** Add an API-backed read path to `apex-mcp` (`APEX_API_URL` + token) so every tool reads through FastAPI; keep direct ClickHouse only as an explicit opt-in for local dev. Errors keep `_sanitize()` discipline — no token or URL reaches the model. | M | — | Sidymar |
| P7.2 | **One verdict engine.** Make the console call the diagnostic routes (`/diagnosis`, `/comparison`, `/recall`, `/verification`) instead of re-deriving verdicts from raw rows, or — if `rules.ts` must stay client-side — add a gate that runs both on the same seeded runs and fails on any difference. | L | P7.1 | Agmar + Sidymar |
| P7.3 | **Cross-door parity gate.** Extend `console_parity_gate.py` (or a sibling) with one check per pairing-map row, in three kinds: *job-scoped* rows compare both doors' answers for the same `job_id`; *unscoped* rows (health, run list) compare them under the same normalized parameters; *n/a* rows (copy diff) are listed as excluded, with the reason. P7.3 ships the gate and the rows already paired once P7.2 lands. Each later pairing task adds its own row as part of its done criteria, so the gate never waits on unrelated work and never silently skips a row. | M | P7.2 | — |
| P7.4 | **Finish L1 `apex_status`** and make `GET /v1/health` return the same `ServerStatus` model. | S | L1 tasks | — |
| P7.5 | **Align the run list.** Give `list_runs` and `GET /runs` the same default limit, time window and paging (today 20 rows / 168 h vs 50 rows / no window). Then add `job_id` prefix, `plan_fingerprint` and `has_findings` filters to both, so the console stops filtering client-side. | S | — | — |
| P7.6 | **Expose job_conf + plan sample** to the MCP by extending `analyze_run(detail="full")` rather than adding tools (keeps the tool surface flat, per the L2 rule). Unblocks F4.3. | S | — | — |
| P7.7 | **Finding lookup.** Decide: extend `verify_fix` / `analyze_run` to accept `finding_id` alone, or add one `get_finding` tool. Default to extending. | S | — | — |
| P7.8 | **Baseline candidates in `compare_runs`.** Return the candidate list in the payload (always, and as the reason on `not_comparable`); switch Compare to `/comparison`. | S | P7.2 | — |
| P7.9 | **Plan-shape listing** for the Memory screen: an `apex://plans` resource (not a tool) mirroring `/plans` and `/plans/{fp}/runs`. Delivers F6.3. | S | — | — |
| P7.10 | **One proposal source.** `apex.fix_verifications` stores `proposed_config` (canonical JSON). `proposed_diff` is only the name the console and `ch.py` project it under, while `suggest_fix` generates a real diff. Compare the normalized `proposed_config` the two doors carry for the same finding, not the rendered text. If they can differ, make the stored row authoritative and have `suggest_fix` render from it. No schema change. | S | — | — |
| P7.11 | **Wire Ask.** Replace the script with calls to the diagnostic routes. Open question first: does Ask put an LLM in the loop (`llm_calls` > 0), or is it a structured router over the tools? | M | P7.1, P7.2 | Agmar |
| P7.12 | **MCP prompts** `/apex:diagnose` and `/apex:fix` — the agent-side twins of "ask about this run" and "propose fix". Closes F5.4. | S | — | — |
| P7.13 | **`search_kb` in the console** — a search box on Ask or Runs over `/diagnostics/search`. | XS | — | — |
| P7.14 | **Retire `apex-mcp-http`.** FastAPI now owns the HTTP path, so the prototype has nothing left to serve; delete it or record why it stays. | XS | P7.1 | Agmar |

**Order:** P7.1 → P7.2 → P7.3 is the spine — until the MCP reads through the API and
both doors share one verdict engine, every other pairing can drift silently. The S/XS
rows are independent and can run in parallel with the spine.

**Done when** every row of the pairing map has an MCP twin (or a written reason it
should not), and the cross-door gate passes on a live cluster.

### Status — 2026-10-22

Tracked in Linear (project **Apex**, `SRP-*`). Nothing in L7 is merged yet.

| # | State | PR | Linear | Evidence / note |
|---|---|---|---|---|
| P7.1 | **in review — ready** | #195 | SRP-16 | Live QA on 7 real Spark runs: all 8 tools + `apex://runs` identical through ClickHouse and through the API (0 differences); console parity 0 failed; no secret leaks under failure. Serve suite 749 passed. |
| P7.10 | in review | #193 | SRP-22 | `suggest_fix` now renders the stored verified `proposed_config`. Codex follow-ups fixed: both doors reject the same numbers, per-finding lookup (no 50-row cap), same tie-break. 517 passed; live parity 17/0. |
| P7.12 | in review | #194 | SRP-23 | Prompts `/apex:diagnose`, `/apex:fix`; 525 passed; stdio-listed with no database. |
| P7.13 | in review | #192 | SRP-24 | Search KB screen; CI green (route registered against the existing search route). |
| P7.2 | **needs a decision** | — | SRP-25 | Console calls the diagnostic routes, or `rules.ts` stays behind a parity gate? Blocks P7.3, P7.8. |
| P7.11 | **needs a decision** | — | SRP-29 | Does Ask put an LLM in the loop? |
| P7.14 | **needs a decision** | — | SRP-26 | Retire `apex-mcp-http`? |
| P7.3, P7.8 | blocked | — | SRP-27, SRP-28 | Wait on P7.2. |
| P7.5 | in review — stacked on #195 | #200 | SRP-18 | Same defaults on both doors (50 rows, 7 days, offset paging) + server-side filters; 826 passed; live parity 28/0. CI runs once retargeted to main. |
| P7.6, P7.7, P7.9 | next | — | SRP-19, -20, -21 | Follow P7.5 on the same stack. |
| P7.4 | blocked | — | SRP-17 | Waits on the remaining L1 status tasks. |

**Found while live-testing** (outside L7, all pre-existing on `main`):

| Item | PR / Linear |
|---|---|
| `serve/tools/recall_gate.py` asserted a stale 6-tool list | #196 · SRP-30 |
| Pinned `minio/minio` + `minio/mc` can't be pulled; dev store moved to RustFS (verify 6/6, canonical E2E 4/4) | #197 · SRP-31 |
| MCP stalls when the store hangs (serial calls × 30 s timeout) | SRP-34 |
| verify lane never writes `apex.fix_verifications` | SRP-33 |
| engine evidence validator rejected the driver_oom finding (validator rule stricter than the contract) | #198 · SRP-36 |
| `make verify-e2e` env + scripts not executable (`e2e_canonical.sh`, `scripts/apex.sh`) | #199 · SRP-32, SRP-35 |
| compare refuses two plain skew_join runs (1 of 9 fingerprints differs) | SRP-37 |
| jar may sample a `TaskResultLost` attempt as a success | SRP-38 |
| six-lane gate labels the serve lane "degraded" when it passes | SRP-39 |

---

## Cross-cutting rail — the safety guarantees stay visible

Not a leg; an invariant no leg may break.

- `applied` is `Literal[False]` — a suggestion claiming otherwise **cannot be constructed**.
- Observed Spark text stays in typed data fields; `tests/test_injection_hardening.py`
  patches `subprocess.*`, `os.system/popen/remove/unlink/rmdir` and write-mode `open()`
  to fail the test if any is called.
- Driver exceptions are replaced with short codes — the password, host and port of the
  connection string never reach the model.
- **stdout is the JSON-RPC channel.** Nothing in `src/apex_mcp/` may `print()`.

Every new tool inherits the read-only annotation discipline and the param-binding tests.

---

## Sequencing

| Order | Leg | Why here |
|---|---|---|
| 1 | **L2 Discover** | the lane is unusable without a `job_id` sourced from outside the system |
| 2 | **L1 Connect** | cheap, and it is the first thing a new user hits |
| 3 | **L3 Understand** | payload volume is the loudest complaint once people can actually reach a run |
| 4 | **L5 Fix** ✅ | `verify_fix` is a thin wrapper with outsized value — over the *verify lane*, not over `compare_runs` (**shipped**) |
| 5 | **L6 Learn** ✅ | compounding, and delivered ahead of its slot once the memory lane made it a read rather than a build |
| 6 | **L4 Correlate** | depends on contract/jar work outside this lane |
| 7 | **L7 Pair** | the 2026-09-15 FastAPI decision; can run alongside L1 and ahead of L4 — its P7.1→P7.3 spine is the next build |

**L1 is being built first by decision**, ahead of L2 — see [`L1_tasks.md`](L1_tasks.md).

---

## Correction to a standing document

`docs/WEAKNESSES-AND-OPEN-QUESTIONS.md:83` records *"`serve`: `analyze_run` returns an
empty diagnosis"* for a dropped `job_id` (W1). **That is stale.** `diagnose.analyze()`
returns `status="not_found"` with an explicit message, distinct from `"healthy"`:

```python
# diagnose.py:279
if not stages:
    return Diagnosis(job_id=job_id, status="not_found", summary=(
        "No stage telemetry exists for this job_id. Check the id, or "
        "confirm the jar/collect lanes shipped this run."))
```

W1 remains real for the **engine** lane and for the six-lane gate. It is not a serve
defect and should not be scheduled here.
