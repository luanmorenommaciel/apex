# What Is DataFlint

> **Purpose**: What the DataFlint OSS plugin is — "Spark Performance Made Simple", a drop-in replacement for the Apache Spark UI that adds named performance alerts — its diagnose-only nature, OSS vs SaaS, and its Spark/Scala requirements
> **Confidence**: 0.95
> **MCP Validated**: Full-source validation 2026-06-22 (GitHub README + GitBook docs + dataflint.io)

## Overview

DataFlint is an open-source (**Apache-2.0**) "drop-in replacement for the Apache Spark UI",
tagged "Spark Performance Made Simple". It is not a separate UI server and not a tuning
engine — it is a Spark **plugin** that, once registered, adds a **DataFlint** view to the
*existing* Spark UI and raises named, human-readable performance alerts. It reads the same
event/metric stream the Spark UI already renders — see
[plugin-architecture.md](plugin-architecture.md).

> **DataFlint DIAGNOSES; it does not fix.** It surfaces *candidates*. The actual fix is a
> config or code change applied by the relevant Spark specialist (shuffle / skew /
> manager / etc.). See [alerts-catalog.md](alerts-catalog.md) and
> [../patterns/alert-triage-routing.md](../patterns/alert-triage-routing.md).

## Official Features (6)

1. **Real-time query and cluster status**
2. **Query breakdown** with a performance heat map
3. **Application Run Summary**
4. **Performance alerts and suggestions** (the named alerts — see [alerts-catalog.md](alerts-catalog.md))
5. **Identify query failures** (error pulled from the JVM stack trace, failing node pinpointed)
6. **Spark AI Assistant**

## Where It Runs

DataFlint works in two scopes — both read the same Spark metrics, live or replayed:

| Scope | What it reads | Use case | Pattern |
|-------|---------------|----------|---------|
| **Live driver UI** | The running job's metric stream | Dev/active job, tab at `:4040` → DataFlint | [../patterns/install-pyspark-session.md](../patterns/install-pyspark-session.md) |
| **Spark History Server** | Replayed event logs (offline) | Post-mortem of finished runs from MinIO | [../patterns/install-history-server.md](../patterns/install-history-server.md) |

The History Server scope is the highest-value path for this repo: it analyses already-
finished jobs from the event logs in MinIO without re-running anything.

## OSS vs SaaS — Two Different Products

| | **OSS plugin** (this KB) | **SaaS / cloud platform** |
|--|--------------------------|---------------------------|
| What | In-process Spark plugin, local UI tab | "Production-Aware AI Agents for Apache Spark" |
| Data | Stays in-process; nothing external when telemetry off | Sends operational metadata externally |
| Opt-in | Two configs (`spark.plugins` + package) | Separate explicit sign-up |
| This platform | Default path; safe | Must **not** be enabled without explicit authorization |

The SaaS product is a **Spark MCP server** feeding **4 agents**:
- **Agentic Spark Copilot** in the IDE (Cursor / VS Code / IntelliJ)
- **Cluster Agent** for real-time right-sizing
- **Review Agent** for catching PR regressions
- **Fleet Observability** dashboard

It is **SOC 2 Type II**, and it analyses Spark **logs** (operational metadata), **not**
business data.

> **Security note**: the OSS plugin runs locally and adds no new data collection (with
> telemetry off). Enabling the SaaS/external product = sending operational metadata
> externally — treat it as a **CRITICAL (0.98)** authorization decision on this platform.
> See [plugin-architecture.md](plugin-architecture.md) for the clean-removal contract.

## Requirements

| Requirement | Value | Note |
|-------------|-------|------|
| Spark | **3.0 – 4.0** | README says "3.2 and up"; supported-versions page lists 3.0–4.0. This repo: 3.5.6 |
| Scala | **2.12 or 2.13** | Must match the Spark build's Scala (see below) |
| Modes | **batch + streaming** | Both supported |
| Spark 4.x | Separate artifact | `io.dataflint:dataflint-spark4_2.13` line |

> The **#1 install failure** is a Scala/Spark mismatch — pick the package matching your
> Spark build's Scala (`spark-submit --version` banner prints it). Default Spark 3.5
> builds ship **Scala 2.12**. Full matrix in
> [package-version-matrix.md](package-version-matrix.md).

## What It Is Not

| Misconception | Reality |
|---------------|---------|
| A profiler/tuner that fixes jobs | Diagnose-only; it never changes the query plan or execution |
| A separate UI server to deploy | A plugin that augments the existing Spark UI |
| Always-on external monitoring | OSS is in-process; external egress is the *separate* SaaS |
| A verdict engine | It flags candidates — confirm each against the real metric before acting |

## Related

- [plugin-architecture.md](plugin-architecture.md)
- [alerts-catalog.md](alerts-catalog.md)
- [package-version-matrix.md](package-version-matrix.md)
- [../patterns/install-pyspark-session.md](../patterns/install-pyspark-session.md)
- [../patterns/install-history-server.md](../patterns/install-history-server.md)
