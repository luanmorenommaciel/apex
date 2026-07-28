"""Memory-lane configuration — every knob is an env var with a local-dev default.

ClickHouse defaults match `infra/.env.example` and CONTRACT.md § Port Map
(HTTP 8123), identical to the engine lane. No secret is invented here.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

# ── Encoder identity ─────────────────────────────────────────────────────────
# Written into apex.plan_memory.encoder_version. Bump this string whenever the
# feature layout changes: rows encoded by different versions are NOT comparable,
# and recall() refuses to mix them rather than silently returning garbage
# neighbours. The (plan_fingerprint, encoder_version) primary key makes both
# generations coexist during a re-index.
ENCODER_VERSION = "struct-v1"
EMBEDDING_KIND = "structural"

# ── The noise floor (verify lane, measured — not assumed) ────────────────────
# The verify lane ran three BYTE-IDENTICAL jobs and measured job-level run-to-run
# variance at ~5.8% (1 sigma). Any predicted improvement smaller than this is
# indistinguishable from the same job run twice, so recall() must refuse to quote
# it as meaningful. We require the delta to clear 1 sigma before it is reported
# as real; below that the prediction is returned with meaningful=False and the
# reason `below_noise_floor`.
NOISE_FLOOR_PCT = 5.8

# The verify figure is JOB-level. recall() compares per-SHAPE task_time_ms, which
# is a different and much noisier quantity, so reusing 5.8 here would understate
# the floor by ~3x and wave through differences that are pure variance.
#
# Measured on the calibrated corpus (2026-07-28): 65 cells of >=3 runs sharing an
# identical plan shape, identical canonical config AND identical input_bytes,
# covering 308 runs -> median CV = 15.9% (1 sigma), p90 = 76.4%, max = 114.8%.
#
# Two things that measurement ruled out:
#   * It is NOT JVM warmup. Dropping each cell's first run leaves the median at
#     16.2% -- statistically unchanged.
#   * It is NOT a small-sample artefact. Median CV is 15.4% for cells with <=8
#     tasks and 15.1% for cells with >100 tasks; more tasks does not average it
#     out. The corpus was collected on a shared developer host, so background
#     load is the most likely driver.
#
# This constant is only the FALLBACK. When a shape has enough same-config runs to
# measure its own variance, recall() uses that instead -- a global median is a
# poor description of a distribution whose p90 is five times its median.
SHAPE_NOISE_FLOOR_PCT = 15.9

# A config group needs at least this many runs before its median is trusted as
# that configuration's performance. A single run is a sample, not an estimate.
MIN_RUNS_PER_CONFIG_GROUP = 2

# Minimum runs in a group before its within-group CV contributes to the
# empirical noise estimate.
MIN_RUNS_FOR_NOISE_ESTIMATE = 3

# ── Retrieval knobs ──────────────────────────────────────────────────────────
# ZEST tuned k=29 over an index of 19,360 executions. Apex's index is orders of
# magnitude smaller, so a k that large would reach past every genuinely similar
# plan and average in noise. We default to 10 and, more importantly, gate on
# similarity rather than on rank -- a neighbour below MIN_SIMILARITY is dropped
# even if that leaves fewer than k results. Returning three honest neighbours
# beats returning ten where seven are unrelated.
DEFAULT_TOP_K = 10
MIN_SIMILARITY = 0.80

# ── Confidence thresholds ────────────────────────────────────────────────────
# Deliberately strict. With the store as it stands (see README § "What the data
# can actually support") NOTHING reaches MEDIUM, and that is the correct answer.
# n_* counts DISTINCT JOBS, never rows: seventeen stages of one job are one
# observation, not seventeen.
HIGH_MIN_EXACT_JOBS = 8
HIGH_MIN_CONFIG_VARIANTS = 3
MEDIUM_MIN_EXACT_JOBS = 4
MEDIUM_MIN_CONFIG_VARIANTS = 2

# Fingerprints that carry no information. The store contains rows whose
# fingerprint is the empty FixedString (plan unavailable for that stage) and
# synthetic fixture rows whose fingerprint is all zeroes. Neither is a real plan
# and both would otherwise collide into one enormous bogus "shape".
NULL_FINGERPRINTS = ("", "0" * 64)

# Minimum operator count for a plan to enter the STRUCTURAL index.
#
# A single-node plan ("Scan parquet") has no structure, so every structural
# encoder must map all such plans to the same point -- they would all match each
# other at similarity 1.0 and drown real neighbours. This is not hypothetical:
# the live store's three fixture jobs contribute 51 distinct fingerprints that
# all render as the single node `Scan parquet`, and without this floor they
# became 51 perfect-similarity neighbours for any degenerate query.
#
# Filtering on the fingerprint's shape instead would be wrong -- a genuine
# SHA-256 may legitimately begin with zeroes -- so the test is on the plan's
# information content, which is the property that actually matters.
#
# This bounds plan_memory ONLY. run_outcomes still records these runs, and exact
# `plan_fingerprint` equality still retrieves them at full confidence: the exact
# tier needs no embedding, so nothing is lost by keeping them out of the fuzzy
# index.
MIN_PLAN_NODES = 2


@dataclass(frozen=True)
class ClickHouseSettings:
    host: str = os.getenv("CLICKHOUSE_HOST", "localhost")
    port: int = int(os.getenv("CLICKHOUSE_PORT", "8123"))
    username: str = os.getenv("CLICKHOUSE_USER", "apex")
    password: str = os.getenv("CLICKHOUSE_PASSWORD", "apex_local_dev")
    database: str = os.getenv("CLICKHOUSE_DATABASE", "apex")

    def connect(self):
        """Open a clickhouse-connect client. Imported lazily so the pure
        deterministic core (encoder, confidence) stays importable and testable
        without the driver installed."""
        import clickhouse_connect

        return clickhouse_connect.get_client(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            database=self.database,
        )
