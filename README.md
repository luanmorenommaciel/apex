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

## Repo conventions

- **Monorepo, directory-per-stage.** Each dir has its own build file (`build.sbt`, `pyproject.toml`, `docker-compose.yml`).
- **Branch per task, not per stage.** Short-lived `dir/task` branches → merge to a green `main`. (See [PIPELINE.md](PIPELINE.md) § Workflow rules.)
- **The contract is law.** [`contract/`](contract/) holds the schema, DDL, and `sample_event.json` fixture. Obey the field names exactly.

## Status

Scaffold. Stages are empty dirs with briefs in [docs/lanes/](docs/lanes/). First commit target: freeze the contract, then a tracer bullet through all six.
