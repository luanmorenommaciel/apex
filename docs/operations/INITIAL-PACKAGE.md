# Apex initial package - operator runbook

## Prerequisites

- Windows 10/11 with PowerShell 7;
- Docker Desktop using Linux containers, with at least 4 CPUs and 8 GB RAM;
- Python 3.11+ and `uv`;
- free ports from the local `.apex/*.env` configuration.

Host Java, Scala and sbt are not required. The Docker build compiles the
official Spark 4.1.2 JAR in a pinned build stage.

## First installation

From the repository root:

```powershell
.\scripts\apex.ps1 bootstrap
```

The first run:

1. generates local service secrets under ignored `.apex/`;
2. builds the Spark 4.1.2 image and `apex_41` JAR cell;
3. starts canonical INFRA, redacting COLLECT and DEV;
4. applies additive ClickHouse migrations;
5. waits for the long-running components;
6. prints `APEX_DOCTOR=ready` only after all checks pass.

Do not delete `.apex/` while retaining the corresponding Docker volumes:
those files hold the local service credentials used to initialize the data.

## First product proof

```powershell
.\scripts\apex.ps1 smoke
```

This runs one real `skew_join`, validates all six lanes and calls all four MCP
tools. On a 4-CPU Docker Desktop, the first execution can take 20-25 minutes
because it materializes five million deterministic Delta rows. A successful
run ends with:

```text
APEX_PRODUCT_GATE=passed job_id=app-...
```

It does not invoke CrewAI or an external LLM. `suggest_fix` returns a proposal
with `applied=false` and requires human approval.

## Daily operation

```powershell
.\scripts\apex.ps1 status
.\scripts\apex.ps1 doctor
.\scripts\apex.ps1 smoke
.\scripts\apex.ps1 down
```

`down` stops the package and preserves named volumes. `bootstrap -SkipBuild`
is the fast restart path when no JAR, Dockerfile or dependency changed.

## Full engineering gate

```powershell
.\scripts\apex.ps1 e2e
```

The reference local validation on 2026-07-25 completed all four canonical
pathologies (`skew_join`, `spill`, `bad_shuffle`, `driver_oom`) and ended with
`APEX_PRODUCT_GATE=passed`. See
[`C12-INITIAL-PACKAGE-VALIDATION-2026-07-25.md`](../convergence/C12-INITIAL-PACKAGE-VALIDATION-2026-07-25.md)
for the fresh application IDs and measured evidence.

This runs `skew_join`, `spill`, `bad_shuffle` and `driver_oom`, followed by the
deterministic six-lane and MCP gates. Use it before a release or integration
decision, not as the normal developer startup.

## Local endpoints

The generated values in `.apex/*.env` are authoritative. Defaults include:

| Component | URL |
|---|---|
| HyperDX | `http://127.0.0.1:8090` |
| ClickHouse HTTP | `http://127.0.0.1:8123` |
| Collector health | `http://127.0.0.1:13133` |
| Spark master UI | `http://127.0.0.1:18081` |
| Spark History Server | `http://127.0.0.1:28080` |
| MinIO console | `http://127.0.0.1:19001` |

## Failure guide

| Symptom | Meaning | Action |
|---|---|---|
| `Docker Desktop engine is not available` | daemon is stopped | start Docker Desktop and repeat |
| port bind error | another local stack owns a port | change only the host port in the relevant ignored `.apex/*.env` |
| ClickHouse credential mismatch | runtime config and retained volume differ | restore the `.apex` files that initialized the volume; do not rotate blindly |
| History Server `403` | Spark and MinIO credentials differ | rerun `bootstrap`; generated Spark defaults must remain mounted |
| collector unhealthy | OTLP path is unavailable | inspect `docker logs apex-otel-collector`; Spark remains fail-safe |
| smoke takes longer on first run | Delta data is being materialized | observe CPU and wait; later runs reuse committed data |
| MCP gate fails | telemetry or findings are missing/inconsistent | use the reported `job_id`, then run `doctor` and inspect the six-lane output |

## Security

- Never add API keys to `.apex/*.env`.
- External Judge credentials are provided only in the operator process that
  explicitly runs that separate smoke.
- Do not upload Docker environment dumps as evidence.
- Share only the sanitized C12 report, not runtime files or raw credentials.
