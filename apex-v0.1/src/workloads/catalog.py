"""
Typed catalog of synthetic-workload parameters (design decision D-007).

All tuning for the problem workloads lives here — the runner scripts in
this package never hard-code row counts, ratios, or Spark confs. This is
deliberate: assumption A-004 says skew/spill reproduction at local
single-machine scale may need calibration, and calibration should be a
data edit (or an env var), not a code change.

Environment overrides
---------------------
Every dataclass field can be overridden with `WORKLOAD_<FIELD_NAME>`
(upper-cased field name), e.g.:

    WORKLOAD_ROWS=1000000 make workload-skew
    WORKLOAD_PAYLOAD_REPEAT=4 WORKLOAD_ROWS=3000000 make workload-shuffle

Values are cast to the type of the field's default (int/float/str).
Both workloads share the env-var namespace; only one workload runs per
spark-submit, so there is no ambiguity in practice.

Sizing rationale (defaults, one worker with 1 core / 1g memory)
---------------------------------------------------------------
- skew_join: 5M fact rows, one hot key owning ~90% of them, joined over
  a fixed 24 shuffle partitions with AQE skew mitigation off. The hot
  partition sorts/joins ~4.5M rows (tens of seconds) while the other 23
  partitions get ~20k rows each (sub-second) -> max/p50 task-duration
  ratio far above the critical threshold of 6, with >= 8 tasks and a
  max task duration well above 5s.
- shuffle_heavy: 2M rows carrying a 224-char payload (~480 MB of
  shuffle) aggregated over near-unique keys into only 4 reduce
  partitions with spark.memory.fraction=0.2. Each reduce task must hold
  ~120 MB serialized (more in-memory) against a ~145 MB unified memory
  pool -> hash-aggregate + sort spill to memory/disk, and stage shuffle
  bytes are far above the 16 MiB detector guard.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, fields, replace
from typing import Any, TypeVar, Union

ENV_PREFIX = "WORKLOAD_"

ParamsT = TypeVar(
    "ParamsT",
    "SkewJoinParams",
    "ShuffleHeavyParams",
    "GcChurnParams",
    "OomVictimParams",
    "CrossJoinParams",
    "CacheHeavyParams",
)


@dataclass(frozen=True)
class SkewJoinParams:
    """Parameters for the deterministic hot-key join workload (skew_join.py)."""

    rows: int = 12_000_000  # fact-side row count; sized so the hot task exceeds the 5s skew guard (calibrated 2026-07-06)
    dim_rows: int = 150_000  # dimension rows; large enough to never be broadcast
    hot_key_ratio: float = 0.90  # share of fact rows owned by the single hot key (1% granularity)
    hot_key: int = 0  # join key that receives the hot share; must exist in the dimension
    payload_repeat: int = 1  # payload width = 32 chars (md5) * payload_repeat
    input_partitions: int = 8  # partitions used by spark.range generation
    shuffle_partitions: int = 24  # fixed so the hot partition is one straggler task among 24
    seed: int = 42  # reserved for future random generators; current generation is hash-based

    def spark_conf(self) -> dict[str, Any]:
        """Session extra_conf that makes the skew observable instead of mitigated."""
        return {
            # Force a shuffle (sort-merge) join: never broadcast the dimension.
            "spark.sql.autoBroadcastJoinThreshold": -1,
            # Keep exactly `shuffle_partitions` reduce tasks so the detector
            # sees >= 8 tasks and one dominant straggler.
            "spark.sql.shuffle.partitions": self.shuffle_partitions,
            # AQE would split the hot partition (skew join) or merge the tiny
            # ones (coalescing), hiding the ground-truth pathology. Disable
            # the whole adaptive layer plus the specific features for clarity.
            "spark.sql.adaptive.enabled": False,
            "spark.sql.adaptive.skewJoin.enabled": False,
            "spark.sql.adaptive.coalescePartitions.enabled": False,
        }


@dataclass(frozen=True)
class ShuffleHeavyParams:
    """Parameters for the wide-payload spilling aggregation workload (shuffle_heavy.py)."""

    rows: int = 2_000_000  # generated row count
    distinct_key_ratio: float = 1.0  # distinct keys = rows * ratio; 1.0 => no map-side reduction
    payload_repeat: int = 7  # payload width = 32 chars (md5) * 7 = 224 chars per row
    input_partitions: int = 8  # partitions used by spark.range generation
    shuffle_partitions: int = 4  # few, fat reduce partitions so each one overflows memory
    memory_fraction: float = 0.2  # shrink the unified memory pool to guarantee spill at 1g heap
    seed: int = 42  # reserved for future random generators; current generation is hash-based

    def spark_conf(self) -> dict[str, Any]:
        """Session extra_conf that forces memory->disk spill during the shuffle."""
        return {
            # Keep every join/aggregation on the shuffle path.
            "spark.sql.autoBroadcastJoinThreshold": -1,
            # Few reduce partitions => each task must process ~rows/4 wide rows.
            "spark.sql.shuffle.partitions": self.shuffle_partitions,
            # Starve execution memory so hash aggregation and sorting spill.
            "spark.memory.fraction": self.memory_fraction,
            # Deterministic partition count: no runtime coalescing/replanning.
            "spark.sql.adaptive.enabled": False,
            "spark.sql.adaptive.coalescePartitions.enabled": False,
        }

    @property
    def distinct_keys(self) -> int:
        """Number of distinct group keys derived from rows and distinct_key_ratio."""
        return max(1, int(self.rows * self.distinct_key_ratio))


@dataclass(frozen=True)
class GcChurnParams:
    """Parameters for the GC-pressure workload (gc_churn.py): object churn on a small heap."""

    rows: int = 600_000  # base rows before explode; sized to churn WITHOUT spilling (spill dilutes the GC ratio)
    explode_factor: int = 24  # each row explodes into this many short-lived rows; sized for margin above the 10% GC threshold
    payload_repeat: int = 4  # churny string payload per exploded row
    input_partitions: int = 8
    shuffle_partitions: int = 8
    executor_memory: str = "512m"  # small heap => frequent young-gen collections
    gc_java_options: str = "-XX:+UseSerialGC -Xmn4m"  # serial GC + tiny young gen; calibrated to ~12% GC (warning tier)
    seed: int = 42

    def spark_conf(self) -> dict[str, Any]:
        """Session extra_conf that maximizes allocation churn on a small heap.

        G1 on Java 17 absorbs SQL-op churn almost for free (~1% GC), so the
        workload also pins the executor JVM to the serial collector with a
        tiny young generation — the deliberately bad setting that turns the
        same churn into measurable GC time (>= the detector's 15% threshold).
        """
        return {
            "spark.executor.memory": self.executor_memory,
            "spark.executor.extraJavaOptions": self.gc_java_options,
            "spark.sql.shuffle.partitions": self.shuffle_partitions,
            "spark.sql.autoBroadcastJoinThreshold": -1,
            "spark.sql.adaptive.enabled": False,
        }


@dataclass(frozen=True)
class OomVictimParams:
    """Parameters for the OOM workload (oom_victim.py): allocations that cannot spill."""

    rows: int = 4  # one giant allocation per task
    array_cells: int = 60_000_000  # sequence(1, N) longs per row (~8B each) >> heap
    input_partitions: int = 4
    executor_memory: str = "512m"
    task_max_failures: int = 2  # abort fast; default 4 retries just waste time
    seed: int = 42

    def spark_conf(self) -> dict[str, Any]:
        """Session extra_conf that guarantees an executor-side OutOfMemoryError."""
        return {
            "spark.executor.memory": self.executor_memory,
            "spark.task.maxFailures": self.task_max_failures,
            "spark.sql.adaptive.enabled": False,
        }


@dataclass(frozen=True)
class CrossJoinParams:
    """Parameters for the plan-antipattern workload (cross_join.py): CartesianProduct."""

    left_rows: int = 3_000
    right_rows: int = 3_000  # 9M combinations: visible in the plan, cheap to run
    input_partitions: int = 4
    seed: int = 42

    def spark_conf(self) -> dict[str, Any]:
        """Session extra_conf that keeps the cartesian product visible in the plan."""
        return {
            "spark.sql.autoBroadcastJoinThreshold": -1,
            "spark.sql.adaptive.enabled": False,
        }


@dataclass(frozen=True)
class CacheHeavyParams:
    """Parameters for the cache-tracking workload (cache_heavy.py): oversized persist."""

    rows: int = 1_200_000
    payload_repeat: int = 7  # ~224-char payload => dataset larger than the storage pool
    input_partitions: int = 8
    memory_fraction: float = 0.3  # shrink storage memory so cached blocks overflow to disk
    seed: int = 42

    def spark_conf(self) -> dict[str, Any]:
        """Session extra_conf that logs cache block events and forces disk-tier caching."""
        return {
            # Emit SparkListenerBlockUpdated events into the event log (off by default);
            # the spark_cache_blocks view reads them from spark_raw_events.
            "spark.eventLog.logBlockUpdates.enabled": True,
            "spark.memory.fraction": self.memory_fraction,
            "spark.sql.adaptive.enabled": False,
        }


WorkloadParams = Union[
    SkewJoinParams, ShuffleHeavyParams, GcChurnParams, OomVictimParams, CrossJoinParams, CacheHeavyParams
]

CATALOG: dict[str, WorkloadParams] = {
    "skew_join": SkewJoinParams(),
    "shuffle_heavy": ShuffleHeavyParams(),
    "gc_churn": GcChurnParams(),
    "oom_victim": OomVictimParams(),
    "cross_join": CrossJoinParams(),
    "cache_heavy": CacheHeavyParams(),
}


def apply_env_overrides(params: ParamsT, environ: Mapping[str, str] | None = None) -> ParamsT:
    """Return a copy of `params` with WORKLOAD_<FIELD> env overrides applied.

    Each override is cast to the type of the field's default value, so
    `WORKLOAD_ROWS=1000000` yields an int and `WORKLOAD_MEMORY_FRACTION=0.3`
    a float. Invalid values raise ValueError early, before any Spark work.
    """
    env = os.environ if environ is None else environ
    overrides: dict[str, Any] = {}
    for field in fields(params):
        raw = env.get(f"{ENV_PREFIX}{field.name.upper()}")
        if raw is None:
            continue
        field_type = type(getattr(params, field.name))
        try:
            overrides[field.name] = field_type(raw)
        except ValueError as exc:
            raise ValueError(
                f"Invalid value {raw!r} for {ENV_PREFIX}{field.name.upper()} "
                f"(expected {field_type.__name__})"
            ) from exc
    return replace(params, **overrides) if overrides else params


def load_params(name: str, environ: Mapping[str, str] | None = None) -> WorkloadParams:
    """Fetch a workload's parameters from the catalog with env overrides applied."""
    try:
        params = CATALOG[name]
    except KeyError as exc:
        raise KeyError(
            f"Unknown workload '{name}'. Available workloads: {sorted(CATALOG)}"
        ) from exc
    return apply_env_overrides(params, environ)


def describe(params: WorkloadParams) -> str:
    """One-line `field=value` rendering of the parameters, for start-of-run logging."""
    return " ".join(f"{field.name}={getattr(params, field.name)}" for field in fields(params))
