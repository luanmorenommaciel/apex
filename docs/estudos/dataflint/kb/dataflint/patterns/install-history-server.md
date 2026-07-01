# Install on the Spark History Server (Offline / Post-Mortem)

> **Purpose**: Wire DataFlint into the Spark History Server classpath so it analyses finished runs from event logs in MinIO — classpath + restart + the eventLog/history dir-match prerequisite
> **MCP Validated**: Full-source validation 2026-06-22 (GitHub README + GitBook docs + dataflint.io)

## When to Use

- Jobs already finished; you want DataFlint to analyse runs from event logs in MinIO
- The highest-value path for this repo — post-mortem with **no re-run**. Pairs with the
  `spark-history-specialist` (event-log storage) and the tuning specialists (the fix).

DataFlint is a **file-system plugin** loaded into the History Server: it adds the DataFlint
UI when a Spark app is loaded from logs.

## Prerequisites (must already be true for DataFlint to have data)

```properties
spark.eventLog.enabled            true
spark.eventLog.dir                s3a://<bucket>/spark-events     # MinIO, set on jobs
spark.history.fs.logDirectory     s3a://<bucket>/spark-events     # MUST match eventLog.dir
```

> An **empty DataFlint-on-SHS view ≈ an empty SHS**: almost always an `eventLog.dir` vs
> `history.fs.logDirectory` mismatch, or MinIO `s3a` credentials/endpoint. Diagnose the
> storage wiring first via the spark-history KB (`patterns/diagnose-empty-shs.md`) and the
> `spark-history-specialist` — DataFlint cannot show data the SHS itself cannot read.

> Local SHS replay needs **Java 8 or 11** + `SPARK_HOME` set.

## Install Steps

1. **Download the matching-Scala jar** to the SHS machine (e.g. `spark_2.12-0.9.9.jar`) —
   the SHS does **NOT** support Apache Ivy / package loading (unlike a live app), so you
   **MUST** download the jar manually. See
   [../concepts/package-version-matrix.md](../concepts/package-version-matrix.md).
2. Add it to the History Server classpath — either:
   - set `SPARK_DAEMON_CLASSPATH=/path/spark_2.12-0.9.9.jar`, **or**
   - drop the jar in `$SPARK_HOME/jars/` (auto-loaded).
3. Restart the History Server.
4. Open a completed application → the **DataFlint** view renders from the replayed log.

```bash
# Option A: drop the jar into the jars dir (auto-loaded; rebuild the SHS image on K8s)
cp spark_2.12-0.9.9.jar "$SPARK_HOME/jars/"

# Option B: classpath env var (e.g. in the SHS Deployment / Helm values)
export SPARK_DAEMON_CLASSPATH="/path/spark_2.12-0.9.9.jar"

# Restart the history server daemon
"$SPARK_HOME/sbin/stop-history-server.sh" && "$SPARK_HOME/sbin/start-history-server.sh"
```

> **No Ivy/packages on the SHS** — there is no `spark.jars.packages` Maven resolution at
> SHS load time. The jar must be physically on the classpath.

> **Persistent history servers are NOT supported** (Databricks, EMR-persistent) — they
> cannot load custom providers. See the platform matrix in
> [../concepts/package-version-matrix.md](../concepts/package-version-matrix.md).

## Kubernetes Note

On K8s the SHS is a Deployment. Bake the jar into the SHS image (Option A) or mount it and
set `SPARK_DAEMON_CLASSPATH` via the Deployment/Helm values (Option B). Do not depend on
runtime Maven resolution. Coordinate with
[install-on-kubernetes.md](install-on-kubernetes.md) and the `spark-history-specialist`.

## Verify

1. After restart, open the SHS UI (default `:18080`).
2. Open a finished app → confirm a **DataFlint** view renders alongside the replayed UI.
3. Empty view → run the empty-SHS triage (dir match + `s3a` creds) before suspecting
   DataFlint. No DataFlint view but SHS works → suspect a Scala/jar mismatch.

## Pitfalls

| Don't | Do |
|-------|----|
| Try `spark.jars.packages` on the SHS | Download the jar manually — SHS has no Ivy |
| Install on SHS without matching eventLog dirs | Verify `eventLog.dir == history.fs.logDirectory` first |
| Use the wrong Scala jar | Match the SHS Spark build's Scala |
| Forget to restart the daemon | Stop/start the history server after classpath change |
| Expect it on a persistent SHS | Not supported — use a non-persistent SHS |

## See Also

- [install-pyspark-session.md](install-pyspark-session.md)
- [install-on-kubernetes.md](install-on-kubernetes.md)
- [alert-triage-routing.md](alert-triage-routing.md)
- [../concepts/plugin-architecture.md](../concepts/plugin-architecture.md)
- spark-history KB → MinIO/`s3a` event-log wiring (`patterns/eventlog-on-minio.md`)
