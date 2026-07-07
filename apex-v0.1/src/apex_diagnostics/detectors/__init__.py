from collections.abc import Callable
from dataclasses import dataclass

from apex_diagnostics.clickhouse import CHClient
from apex_diagnostics.config import DiagnosticsThresholds
from apex_diagnostics.detectors.gc import detect_gc
from apex_diagnostics.detectors.oom import detect_oom
from apex_diagnostics.detectors.plans import detect_plans
from apex_diagnostics.detectors.shuffle import detect_shuffle
from apex_diagnostics.detectors.skew import detect_skew
from apex_diagnostics.models import Finding

__all__ = [
    "detect_skew",
    "detect_shuffle",
    "detect_plans",
    "detect_gc",
    "detect_oom",
    "run_all",
    "DetectorSpec",
    "DETECTORS",
    "DETECTORS_BY_NAME",
]


@dataclass(frozen=True)
class DetectorSpec:
    """Single source of truth for one detector.

    Every surface that exposes detectors — run_all, the Crew tools
    (crew/tools.py) and the MCP server — derives from DETECTORS so they can
    never drift (previously the Crew shipped only 3 of the 5 detectors).
    """

    name: str
    description: str
    fn: Callable[..., list[Finding]]
    # Attribute on DiagnosticsThresholds passed to fn, or None when the detector
    # takes no thresholds (oom classifies failure reasons, no tunable cutoff).
    threshold_attr: str | None

    def run(self, client: CHClient, app_id: str, thresholds: DiagnosticsThresholds) -> list[Finding]:
        if self.threshold_attr is None:
            return self.fn(client, app_id)
        return self.fn(client, app_id, getattr(thresholds, self.threshold_attr))


DETECTORS: list[DetectorSpec] = [
    DetectorSpec("detect_skew", "Deterministic per-stage task-duration skew findings for a Spark application.", detect_skew, "skew"),
    DetectorSpec("detect_shuffle", "Deterministic per-stage shuffle-volume and spill findings for a Spark application.", detect_shuffle, "shuffle"),
    DetectorSpec("detect_plans", "Deterministic AQE adaptive-plan and join-antipattern findings per SQL execution.", detect_plans, "plans"),
    DetectorSpec("detect_gc", "Deterministic per-stage GC-pressure findings for a Spark application.", detect_gc, "gc"),
    DetectorSpec("detect_oom", "Deterministic OOM / lost-executor classification of failed tasks.", detect_oom, None),
]
DETECTORS_BY_NAME: dict[str, DetectorSpec] = {spec.name: spec for spec in DETECTORS}


def run_all(client: CHClient, app_id: str, thresholds: DiagnosticsThresholds) -> list[Finding]:
    findings: list[Finding] = []
    for spec in DETECTORS:
        findings.extend(spec.run(client, app_id, thresholds))
    return findings
