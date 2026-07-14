"""Conf-recommendation grounding for the Crew writer agent (Seam 2).

Pure functions with no crewai dependency, so they are testable without a
running Crew: they turn deterministic Findings + the conf_recommendations.yaml
catalog into a text block that grounds the LLM writer in exact spark.conf keys
and values instead of letting it invent them.
"""

from apex_diagnostics.config import ConfRecommendation
from apex_diagnostics.models import Finding, Severity

# The writer must recommend a fix for every warning/critical finding; info-level
# findings (e.g. AQE replans) are context, not actionable, so they are skipped.
_ACTIONABLE = (Severity.WARNING, Severity.CRITICAL)


def select_conf_recommendation(
    finding: Finding, recommendations: list[ConfRecommendation]
) -> ConfRecommendation | None:
    """Pick the recommendation matching a finding.

    Matches on (detector, severity). For the plans detector a recommendation may
    also pin `pattern_match` to the finding's evidence["pattern"]; a
    pattern-specific match is preferred over a generic one so, e.g.,
    CartesianProduct and BroadcastNestedLoopJoin get distinct advice.
    """
    candidates = [
        rec
        for rec in recommendations
        if rec.detector == finding.detector and rec.severity == finding.severity
    ]
    if not candidates:
        return None
    pattern = finding.evidence.get("pattern")
    specific = [rec for rec in candidates if rec.pattern_match is not None and rec.pattern_match == pattern]
    if specific:
        return specific[0]
    generic = [rec for rec in candidates if rec.pattern_match is None]
    return generic[0] if generic else None


def build_recommendation_grounding(
    findings: list[Finding], recommendations: list[ConfRecommendation]
) -> str:
    """Build the grounding block injected into the writer agent's task.

    One line per actionable finding, carrying the validated conf_key/value (or a
    code-review note when conf_key is null) and its location. Returns "" when no
    finding maps to a recommendation, so the caller can skip injection entirely.
    """
    lines: list[str] = []
    for finding in findings:
        if finding.severity not in _ACTIONABLE:
            continue
        rec = select_conf_recommendation(finding, recommendations)
        if rec is None:
            continue
        location = (
            f"stage {finding.stage_id}"
            if finding.stage_id is not None
            else f"execution {finding.execution_id}"
        )
        if rec.conf_key:
            fix = f"set `{rec.conf_key}` = `{rec.suggested_value}`"
        else:
            fix = "no spark.conf fix — code review"
        lines.append(f"- {finding.detector}/{finding.severity.value} ({location}): {fix} — {rec.rationale}")
    return "\n".join(lines)
