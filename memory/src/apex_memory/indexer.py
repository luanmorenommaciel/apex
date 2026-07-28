"""Build apex.plan_memory and apex.run_outcomes from what is already stored.

The indexer is the only writer in this lane. It derives everything from
`apex.spark_events`, `apex.plan_transitions` and `apex.findings` -- it requires
no new emission from jar or collect, which is why the memory lane can be useful
today rather than after a pipeline change.

Both target tables are ReplacingMergeTree keyed on their natural identity, so
re-indexing is idempotent: running this twice leaves the same logical rows, the
way engine's `analyze()` converges rather than accumulating.
"""

from __future__ import annotations

from dataclasses import dataclass

from .clickhouse import (
    ALL_JOB_IDS_SQL,
    DISTINCT_PLANS_SQL,
    JOB_AQE_SQL,
    JOB_CONF_SQL,
    PLAN_MEMORY_COLUMNS,
    RUN_OUTCOME_COLUMNS,
    SEVERITY_BY_RANK,
    SHAPE_FINDINGS_SQL,
    SHAPE_OUTCOMES_SQL,
    MemoryStore,
    normalise_fingerprint,
    utcnow,
)
from .conf import canonicalise, zest_columns
from .config import EMBEDDING_KIND, ENCODER_VERSION, MIN_PLAN_NODES
from .encoder import VECTOR_DIM, encode


@dataclass
class IndexReport:
    plans_indexed: int = 0
    plans_skipped_unencodable: int = 0
    plans_skipped_degenerate: int = 0
    outcomes_indexed: int = 0
    jobs_seen: int = 0

    def __str__(self) -> str:
        return (
            f"plan_memory: {self.plans_indexed} indexed, "
            f"{self.plans_skipped_unencodable} skipped (no plan text), "
            f"{self.plans_skipped_degenerate} skipped (<{MIN_PLAN_NODES} nodes) | "
            f"run_outcomes: {self.outcomes_indexed} rows across "
            f"{self.jobs_seen} jobs"
        )


def index_plans(store: MemoryStore) -> tuple[int, int, int]:
    """Encode every distinct real plan into apex.plan_memory.

    Returns (indexed, skipped_unencodable, skipped_degenerate). Both skip
    reasons are counted and reported rather than silently dropped -- a
    similarity index that quietly ignores part of the corpus reads as complete
    coverage when it is not.
    """
    rows = store.query(DISTINCT_PLANS_SQL)
    now = utcnow()
    payload, skipped, degenerate = [], 0, 0

    for row in rows:
        feats = encode(row["plan_json"])
        if not feats.encodable:
            # A zero vector must never be indexed: cosineDistance against it is
            # 0/0, and the resulting NaN sorts unpredictably inside ORDER BY,
            # which would quietly corrupt every top-k that touched it.
            skipped += 1
            continue
        if feats.node_count < MIN_PLAN_NODES:
            # No structure to compare -- see config.MIN_PLAN_NODES.
            degenerate += 1
            continue
        payload.append([
            normalise_fingerprint(row["plan_fingerprint"]),
            ENCODER_VERSION,
            EMBEDDING_KIND,
            feats.vector,
            VECTOR_DIM,
            {k: int(v) for k, v in feats.op_counts.items()},
            feats.node_count,
            feats.max_depth,
            feats.join_count,
            feats.agg_count,
            feats.exchange_count,
            feats.scan_count,
            1 if feats.has_udf else 0,
            feats.plan_chars,
            row["plan_json"],
            row["first_seen"],
            row["last_seen"],
            now,
        ])

    written = store.insert("apex.plan_memory", payload, PLAN_MEMORY_COLUMNS)
    return written, skipped, degenerate


def index_outcomes_for_job(store: MemoryStore, job_id: str) -> int:
    """Derive and write one run_outcomes row per plan shape in `job_id`."""
    shapes = store.query(SHAPE_OUTCOMES_SQL, {"job_id": job_id})
    if not shapes:
        return 0

    aqe_rows = store.query(JOB_AQE_SQL, {"job_id": job_id})
    aqe = aqe_rows[0] if aqe_rows else {"aqe_skew_splits": 0, "aqe_coalesces": 0}

    findings = {
        normalise_fingerprint(r["plan_fingerprint"]): r
        for r in store.query(SHAPE_FINDINGS_SQL, {"job_id": job_id})
    }

    # Contract v0.4: the resolved allowlisted SparkConf, if this run emitted it.
    # Canonicalised on the way in so that '5' and '5.0' -- both present in the
    # live store for skewedPartitionFactor -- are stored as one value and cannot
    # later be miscounted as two distinct configurations.
    conf_rows = store.query(JOB_CONF_SQL, {"job_id": job_id})
    observed_conf = canonicalise(dict(conf_rows[0]["conf"])) if conf_rows else {}
    config_source = "observed" if observed_conf else "unknown"
    zest = zest_columns(observed_conf)

    now = utcnow()
    payload = []
    for shape in shapes:
        fp = normalise_fingerprint(shape["plan_fingerprint"])
        found = findings.get(fp)
        payload.append([
            shape["job_id"],
            shape["app_id"],
            shape["app_name"],
            fp,
            # The ZEST six, from apex.job_conf (contract v0.4). Only
            # shuffle.partitions is universally present in standalone runs;
            # executor.*/driver.* land only when explicitly set. A key the jar
            # did not capture stays None -- never a synthesised default, which
            # would be indistinguishable from an observation and would poison
            # "the config that worked".
            zest["conf_shuffle_partitions"],
            zest["conf_executor_instances"],
            zest["conf_executor_cores"],
            zest["conf_executor_memory_mb"],
            zest["conf_driver_cores"],
            zest["conf_driver_memory_mb"],
            # The full canonicalised allowlist, including the AQE knobs that are
            # not part of ZEST's six but are the ones that actually vary here.
            observed_conf,
            config_source,
            int(shape["stage_count"]),
            int(shape["task_count"]),
            int(shape["wall_clock_ms"]),
            int(shape["task_time_ms"]),
            int(shape["shuffle_read_bytes"]),
            int(shape["shuffle_write_bytes"]),
            int(shape["spill_disk_bytes"]),
            int(shape["spill_mem_bytes"]),
            int(shape["gc_time_ms"]),
            int(shape["input_bytes"]),
            int(shape["output_bytes"]),
            int(shape["peak_execution_mem_bytes"]),
            float(shape["max_skew_ratio"]),
            int(aqe["aqe_skew_splits"]),
            int(aqe["aqe_coalesces"]),
            int(found["finding_count"]) if found else 0,
            SEVERITY_BY_RANK.get(int(found["worst_severity_rank"]), "") if found else "",
            "apex",
            shape["observed_at"],
            now,
        ])

    return store.insert("apex.run_outcomes", payload, RUN_OUTCOME_COLUMNS)


def reindex(store: MemoryStore, job_ids: list[str] | None = None) -> IndexReport:
    """Rebuild the whole index, or just the given jobs."""
    report = IndexReport()
    (
        report.plans_indexed,
        report.plans_skipped_unencodable,
        report.plans_skipped_degenerate,
    ) = index_plans(store)

    if job_ids is None:
        job_ids = [r["job_id"] for r in store.query(ALL_JOB_IDS_SQL)]
    for job_id in job_ids:
        report.outcomes_indexed += index_outcomes_for_job(store, job_id)
        report.jobs_seen += 1
    return report
