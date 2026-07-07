# Apex v0.1

> Local Spark 4 lakehouse and execution-observability platform, with an agentic Spark-diagnostics layer.

## Overview

**Apex** is a self-contained, laptop-scale environment for studying Spark performance and building agent workflows that reason about real Spark runs. It stands up a full Spark 4.1.2 + Delta Lake lakehouse on MinIO, captures every Spark event log, normalizes it into ClickHouse, and then runs deterministic detectors (plus an optional CrewAI crew) that turn raw execution metrics into `spark.conf` recommendations.

Everything runs from project-local Docker images built out of locally cached dependencies, so `make compose` never silently pulls or drifts. The platform is the substrate; the diagnostics layer (`apex_diagnostics`) is what makes it a study bench for agent-driven Spark optimization.

This repository is a workspace with two parts:

| Path | What it is |
|------|-----------|
| [`apex-v0.1/`](apex-v0.1/) | The platform itself — Spark stack, lakehouse, observability, and the `apex_diagnostics` engine. All commands run from here. |


## Architecture

![apex platform data flow: one Spark engine feeds a lakehouse data plane (MinIO lakehouse bucket to Delta medallion tables) and an execution-observability plane (MinIO spark-logs bucket to Spark History and the Go eventlog-loader, into ClickHouse, then out to HyperDX and apex_diagnostics)](apex-v0.1/docs/diagrams/platform-data-flow.png)


One Spark engine feeds two independent planes. The **lakehouse data plane** writes Delta medallion tables to MinIO; the **execution-observability plane** captures event logs, normalizes them into ClickHouse, and drives both interactive dashboards and automatic diagnostics.

Raw event logs land in MinIO first as a replayable source of truth: if the parser or ClickHouse schema changes, logs can be reprocessed without rerunning any Spark job.


## Stack

| Component | Version | Role |
|-----------|---------|------|
| Apache Spark | 4.1.2 | Compute engine (`spark-submit`, client deploy mode) |
| Delta Lake | 4.2.0 | Lakehouse table format |
| MinIO | 2025-09-07 | S3-compatible object store for lakehouse data and event logs |
| ClickHouse | 26.5.1 | Analytical store for normalized Spark execution telemetry |
| HyperDX (ClickStack) | 2-beta | UI over the ClickHouse observability tables (MongoDB-backed) |
| eventlog-loader | Go 1.26 | On-demand loader: parses event logs into ClickHouse |
| CrewAI | >= 1.15.1 | Optional LLM layer that interprets findings |
| uv / Python | >= 3.10 | Project tooling and test environment |

## Quick Start

All commands run from [`apex-v0.1/`](apex-v0.1/). 
```bash
cd apex-v0.1

make bootstrap    # download jars, Python wheels, and Go deps once; sync the uv test env
make build        # build every project-local Docker image
make validate     # verify required images exist before Compose
make tests        # fast Python unit tests (fake Spark, no cluster needed)
make compose      # start the full stack and run readiness checks
make smoke        # ingest sample customer data through landing -> bronze -> sanity
make spark-logs   # load event logs into ClickHouse, then run diagnostics
make services     # print service URLs, credentials, and UI click paths
```

Stop and clean up:

```bash
make down         # stop the stack, keep local data
make clean-data   # delete local MinIO / ClickHouse / MongoDB state
make removeimage  # remove local project images; keep downloaded caches
```

## Spark Diagnostics

`apex_diagnostics` ([`src/apex_diagnostics/`](apex-v0.1/src/apex_diagnostics/)) analyzes completed Spark runs from ClickHouse and stores one report per application in the `spark_diagnostic_reports` table.

![apex_diagnostics engine: ClickHouse observability tables fan out to five deterministic detectors (skew, shuffle, plans, gc, oom) that converge into typed Pydantic findings; a CREW_LLM_MODEL decision routes either to the CrewAI Crew A (Diagnostic Analyst then Recommendation Writer producing spark.conf recommendations) or to a detectors-only report, both persisting to the spark_diagnostic_reports table](apex-v0.1/docs/diagrams/diagnostics-engine.png)

- **Deterministic detectors** emit typed Pydantic findings from parameterized SQL: skew stragglers, shuffle volume with memory/disk spill and GC, AQE re-plan counts, plus GC and OOM signals. Thresholds live in [`src/config/diagnostics.yaml`](apex-v0.1/src/config/diagnostics.yaml) — tuning is a YAML edit.
- **Optional LLM layer** — a CrewAI crew (Diagnostic Analyst → Recommendation Writer) writes `spark.conf` recommendations when `CREW_LLM_MODEL` and a provider API key are set. Without them, reports degrade to detectors-only output instead of failing.

```bash
make workloads              # run synthetic problem jobs that trigger findings
make spark-logs             # load event logs, then diagnose recent runs
make diagnose APP_ID=<id>   # diagnose one application by id
```

Synthetic workloads under [`src/workloads/`](apex-v0.1/src/workloads/) exist to produce findings on demand: `skew_join`, `shuffle_heavy`, `gc_churn`, `oom_victim`, `cross_join`, and `cache_heavy`.

### MCP server

An MCP stdio server exposes the tools `list_runs`, `detect_skew`, `detect_shuffle`, `detect_plans`, `get_report`, and `analyze_run`. `PYTHONPATH=src` is required because the project uses a src layout and is not installed as a package:

```bash
claude mcp add spark-diagnostics --env PYTHONPATH=src -- \
  uv run --directory apex-v0.1 python -m apex_diagnostics.mcp_server
```

## Repository Layout

```text
apex-v0.1/                           # the platform (run all commands here)                        
│   ├── Makefile                     # main local workflow contract
│   ├── pyproject.toml               # apex-v0.1 package + uv/pytest config
│   ├── build/                       # Docker images, Compose stack, bootstrap scripts
│   ├── src/
│   │   ├── spark_platform/          # reusable Spark utilities (session, io, jobs, config)
│   │   ├── apps/sample_scripts/     # landing -> bronze -> sanity sample flow
│   │   ├── workloads/               # synthetic problem jobs for diagnostics
│   │   ├── apex_diagnostics/        # detectors, CrewAI crew, MCP server, report store
│   │   └── config/                  # lakehouse.yaml + diagnostics.yaml
│   ├── tests/                       # pytest suites (fake Spark + fake ClickHouse)
│──-└── docs/                        # architecture, operations, observability guides
```

## Documentation

**Detailed technical guides** (this workspace, with icon-based process flowcharts):

- [`docs/Apex-Detailed-guide.md`](apex-v0.1/docs/Apex-Detailed-guide.md) — extremely detailed walkthrough of the whole platform: architecture, the four pipeline stages, table catalog, detectors, ClickStack, workloads, and the experiment cycle.


## Tests

Tests are managed with `uv` from the project root. Fast IO tests use fake Spark objects, so they validate the Spark fluent API without a running cluster or PySpark import. Detector tests use a fake ClickHouse client, so they run without the Docker stack or an LLM. Tests marked `llm` make real LLM calls and are opt-in via `RUN_LLM_TESTS=1`.

```bash
cd apex-v0.1
make tests
```

## Notes

- Local credentials in [`.env.example`](apex-v0.1/.env.example) are for local use only — do not reuse them in shared environments.
- Spark runtime and Spark History run as the upstream Spark user (`uid=185(spark)`) after root-only image build steps complete.
- Default UI ports: Spark Master `28081`, Spark History `28080`, MinIO Console `29001`, ClickHouse HTTP `28123`, HyperDX `28088`.
