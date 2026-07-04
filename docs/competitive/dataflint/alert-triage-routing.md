# Alert Triage → Root Cause → Routing

> **Purpose**: Turn a DataFlint alert into a confirmed root cause and route it to the specialist who owns the fix — the routing table plus the triage discipline that prevents cargo-cult tuning
> **MCP Validated**: Full-source validation 2026-06-22 (GitHub README + GitBook docs + dataflint.io)

## When to Use

- A DataFlint alert appears (live UI or History Server) and you must decide if it is real
- You need to hand a confirmed finding to the right Spark specialist

> **DataFlint names the problem; it does not change your code.** It surfaces *candidates*.
> Confirm the metric, then route. See
> [../concepts/alerts-catalog.md](../concepts/alerts-catalog.md).

## Routing Table (official alert names)

| DataFlint alert | What it means | Likely fix | Route to |
|-----------------|---------------|------------|----------|
| **Reading Small Files** | Scan reads many tiny files (also Iceberg) | Compaction; tune file/split sizing | `spark-specialist` |
| **Writing Small Files** | Sink emits many tiny files | `coalesce`/`repartition` before write; compaction | `spark-specialist` |
| **Apache Iceberg – inefficient replace of data** | Overwrite rewrites too much data | Partition/predicate-scoped replace | `spark-specialist` |
| **Partition Skew** | One partition/task ≫ the rest | AQE `skewJoin` or salting | `spark-skew-specialist` |
| **Large Number Of Small Tasks** | Many tiny tasks, scheduler overhead | Coalesce / lower `shuffle.partitions`; AQE coalescing | `spark-shuffle-specialist` |
| **Memory Over-Provisioning** | Executors over-allocated memory | Right-size executor memory | `spark-manager-specialist` |
| **Memory Under-Provisioning** | Too little memory → spill/GC/OOM | More executor memory / fewer cores per executor | `spark-manager-specialist` |
| **High wasted cores rate** | Allocated cores idle | Right-size cores; dynamic allocation | `spark-manager-specialist` |
| **Large Data Broadcast** | Broadcast large → memory pressure | Lower `autoBroadcastJoinThreshold`; verify build side | `spark-shuffle-specialist` |
| **Broadcast small table in Sort Merge Join** | Small table went through SMJ | Hint/enable broadcast for the small side | `spark-shuffle-specialist` |
| **Large Cross Join Scan** | Cross join scans a large input | Add join keys; avoid cartesian product | `spark-shuffle-specialist` |
| **Large Partition Size** | Oversized partitions → spill/skew | Raise partitions; tune `memory.fraction` | `spark-specialist` |
| **Long Filter Conditions** | Long/truncated filter predicate | Set `spark.sql.maxMetadataStringLength=1000` to log it fully | `spark-specialist` |
| **Query Failures** | Query failed; error pulled from JVM stack trace, failing node pinpointed on logical plan | Diagnose root error (OOM, data, network) | `spark-troubleshooter` |

## Triage Discipline (the important part)

1. **Read the name** — DataFlint tells you the *pattern*, not the verdict.
2. **Open the source metric** — go to the Spark UI tab / event-log metric the alert came
   from (executor cores, stage spill, task duration spread, broadcast size, GC ratio,
   output file count).
3. **Confirm at production scale** — does the metric support the alert on real data, not a
   tiny dev/sample set?
4. **Decide**:
   - Real → route to the owning specialist with the confirming metric attached.
   - False positive → note it and move on (do **not** change config).
5. **Never cargo-cult** — never apply a config change purely because an alert lit up. A
   wrong "fix" can regress performance.

## False-Positive Checklist

| If the alert is | Suspect false positive when | Confirm by |
|-----------------|-----------------------------|------------|
| Reading/Writing Small Files | Dataset is dev/sample-sized | Re-check at production volume |
| Partition Skew | Single cold/first run | Compare across runs (SHS forensics) |
| Writing Small Files | Job intentionally `coalesce(1)` | Check the write intent |
| High wasted cores rate | Short job with startup overhead | Look at steady-state, not warmup |

## Hand-Off Format

When routing, give the specialist:
- The **alert name** (from DataFlint).
- The **confirming metric** (value + where you read it — UI tab or `/api/v1` endpoint).
- The **scope** (live job vs History Server replay) and the app/run id.

> For offline confirmation across many finished runs, pull metrics via the History Server
> REST API (see the spark-history KB `patterns/rest-api-batch-forensics.md`) rather than
> clicking through the UI.

## See Also

- [../concepts/alerts-catalog.md](../concepts/alerts-catalog.md)
- [install-history-server.md](install-history-server.md)
- [../concepts/plugin-architecture.md](../concepts/plugin-architecture.md)
