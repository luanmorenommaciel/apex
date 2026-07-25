# Apex

> **Peak Performance for Apache Spark.** An open, self-hostable, agentic performance & code-review system for vanilla Spark — capture telemetry, land it in an open store, reason over it with agents, and serve fixes through an MCP.

Apex is a 6-stage pipeline in one monorepo. The directory list *is* the data flow:

```
dev  →  jar  →  collect  →  infra  →  engine  →  serve
```

| Dir | Role | Language |
|---|---|---|
| [`dev/`](dev/) | generate real Spark jobs with known pathologies | Python + Docker |
| [`jar/`](jar/) | capture stage metrics + plan fingerprint → OTLP | Scala |
| [`collect/`](collect/) | OTLP → PII scrub → ClickHouse | otelcol YAML |
| [`infra/`](infra/) | ClickStack store & serving (ClickHouse + HyperDX) | SQL + Docker |
| [`engine/`](engine/) | deterministic watchers + gated CrewAI → findings | Python/CrewAI |
| [`serve/`](serve/) | MCP server for Claude Code / Cursor / Codex | Python/FastMCP |

## Start here

1. **[CONTRACT.md](CONTRACT.md)** — the frozen interface every stage obeys. Read it first.
2. **[PIPELINE.md](PIPELINE.md)** — the stage map, dependency graph, and build order.
3. **[docs/lanes/](docs/lanes/)** — the detailed, research-backed build brief for each stage.
4. **[APEX V1 swimlanes](docs/architecture/APEX-V1-SWIMLANES.md)** — the approved product flow, decisions, gates, and security boundaries.
5. **[V1 PR plan](docs/architecture/APEX-V1-PR-PLAN.md)** — the lane-by-lane delivery and merge order.
6. **[ENGINE/SERVE delivery status](docs/convergence/C9-ENGINE-SERVE-DELIVERY-STATUS-2026-07-24.md)** — current PRs, verified evidence, and integration order.
7. **[Augusto E2E readiness](docs/convergence/C10-AUGUSTO-E2E-READINESS-2026-07-24.md)** — current local verification, the cross-lane fix, and the remaining operational rerun.
8. **[Study guide by lane](docs/study/README.md)** — visual macro flow, distributed states, payload sequence, architecture, guided study and sanitized evidence.

## Quick start (once built)

```bash
# 1. stand up the platform
cd infra && docker compose up -d          # ClickHouse + HyperDX

# 2. (fast path) load the fixture → build the brain without the JAR
clickhouse-client < contract/spark_events.ddl.sql
#   ... load contract/sample_event.json ...
cd engine && uv run pytest                 # watchers + gated crew work against synthetic rows

# 3. (full path) run a real pathology job end-to-end
cd dev && make up && make run-pathology JOB=skew_join
#   dev → jar → collect → infra → engine → serve
```

## Canonical E2E gate

The cross-lane gate validates an already-submitted real Spark application. It
does not start infrastructure, delete telemetry, call an LLM, or print secrets.
It proves that the persisted events, deterministic ENGINE findings, and
read-only SERVE response agree for one `job_id`.

```powershell
# Start COLLECT + INFRA, then export operator-provided local credentials.
$env:CLICKHOUSE_HOST = "127.0.0.1"
$env:CLICKHOUSE_PORT = "8123"
$env:CLICKHOUSE_USER = "apex"
$env:CLICKHOUSE_PASSWORD = "<local-secret>"
uv run --project serve --extra dev python scripts/e2e_six_lanes.py --job-id <spark-app-id>
```

On Windows, run the four Spark pathologies with Docker native (not WSL Bash):

```powershell
$env:APEX_CANONICAL_CH_PASSWORD = "<local-secret>"
.\dev\scripts\e2e_canonical.ps1 -StartDev
```

The command uses the plugin path, OTLP Collector, canonical ClickHouse tables
and deterministic assertions. Details and the latest sanitized result are in
[`docs/e2e/CANONICAL_GATE.md`](docs/e2e/CANONICAL_GATE.md).

## Repo conventions

- **Monorepo, directory-per-stage.** Each dir has its own build file (`build.sbt`, `pyproject.toml`, `docker-compose.yml`).
- **Branch per task, not per stage.** Short-lived `dir/task` branches → merge to a green `main`. (See [PIPELINE.md](PIPELINE.md) § Workflow rules.)
- **The contract is law.** [`contract/`](contract/) holds the schema, DDL, and `sample_event.json` fixture. Obey the field names exactly.

## Status

The V1 backbone is no longer a scaffold. DEV, JAR, COLLECT, INFRA, the
deterministic ENGINE, read-only SERVE and the canonical six-lane E2E gate are
merged into `feat/base-project-e2e`. The two remaining review items are the
gated Crew/Judge extension and the safe MCP knowledge/proposal extension.

**Review branch:** `base-project-e2e-augusto` consolidates the two pending
extensions and their C9 evidence without merging them into the Luan-owned base.
It also contains the local cross-lane compatibility fix `52a36da`; this is
validated by tests but still needs one fresh Docker-backed canonical rerun.

| Status | Delivery | Reference |
|---|---|---|
| Merged | V1 architecture and contracts | [#45](https://github.com/luanmorenommaciel/apex/pull/45) |
| Merged | DEV, JAR, COLLECT and INFRA | [#47](https://github.com/luanmorenommaciel/apex/pull/47), [#50](https://github.com/luanmorenommaciel/apex/pull/50), [#49](https://github.com/luanmorenommaciel/apex/pull/49), [#48](https://github.com/luanmorenommaciel/apex/pull/48) |
| Merged | Deterministic ENGINE and read-only SERVE | [#46](https://github.com/luanmorenommaciel/apex/pull/46), [#44](https://github.com/luanmorenommaciel/apex/pull/44) |
| Merged | Canonical six-lane E2E | [#51](https://github.com/luanmorenommaciel/apex/pull/51) |
| Consolidated review branch | Gated Crew/Judge, safe MCP proposal and C9 evidence | [`base-project-e2e-augusto`](https://github.com/luanmorenommaciel/apex/tree/base-project-e2e-augusto) |
| Closed without merge | Original ENGINE, SERVE and C9 review PRs | [#52](https://github.com/luanmorenommaciel/apex/pull/52), [#53](https://github.com/luanmorenommaciel/apex/pull/53), [#54](https://github.com/luanmorenommaciel/apex/pull/54) |

Read the [C9 delivery checkpoint](docs/convergence/C9-ENGINE-SERVE-DELIVERY-STATUS-2026-07-24.md)
for accepted behavior, evidence, safety boundaries and the required final
integration gate after Commander-approved integration.

For the exact state of this Augusto-owned branch, including what is verified
locally versus what still depends on Docker and Commander review, read the
[C10 readiness checkpoint](docs/convergence/C10-AUGUSTO-E2E-READINESS-2026-07-24.md).
