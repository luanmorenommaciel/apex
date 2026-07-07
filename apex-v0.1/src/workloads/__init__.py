"""
Synthetic problem workloads that deliberately misbehave at local scale.

These jobs are the ground truth for the diagnostic detectors (design
D-007 in DESIGN_CREW_A_DIAGNOSTICS.md): each one forces a specific,
reproducible pathology (data skew, shuffle spill) so detector thresholds
can be calibrated against runs that are known to be unhealthy.

All tunable parameters live in `workloads.catalog`; the runner scripts
only wire parameters into a Spark session and materialize a DataFrame
through the `noop` sink.
"""

from workloads.catalog import (
    CATALOG,
    ShuffleHeavyParams,
    SkewJoinParams,
    describe,
    load_params,
)

__all__ = [
    "CATALOG",
    "ShuffleHeavyParams",
    "SkewJoinParams",
    "describe",
    "load_params",
]
