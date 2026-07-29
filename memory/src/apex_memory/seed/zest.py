"""ZEST cold-start seed loader — DROP-IN, NOT SEEDED.

STATUS: Apex is **not** seeded with ZEST data, and this module does not make it
so. It is the loader that would ingest that dataset if it became reachable.

WHY NOT
-------
The ZEST paper (arXiv 2503.03826) states it releases "the largest and most
comprehensive suite of Spark query datasets", and the companion repository
(layer6ai-labs/spark-retrieval-tuning) gives the location as
`s3://l6lab/sparktune/raw`. That location is **not publicly readable**. Probed
2026-07-27:

    aws s3 ls s3://l6lab/sparktune/raw/ --no-sign-request
        -> AccessDenied (ListObjectsV2)
    GET https://l6lab.s3.amazonaws.com/?list-type=2&prefix=sparktune/
        -> 403, <Code>AccessDenied</Code>, x-amz-bucket-region: us-east-1

The bucket exists; anonymous listing and reads are denied. So the 19,360-run
cold-start corpus cannot be ingested, and no claim is made that Apex benefits
from it. `probe_zest_dataset()` re-runs that check on demand so the status can
be re-confirmed rather than trusted from this comment.

WHAT IS BUILT
-------------
`load_zest_dump()` ingests the dataset's documented layout into
`apex.run_outcomes` with `outcome_source='zest-seed'` and
`config_source='zest-seed'`, so seeded rows are always distinguishable from
observed ones and can be deleted with a single predicate. The six tunables ZEST
optimises are exactly the six typed columns in the v0.3 DDL, so a seeded row
needs no translation.

Two honesty constraints are wired in rather than left to the caller:

  * A seeded row carries no `plan_fingerprint` from Apex's own hasher -- ZEST's
    plans were never processed by the jar's literal-normalising pass, so their
    hashes are not comparable to ours. Seeded rows are therefore reachable ONLY
    through the structural tier, never through an exact-fingerprint match that
    would imply a provenance they do not have.
  * ZEST ran on EMR r6g.2xlarge clusters at 100-750 GB scale. Its absolute
    runtimes mean nothing on someone else's hardware, so `task_time_ms` is
    seeded as 0 and seeded rows are excluded from delta prediction. They inform
    *which configuration* to try, never *how much faster it will be*.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from ..clickhouse import RUN_OUTCOME_COLUMNS, MemoryStore, utcnow
from ..conf import canonicalise, zest_columns

ZEST_BUCKET_URI = "s3://l6lab/sparktune/raw"
_ZEST_PROBE_URL = "https://l6lab.s3.amazonaws.com/?list-type=2&prefix=sparktune/&max-keys=1"

# ZEST's parameter names -> the Spark keys Apex stores them under.
ZEST_PARAM_TO_SPARK_KEY = {
    "spark.sql.shuffle.partitions": "spark.sql.shuffle.partitions",
    "spark.executor.instances": "spark.executor.instances",
    "spark.executor.cores": "spark.executor.cores",
    "spark.executor.memory": "spark.executor.memory",
    "spark.driver.cores": "spark.driver.cores",
    "spark.driver.memory": "spark.driver.memory",
}


@dataclass(frozen=True)
class ZestSeedStatus:
    reachable: bool
    detail: str

    def __str__(self) -> str:
        state = "REACHABLE" if self.reachable else "NOT REACHABLE"
        return f"{ZEST_BUCKET_URI}: {state} — {self.detail}"


def probe_zest_dataset(timeout: float = 15.0) -> ZestSeedStatus:
    """Check whether the ZEST dataset can actually be read anonymously.

    Exposed as a function so the claim in this module's header stays falsifiable:
    if Layer 6 opens the bucket, this flips to reachable without a code change.
    """
    try:
        with urllib.request.urlopen(_ZEST_PROBE_URL, timeout=timeout) as response:
            if response.status == 200:
                return ZestSeedStatus(True, "anonymous listing succeeded")
            return ZestSeedStatus(False, f"unexpected HTTP {response.status}")
    except urllib.error.HTTPError as exc:
        return ZestSeedStatus(
            False, f"HTTP {exc.code} — anonymous access denied (credentials required)"
        )
    except (urllib.error.URLError, OSError) as exc:
        return ZestSeedStatus(False, f"network error: {exc}")


def _outcome_row(record: dict, now) -> list:
    """Map one ZEST trial record onto a run_outcomes row."""
    conf = canonicalise(
        {
            spark_key: str(record["config"][zest_key])
            for zest_key, spark_key in ZEST_PARAM_TO_SPARK_KEY.items()
            if zest_key in record.get("config", {})
        }
    )
    zest = zest_columns(conf)
    return [
        f"zest:{record['dataset']}:{record['query']}:{record['trial']}",
        "",
        f"zest-{record['dataset']}-{record['query']}",
        # No Apex fingerprint: ZEST plans never went through the jar's
        # literal-normalising hasher, so any value here would assert a
        # comparability that does not exist. Empty keeps these rows out of the
        # exact tier by construction.
        "",
        zest["conf_shuffle_partitions"],
        zest["conf_executor_instances"],
        zest["conf_executor_cores"],
        zest["conf_executor_memory_mb"],
        zest["conf_driver_cores"],
        zest["conf_driver_memory_mb"],
        conf,
        "zest-seed",
        0, 0, 0,
        # task_time_ms deliberately 0 — see module header. Different hardware,
        # different scale; the absolute number would be actively misleading.
        0,
        0, 0, 0, 0, 0, 0, 0, 0, 0.0,
        0, 0, 0, "",
        "zest-seed",
        now,
        now,
    ]


def load_zest_dump(store: MemoryStore, dump_dir: str | Path) -> int:
    """Ingest a locally-materialised ZEST dump into apex.run_outcomes.

    Expects newline-delimited JSON records, each with `dataset`, `query`,
    `trial`, and a `config` object keyed by ZEST's parameter names. This is the
    shape of the per-trial Optuna records the paper's repo documents alongside
    `data_<tpch|tpcds>_<size>_emr_<trial>`.

    Returns the number of rows written. Raises FileNotFoundError if the dump is
    absent -- which it will be, until the bucket is opened or a copy is obtained
    directly from the authors.
    """
    dump_path = Path(dump_dir)
    if not dump_path.exists():
        raise FileNotFoundError(
            f"No ZEST dump at {dump_path}. Apex ships unseeded: "
            f"{ZEST_BUCKET_URI} denies anonymous access (see module header). "
            f"Obtain a copy from the authors, materialise it as NDJSON, and "
            f"point this loader at it."
        )

    now = utcnow()
    rows = []
    for line in dump_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(_outcome_row(json.loads(line), now))

    return store.insert("apex.run_outcomes", rows, RUN_OUTCOME_COLUMNS)
