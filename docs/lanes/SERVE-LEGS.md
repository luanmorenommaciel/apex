# SERVE lane — legs

> **Companion to [`SERVE.md`](SERVE.md).** `SERVE.md` is the frozen build brief for what
> already shipped (T1–T14). This file is the **forward plan**: the lane
> decomposed into six legs of user-facing work, each broken into candidate features.
> **Snapshot:** 2026-08-12 · branch `feat/base-project-e2e` · head `093c677` · 87 tests green.

## What the lane is today

| | |
|---|---|
| **Shipped** | `apex-mcp` — stdio MCP server, six tools (`analyze_run`, `compare_runs`, `list_runs`, `search_kb`, `verify_fix`, `suggest_fix`) and one resource (`apex://runs`) |
| **Proven** | contract DDL conformance, `argMax` latest-attempt, param binding vs `' OR 1=1 --`, injection hardening, `applied=False` as `Literal[False]`, cross-validated `21.62x` skew against the engine lane's independent watcher |
| **Code** | `src/apex_mcp/{server,ch,models,diagnose}.py` — 1832 LOC · tests 1133 LOC · two live gates |

## The user we are building for

A Spark/data engineer whose job got slow, working inside an MCP client (Claude Code /
Cursor / Codex). Apex's promise is **non-intrusive code↔execution correlation**. Every
feature below is judged against one question:

> *Does this shorten the distance between "this job is slow" and "this line is why"?*

## Two structural facts that shape every leg

1. **`create_server()` registers four `@mcp.tool` and nothing else** (`server.py:51-149`).
   No MCP `resources`, no `prompts`. Apex uses one of the protocol's primitives.
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
misconfigured user sees four healthy-looking tools that fail on every call.

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

**Today:** `analyze_run` is strong — `status="not_found"` is already distinct from
`"healthy"` (`diagnose.py:279`), AQE ground truth is narrated, `untrusted_fields` marks
observed text as data. The UX problem is **volume**: the real P0 run returns 17 stages
plus every finding in one payload.

| # | Feature | Note |
|---|---|---|
| F3.1 | `detail` level — `summary` / `stages` / `full` | the default answer should be three lines, not 17 stages |
| F3.2 | Coverage + freshness in the payload | turns "healthy" into "healthy, **and here is what I actually saw**" |
| F3.3 | `explain_stage(job_id, stage_id)` | drill-down instead of one fat response |
| F3.4 | Critical-path framing | `analyze()` already sums `p99_ms` as tail time — surface it as a path, not a list |

---

## L4 · Correlate — "which line of my code did this?"

The north star, and the thinnest part of the lane. serve is where the correlation
*surfaces*, but the linkage is earned upstream in the jar and contract lanes.

| # | Feature | Note |
|---|---|---|
| F4.1 | Stage → source line / notebook cell | the actual Apex thesis |
| F4.2 | Per-`stage_id` plan-transition linkage | today `(job_id, execution_id)`; flagged as a contract enhancement in `VALIDATION.md` |
| F4.3 | "AQE did X, your config says Y" | `_apply_ground_truth()` (`diagnose.py:224`) already knows the difference |

**Blocked on:** contract work outside this lane. Sequence it last.

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

## L6 · Learn — memory across runs

**Today:** `search_kb` is LIKE/token search over `findings` + redacted `plan_json`
(`ch.py:125-183`). The embedding path is a declared, unimplemented interface.

| # | Feature | Note |
|---|---|---|
| F6.1 | Implement the embedding backend | the interface is already pluggable |
| F6.2 | "This happened before, here is what fixed it" | auto-link finding → prior occurrence → applied remedy |
| F6.3 | Fleet view: recurring symptoms across apps | the compounding-value feature |

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
| 4 | **L5 Fix** | `verify_fix` is a thin wrapper with outsized value — over the *verify lane*, not over `compare_runs` (**shipped**) |
| 5 | **L6 Learn** | compounding, but needs run volume first |
| 6 | **L4 Correlate** | depends on contract/jar work outside this lane |

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
