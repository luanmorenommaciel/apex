# Apex initial package - approved design

## Goal

Give the team one Windows entry point that installs and verifies the existing
six lanes without replacing their Compose files or contracts.

## Commands

| Command | Responsibility |
|---|---|
| `bootstrap` | create local configuration, build Spark 4.1.2, start the lanes, migrate and run `doctor` |
| `doctor` | verify containers, endpoints, schema and Spark 4.1.2 configuration |
| `smoke` | run `skew_join`, the six-lane gate and all four MCP tools |
| `e2e` | run all four real pathologies, then the six-lane and MCP gates |
| `status` | show component state without changing it |
| `down` | stop the package while preserving persistent volumes |

## Composition

The package is an orchestrator, not a seventh implementation:

1. INFRA starts canonical ClickHouse, MongoDB and HyperDX.
2. COLLECT starts its queue and redacting collector, connected to INFRA.
   Its lane-local throwaway ClickHouse is not started.
3. DEV builds the Spark 4.1.2 image, including the official JAR cell, and
   joins the collector network.
4. ENGINE and SERVE remain local Python packages invoked by the gates.

## Secrets

Runtime configuration lives under ignored `.apex/*.env` files. On first
bootstrap the package generates independent ClickHouse, HyperDX, redaction and
MinIO secrets using a cryptographic random generator. Existing files are never
overwritten. If a canonical ClickHouse container already owns a persistent
volume, its local service credential is adopted silently instead of being
rotated behind the volume. External LLM keys are not requested, generated or
persisted.

The package also renders an ignored `.apex/spark-defaults.conf` and mounts it
through `dev/docker-compose.package.yml`. Its S3A credentials match the
generated MinIO account; committed Spark defaults never receive a secret.

## Safety boundaries

- No command deletes named volumes.
- No command changes source code or creates a pull request.
- `suggest_fix` remains a proposal with `applied=false`.
- `bootstrap` and `doctor` never call an external LLM.
- Full Docker CI is manual and requires an operator-owned self-hosted runner.

## Acceptance

- A dry run works without Docker and does not create local configuration.
- `bootstrap` reaches a healthy Spark 4.1.2, collector and canonical store.
- `smoke` produces one fresh `job_id`, deterministic findings and a passing
  real MCP stdio gate.
- Tests verify the command contract and secret-handling invariants.
