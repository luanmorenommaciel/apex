# Apex

> **Peak performance intelligence for Apache Spark.** Open, self-hostable, and agentic: capture telemetry from inside the JVM, land it in an open store, reason over it with agents, and answer questions through an MCP server — so you ask *"why was this job slow?"* in plain language and get an answer backed by measurements.

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Spark](https://img.shields.io/badge/Spark-3.5%20%7C%204.0%20%7C%204.1-e25a1c.svg)](jar/)
[![Tests](https://img.shields.io/badge/tests-400-brightgreen.svg)](#verify-everything)

Apex is one monorepo of eight lanes. The directory list *is* the data flow:

```
dev  →  jar  →  collect  →  infra  →  engine  →  serve
                                        ↕
                                memory   verify
```

| Dir | Role | Language |
|---|---|---|
| [`dev/`](dev/) | **generate** — Spark/Delta lab producing real jobs with known pathologies | Python + Docker |
| [`jar/`](jar/) | **capture** — `SparkListener` → stage metrics, plan fingerprint, AQE decisions → OTLP | Scala |
| [`collect/`](collect/) | **transport** — OTLP `:4318` → PII scrub → ClickHouse | otelcol YAML |
| [`infra/`](infra/) | **store** — ClickHouse + HyperDX ("ClickStack") | SQL + Docker |
| [`engine/`](engine/) | **reason** — deterministic watchers + gated CrewAI → findings | Python / CrewAI |
| [`serve/`](serve/) | **interface** — read-only MCP server for Claude Code, Cursor, Codex | Python / FastMCP |
| [`memory/`](memory/) | **recall** — "we have seen this plan shape before, and here is what worked" | Python |
| [`verify/`](verify/) | **refute** — predict a fix's effect, replay it, report what can actually be certified | Python |

## What makes it different

Most Spark performance tools compete on *finding more things*. Apex competes on **not being wrong**, because a confident bad recommendation costs more than silence.

The `verify/` lane's first act was to **refute Apex's own headline demo.** Finding `189e3495` — *"critical 21.62× skew"* — failed four independent checks at once:

| Check | Result |
|---|---|
| **No-op gate** | the recommended `spark.sql.adaptive.skewJoin.enabled=true` was **already `true`** |
| **Bound analysis** | the stage is *work-bound* — a **perfect** fix returns **0.0 ms** |
| **Noise floor** | "21.62×" is 21.62 / 24.71 / 24.53 across three **byte-identical** runs |
| **Mechanism** | the stage moves **278 bytes/task** and its plan contains **no Join node at all** |

That is DataFlint's published SimilarWeb failure — a confidently-suggested `repartition(20000)` that left a 3-hour job at 3 hours — reproduced inside Apex, caught by Apex, and refused.

**Refusal is a first-class output.** Concretely, that gave us:

- **A closed form instead of a magic threshold.** A stage is tail-bound *iff* `p99/p50 > (n_tasks − 1) / (slots − 1)`. No tunable constant. A fixed 5×/10× threshold is simply wrong — it ignores how wide the cluster is, and volume cancels out of the derivation.
- **Measured noise floors, never inherited ones.** The same system measured 5.8%, 9.2%, and 37.7% depending on level and scale. A number carried across scales is wrong by up to 6.5×. Below the floor the magnitude is **withheld** — noise proves a delta *unresolvable*, never *zero*.
- **Honest unknowns.** `spark.executor.instances` appears in **0 of 51** real config rows, so cluster width is usually unknown. Apex answers *"tail-bound only above 5.8 slots"* rather than guessing a number.
- **Separate verdicts for mechanism and magnitude.** `mechanism_confirmed` ("the fix provably fired") is independent of `runtime_certified` ("and here is what it saved"). A laptop bench can honestly deliver the first and not the second.

Design rationale for all of it: **[CONTRACT.md](CONTRACT.md) — read it first.**

## Quick start

**Prerequisites:** Docker, [`uv`](https://docs.astral.sh/uv/), and JDK 17 for the jar lane (`brew install openjdk@17` — see [`jar/README.md`](jar/README.md), this one bites).

```bash
# 1. stand up the store
cd infra && make apply-ddl && docker compose up -d --wait   # ClickHouse + HyperDX

# 2. run a real Spark job with a known pathology, instrumented
cd ../dev && make up && make run-pathology JOB=skew_join

# 3. ask about it
cd ../serve && uv run --extra dev python -m apex_mcp.server   # MCP over stdio
```

Point Claude Code, Cursor, or any MCP client at `serve/` and ask *"why was `app-…` slow?"*

## Verify everything

One command, whole repo, **400 tests**:

```bash
make test
```

```
engine 114 (+2 skipped) · serve 92 · memory 40 (+7 skipped) · verify 105 · root gate 4  = 363 Python
apex_35(2.12) 9 · apex_35(2.13) 9 · apex_40 9 · apex_41 9                               =  36 Scala
```

Tests needing live ClickHouse **skip** rather than fail, so `make test` is green with no infrastructure running. `make help` lists every target.

Each lane is a separate project with its own dependency set, so a single root `pytest` **cannot** work — it collects all eight lanes into one interpreter and dies. The Makefile shells into each lane with `uv`, which also bootstraps a clean clone.

| Command | What it proves |
|---|---|
| `make test` | every unit + integration suite, no infrastructure needed |
| `make jdk` | which JDK the jar lane will build with, and why |
| `make verify-ddl` | every ClickHouse table matches its contract DDL *(needs infra up)* |
| `make verify-e2e JOB=<app-id>` | all six lanes agree on one real job *(needs infra up)* |

See **[docs/e2e/README.md](docs/e2e/README.md)** for how the three end-to-end entry points layer together, and what has been observed live versus what is still expected.

## Start here

1. **[CONTRACT.md](CONTRACT.md)** — the frozen interface every lane obeys, plus seven cross-lane rules that were each discovered by an implementation contradicting the spec.
2. **[PIPELINE.md](PIPELINE.md)** — stage map, dependency graph, build order.
3. **[docs/lanes/](docs/lanes/)** — the research-backed build brief for each lane.
4. **[CHANGELOG.md](CHANGELOG.md)** — what shipped, and what each fix cost to learn.

## Repo conventions

- **Monorepo, directory-per-lane.** Each lane owns its build file (`build.sbt`, `pyproject.toml`, `docker-compose.yml`) and its own README.
- **The contract is law.** [`contract/`](contract/) holds the canonical schema, DDL, and `sample_event.json` fixture. A lane may **add** a field; it may never rename or repurpose one. Only a ratified change amends the contract.
- **Branch per task, not per lane.** Short-lived `lane/task` branches → merge to a green `main`.
- **No silent green.** If a check could not run it says so and exits non-zero. Two of four cross-build cells went unverified behind a suite that reported green; the tooling now refuses to let that recur.

## Status

**v0.1** — all eight lanes implemented, 400 tests green, contract at v0.4, and the **canonical
six-lane gate PASSED live** against a real Spark job on 2026-07-29
([evidence](docs/e2e/evidence/six-lane-gate-app-20260729180235-0044.json) ·
[narrative](docs/e2e/CANONICAL_GATE.md)).

Known limits, stated plainly:

- **Runtime magnitude is not certified at laptop scale.** ~1.2 s of fixed overhead on a ~2 s stage puts a 17–37% floor under everything, so effects smaller than that are structurally unresolvable no matter how many repetitions you run. Apex reports `mechanism_confirmed` + `runtime_unresolved` instead of a fabricated percentage. Certifying magnitude needs a real cluster.
- **`memory/`'s corpus is one environment.** Its confidence numbers are directionally right and magnitude-uncertain until there is cross-host history.
- **ZEST cold-start seeding is built but not seeded** — the upstream dataset returns `403 AccessDenied`, verified by a live probe kept in the code so the claim stays falsifiable.
- **Spark 3.5 on JDK 21** is not officially supported by Spark, though both 3.5 cells pass there. Local builds prefer JDK 17, the only version supported by every cell; CI matrixes 17 and 21.
- **The 1 MiB/task skew floor can miss a stage AQE already split.** Splitting spreads the hot partition's bytes over more tasks, so a rescued stage systematically under-reads on bytes/task (live: stage 29 of the canonical run, 5% under the floor). The ground-truth path backstops it — engine reports the skew job-level from the `skew_split` transition. Adjudicated as intended conservatism, with the rationale in [docs/e2e/CANONICAL_GATE.md](docs/e2e/CANONICAL_GATE.md).

## License

[Apache-2.0](LICENSE). The same license as Apache Spark itself, and the patent grant matters for a tool you deploy against production workloads.
