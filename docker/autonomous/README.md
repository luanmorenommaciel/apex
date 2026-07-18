# Apex Autonomous Docker Stack

This folder contains a standalone Docker proposal for running the Apex Spark
diagnostic loop without relying on the local `spark-plat-v0-*` images.

The existing root `docker-compose.yml` is intentionally preserved. This module
adds a parallel compose file:

```powershell
docker compose -f docker-compose.autonomous.yml build
docker compose -f docker-compose.autonomous.yml up -d
docker compose -f docker-compose.autonomous.yml ps
```

## Services

| Service | Image/build source | Purpose |
|---|---|---|
| `clickhouse` | `clickhouse/clickhouse-server:26.5.1` | Apex telemetry store with `docs/specs/apex_telemetry_v1.sql` mounted at init. |
| `minio` | `quay.io/minio/minio:RELEASE.2025-09-07T16-13-09Z` | S3-compatible Spark event log storage. |
| `minio-init` | `quay.io/minio/mc:RELEASE.2025-08-13T08-35-41Z` | Explicitly creates `spark-logs` and the `events/` prefix marker. |
| `spark-master` | local `docker/autonomous/spark/Dockerfile` | Spark 4.1.2 master with S3A jars and official Apex listener path. |
| `spark-worker` | local `apex-autonomous-spark:4.1.2-s3a` | 8-core Spark 4.1.2 worker for real skew validation. |

## Ports

The autonomous stack uses separate host ports so it can run next to an existing
`spv0` or root Apex stack:

| Component | Host port | Container port |
|---|---:|---:|
| Spark master RPC | `37077` | `7077` |
| Spark master UI | `38080` | `8080` |
| Spark worker UI | `38081` | `8081` |
| ClickHouse HTTP | `38123` | `8123` |
| ClickHouse native | `39000` | `9000` |
| MinIO API | `39001` | `9000` |
| MinIO console | `39002` | `9001` |

Inside the Docker network, Spark still writes event logs to:

```text
s3a://spark-logs/events
```

The Apex listener is mounted and loaded by default:

```text
/opt/apex/listener/apex-spark-listener-0.1.0.jar
spark.extraListeners apex.commander.spark.ApexSparkListener
spark.apex.listener.output /tmp/apex-listener-events.ndjson
```

## Validation Commands

Start clean:

```powershell
docker compose -f docker-compose.autonomous.yml down -v
docker compose -f docker-compose.autonomous.yml build
docker compose -f docker-compose.autonomous.yml up -d
docker compose -f docker-compose.autonomous.yml ps
```

Check ClickHouse:

```powershell
docker exec apex-autonomous-clickhouse clickhouse-client --user spv0 --password spv0 --query "SELECT 1"
```

Check MinIO bucket:

```powershell
docker exec apex-autonomous-minio-init /bin/sh -lc "mc alias set apex http://minio:9000 spv0 spv0spv0 && mc ls apex/spark-logs"
```

Submit a minimal Spark job:

```powershell
docker exec apex-autonomous-spark-master /opt/spark/bin/spark-submit `
  --master spark://spark-master:7077 `
  --conf spark.eventLog.enabled=true `
  --conf spark.eventLog.dir=s3a://spark-logs/events `
  /opt/spark/examples/src/main/python/pi.py 10
```

Confirm an event log was written:

```powershell
docker exec apex-autonomous-minio-init /bin/sh -lc "mc alias set apex http://minio:9000 spv0 spv0spv0 && mc find apex/spark-logs/events"
```

## Current Status

This module is aligned to the Commander decision that Spark 4.1.2 is the target
runtime. Compose rendering is validated in
`evidence/f7-spark412-official-listener-compose-autonomous-2026-07-18.log`.

Known validation points before declaring the gap fully closed:

- close CODEX-041: the Spark 4.1.2 image resolves, but the Maven download of
  the AWS SDK bundle for S3A timed out during this pass;
- confirm `hadoop-aws` and `aws-java-sdk-bundle` versions are compatible with
  the Spark/Hadoop runtime in the base image;
- run the G3 skew job and verify event log capture in MinIO;
- rerun G5 after the real job proves this stack is equivalent to the validated
  Spark 4.1.2 platform.

If any public image tag is unavailable, pin the nearest approved tag here rather
than falling back to the old `spark-plat-v0-*` images.
