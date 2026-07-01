# DataFlint Knowledge Base

> **Purpose**: The DataFlint open-source plugin — "Spark Performance Made Simple", a drop-in replacement for the Apache Spark UI that adds named performance alerts. Covers the 6 features, the plugin model (`spark.plugins`), `io.dataflint` artifact/Scala selection (incl. spark4 + Databricks lines), live + K8s Spark Operator + Spark History Server install on MinIO/`s3a://` (Spark 3.5.x), the 14 official alerts, alert triage, and routing fixes to the right Spark specialist. DataFlint DIAGNOSES; the specialists FIX.
> **MCP Validated**: Full-source validation 2026-06-22 (GitHub README + GitBook docs + dataflint.io)
> **Sources**: github.com/dataflint/spark · dataflint.gitbook.io/dataflint-for-spark (each page also has a `.md`; an `llms.txt` index exists) · www.dataflint.io · Maven Central `io.dataflint`

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/what-is-dataflint.md](concepts/what-is-dataflint.md) | Drop-in Spark UI replacement, 6 features, diagnose-only nature, OSS plugin vs SaaS AI-agents platform, requirements (Spark 3.0–4.0, Scala 2.12/2.13, batch+streaming) |
| [concepts/plugin-architecture.md](concepts/plugin-architecture.md) | `spark.plugins` / `SparkPlugin` hook, in-process, no new ports, fails-safe, ~1s polling, MixPanel telemetry, clean removal |
| [concepts/alerts-catalog.md](concepts/alerts-catalog.md) | The 14 official alerts (+ roadmap) — what each means, what to verify, who fixes it |
| [concepts/package-version-matrix.md](concepts/package-version-matrix.md) | Artifact × Scala × Spark selection incl. spark4 + Databricks lines, supported versions, platform realtime/SHS matrix |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/install-pyspark-session.md](patterns/install-pyspark-session.md) | Live install — PySpark builder + spark-submit, telemetry off |
| [patterns/install-history-server.md](patterns/install-history-server.md) | SHS classpath + restart + eventLog/history dir match on MinIO (offline post-mortem) |
| [patterns/install-on-kubernetes.md](patterns/install-on-kubernetes.md) | Official Spark Operator manifest (`deps.packages` + ivy cache), jar baking vs `spark.jars`, manual-jar for egress-blocked pods |
| [patterns/alert-triage-routing.md](patterns/alert-triage-routing.md) | Alert → root cause → specialist routing table + triage discipline |

### Specs (Machine-Readable)

| File | Purpose |
|------|---------|
| [specs/dataflint-config-schema.yaml](specs/dataflint-config-schema.yaml) | Every `spark.plugins` (DataFlint value) + `spark.dataflint.*` config: default, type, allowed values, note |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) - Install snippets (live + SHS), config table, alert→specialist, version/Scala matrix, pitfalls

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Plugin model** | Activated by `spark.plugins=io.dataflint.spark.SparkDataflintPlugin`; in-process, no daemon, no new ports |
| **Diagnose-only** | Reads the same metrics the Spark UI uses; never alters query plans or execution; fails safe |
| **OSS vs SaaS** | OSS is in-process/local; the SaaS is a "Production-Aware AI Agents for Spark" platform (MCP + 4 agents, SOC 2 Type II) that egresses operational metadata (separate opt-in) |
| **Scala match** | `io.dataflint:spark_2.12` vs `_2.13` MUST match the Spark build's Scala (#1 install failure) |
| **Two scopes** | Live driver UI (`:4040`) and Spark History Server (offline; NOT on persistent SHS) |
| **Alert → route** | 14 official alerts; confirm the metric, then route to the owning specialist |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Beginner** | concepts/what-is-dataflint.md, concepts/plugin-architecture.md |
| **Intermediate** | concepts/package-version-matrix.md, patterns/install-pyspark-session.md |
| **Advanced** | concepts/alerts-catalog.md, patterns/install-history-server.md, patterns/install-on-kubernetes.md, patterns/alert-triage-routing.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| dataflint-specialist | All files | DataFlint install (live + SHS on MinIO/K8s), package selection, alert triage + routing |
| spark-history-specialist | patterns/install-history-server.md | Hand-off for event-log storage wiring when the SHS / DataFlint view is empty |
| spark-shuffle-specialist | concepts/alerts-catalog.md, patterns/alert-triage-routing.md | Fixes partition-size / spill / broadcast alerts |
| spark-skew-specialist | concepts/alerts-catalog.md, patterns/alert-triage-routing.md | Fixes skewed-stage / straggler alerts |
| spark-manager-specialist | patterns/install-on-kubernetes.md, patterns/alert-triage-routing.md | Image/jar baking; fixes idle-cores / GC alerts |
