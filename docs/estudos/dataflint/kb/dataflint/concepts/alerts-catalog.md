# Alerts Catalog

> **Purpose**: The OFFICIAL DataFlint performance alerts — what each one means, what to verify against the real metric, and which Spark specialist owns the fix
> **Confidence**: 0.95
> **MCP Validated**: Full-source validation 2026-06-22 (GitHub README + GitBook docs + dataflint.io)
> **Source**: dataflint.gitbook.io/dataflint-for-spark/advanced/alerts

## Overview

DataFlint's core value is turning raw stage/task metrics into **named** alerts. Each alert
is a *candidate*, not a verdict: DataFlint reads metrics that already exist and flags a
recognizable pattern. You must confirm the alert against the actual Spark UI / event-log
metric before acting — a "small files" flag on a deliberately tiny dev dataset is a
false positive. Routing each alert to the right specialist is covered in
[../patterns/alert-triage-routing.md](../patterns/alert-triage-routing.md).

## The Catalog (shipped alerts)

| Alert | What it means | Route to |
|-------|---------------|----------|
| **Reading Small Files** | Reads scan many tiny files (also works for Apache Iceberg tables) → IO overhead | `spark-specialist` |
| **Writing Small Files** | The sink emits many tiny output files | `spark-specialist` |
| **Apache Iceberg – inefficient replace of data** | Iceberg overwrite rewrites far more data than needed | `spark-specialist` |
| **Partition Skew** | One partition/task ≫ the rest, stalling the stage | `spark-skew-specialist` |
| **Large Number Of Small Tasks** | Too many tiny tasks → scheduler overhead | `spark-shuffle-specialist` |
| **Memory Over-Provisioning** | Executors hold far more memory than used → waste | `spark-manager-specialist` |
| **Memory Under-Provisioning** | Too little memory → spill / GC / OOM risk | `spark-manager-specialist` |
| **High wasted cores rate** | Allocated cores idle relative to work done | `spark-manager-specialist` |
| **Large Data Broadcast** | A broadcast is large → driver/executor memory pressure | `spark-shuffle-specialist` |
| **Broadcast small table in Sort Merge Join** | A small table went through SMJ instead of being broadcast | `spark-shuffle-specialist` |
| **Large Cross Join Scan** | A cross join scans a large input → blow-up | `spark-shuffle-specialist` |
| **Large Partition Size** | Individual partitions are oversized → spill/skew risk | `spark-specialist` |
| **Long Filter Conditions** | Filter predicate string is long/truncated in the plan | `spark-specialist` |
| **Query Failures** | A query failed; DataFlint extracts the error from the JVM stack trace and pinpoints the failing node on the logical plan | `spark-troubleshooter` |

> **Long Filter Conditions tip**: set `spark.sql.maxMetadataStringLength=1000` so Spark
> logs the full filter condition untruncated (native Spark config). See
> [../specs/dataflint-config-schema.yaml](../specs/dataflint-config-schema.yaml).

## Alerts Roadmap (NOT yet shipped)

These are announced but not yet released — do **not** assume they fire today:

- High task error rate
- High executors error rate
- High disk spill relative to input size and available memory
- Repartition before write with low cardinality causing lack of parallelism or huge files
- Executor memory overhead too low causing container failure

## How to Read an Alert (discipline)

1. **Name** — DataFlint tells you *which* pattern (e.g. "Reading Small Files").
2. **Locate** — open the corresponding Spark UI tab / event-log metric it derived it from.
3. **Confirm** — does the real metric support the alert at *production* data scale?
4. **Decide** — real → route to the owning specialist; false positive (e.g. dev-scale
   dataset) → note and ignore.
5. **Never** apply a config change purely because an alert lit up — that is cargo-cult
   tuning and can regress performance.

> **Diagnose-only reminder**: DataFlint does not apply any of these fixes. It surfaces the
> candidate; the specialist applies and verifies the change. See
> [plugin-architecture.md](plugin-architecture.md).

## Why Confirmation Matters (false positives)

| Alert fires on | Why it can be false | Confirm by |
|----------------|---------------------|------------|
| Tiny dev/sample dataset | Small files/partitions are *expected* at that scale | Re-check at production volume |
| First/cold run | Skew may be a one-off data quirk | Compare across multiple runs (SHS forensics) |
| Intentional `coalesce(1)` write | "Writing Small Files" is by design | Check the job's write intent |

## Related

- [what-is-dataflint.md](what-is-dataflint.md)
- [plugin-architecture.md](plugin-architecture.md)
- [../patterns/alert-triage-routing.md](../patterns/alert-triage-routing.md)
- [../patterns/install-history-server.md](../patterns/install-history-server.md)
