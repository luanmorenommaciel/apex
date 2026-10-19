"""OTLP drain decision (pyspark-free, importable on the host).

`stop_session` sleeps before `spark.stop()` so the ApexPlugin's bounded span
queue can finish exporting (measured 2026-07-28: fast ~20 s lab apps lost
their whole export ~2/3 of the time without it). That wait only makes sense
when the plugin is attached. The r9d OFF arm and any plain run submit with
`spark.plugins=` (empty) and were still paying the five seconds, inflating the
control arm of the overhead A/B.
"""
from __future__ import annotations

import os
from typing import Mapping

PLUGIN_CLASS = "apex.ApexPlugin"
DRAIN_ENV = "APEX_OTLP_DRAIN_SECONDS"
DEFAULT_DRAIN_SECONDS = 5.0


def plugin_attached(spark_plugins: str | None) -> bool:
    """True when `spark.plugins` names the Apex plugin (comma-separated list)."""
    if not spark_plugins:
        return False
    return any(part.strip() == PLUGIN_CLASS for part in spark_plugins.split(","))


def drain_seconds(spark_plugins: str | None, env: Mapping[str, str] | None = None) -> float:
    """Seconds to wait before spark.stop(): 0 without the plugin, else the configured value."""
    if not plugin_attached(spark_plugins):
        return 0.0
    source = os.environ if env is None else env
    raw = source.get(DRAIN_ENV)
    if raw is None or not raw.strip():
        return DEFAULT_DRAIN_SECONDS
    try:
        value = float(raw)
    except ValueError:
        return DEFAULT_DRAIN_SECONDS
    return max(0.0, value)
