# Synthetic Problem Workloads

Deliberately misbehaving Spark jobs that produce **ground truth** for the diagnostic
detectors (design D-007). Each workload forces one reproducible pathology at local
single-machine scale, so detector thresholds in `src/config/diagnostics.yaml` can be
calibrated against runs that are known to be unhealthy.

| Script | App name | Pathology | How it is forced |
|--------|----------|-----------|------------------|
| `skew_join.py` | `workload-skew` | Task-duration skew | One hot key owns ~90% of 5M fact rows; sort-merge join over a fixed 24 shuffle partitions with broadcast and all AQE mitigation (skew-join split, coalescing) disabled → one straggler task. |
| `shuffle_heavy.py` | `workload-shuffle` | Shuffle spill | 2M rows with a 224-char payload and near-unique keys aggregated + sorted into only 4 reduce partitions with `spark.memory.fraction=0.2` → memory/disk spill, hundreds of MiB shuffled. |

Both materialize through the `noop` sink: full computation, no storage side effects.
Runs are deterministic (hash-based key/payload generation, no unseeded randomness) and
target < ~3 minutes each on a laptop-class machine with the default one-worker stack.

## How to run

With the Compose stack up (`make compose`):

```bash
make workload-skew        # once the Make targets from the design land
make workload-shuffle
```

Or manually, mirroring the sample scripts:

```bash
docker exec -it spv0-spark-master \
  env PYTHONPATH=/opt/spark/src /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  --conf spark.executorEnv.PYTHONPATH=/opt/spark/src \
  /opt/spark/src/workloads/skew_join.py   # or shuffle_heavy.py
```

Then `make spark-logs` to load the event logs into ClickHouse and run diagnostics.

## How to tune

All parameters live in `catalog.py` (dataclasses `SkewJoinParams`,
`ShuffleHeavyParams`) — the scripts contain no tuning knobs. Two ways to adjust:

1. **Env vars** (per run, no code change): `WORKLOAD_<FIELD>` overrides any field,
   cast to the field's type. Examples:

   ```bash
   WORKLOAD_ROWS=10000000 make workload-skew            # bigger straggler
   WORKLOAD_HOT_KEY_RATIO=0.95 make workload-skew       # more extreme skew
   WORKLOAD_PAYLOAD_REPEAT=10 make workload-shuffle     # wider rows, more spill
   WORKLOAD_MEMORY_FRACTION=0.1 make workload-shuffle   # starve memory harder
   ```

2. **Catalog defaults** (permanent recalibration for A-004): edit the dataclass
   defaults in `catalog.py`. The `spark_conf()` methods hold the deliberately bad
   session settings (AQE off, `autoBroadcastJoinThreshold=-1`, fixed shuffle
   partitions, shrunken memory fraction) — keep those intact or the pathologies
   get optimized away by Spark itself.

If a workload stops tripping its detector, the usual fixes are: raise `rows` /
`payload_repeat` (more data per task) or lower `memory_fraction` (shuffle_heavy)
before touching detector thresholds.
