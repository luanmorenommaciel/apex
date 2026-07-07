import json
from typing import Any

from spark_platform.utils.logger import logger

from apex_diagnostics.clickhouse import CHClient
from apex_diagnostics.config import DiagnosticsThresholds
from apex_diagnostics.crew.tools import build_detector_tools
from apex_diagnostics.models import DiagnosticReport, Finding


def detectors_only_report(app_id: str, findings: list[Finding]) -> DiagnosticReport:
    by_severity: dict[str, int] = {}
    for finding in findings:
        by_severity[finding.severity.value] = by_severity.get(finding.severity.value, 0) + 1
    counts = ", ".join(f"{count} {severity}" for severity, count in sorted(by_severity.items())) or "no findings"
    return DiagnosticReport(
        app_id=app_id,
        status="detectors_only",
        summary=f"Deterministic detectors produced {counts} for {app_id}. LLM analysis skipped.",
        findings=findings,
    )


def run_crew(
    app_id: str,
    findings: list[Finding],
    llm: Any,
    client: CHClient,
    thresholds: DiagnosticsThresholds,
) -> DiagnosticReport:
    from crewai import Agent, Crew, Process, Task

    findings_json = json.dumps([finding.model_dump() for finding in findings])
    tools = build_detector_tools(client, thresholds)

    analyst = Agent(
        role="Spark Diagnostic Analyst",
        goal="Rank the root causes behind detector findings for one Spark application run.",
        backstory=(
            "You are a Spark performance engineer. You trust the deterministic detector findings "
            "you are given, may re-run detector tools for detail, and never invent metrics."
        ),
        llm=llm,
        tools=tools,
        memory=False,
        verbose=False,
        max_iter=3,
        max_rpm=10,
    )
    writer = Agent(
        role="Spark Recommendation Writer",
        goal="Turn the analysis into concrete, safe spark.conf and code recommendations.",
        backstory=(
            "You write actionable Spark tuning advice. Every recommendation names an exact "
            "spark.conf key and value justified by the evidence."
        ),
        llm=llm,
        memory=False,
        verbose=False,
        max_iter=3,
        max_rpm=10,
    )

    analyze = Task(
        agent=analyst,
        description=(
            f"Analyze Spark application '{app_id}'. Deterministic detector findings (JSON): "
            f"{findings_json}. Identify the most likely root causes, ranked by impact. "
            "Use detector tools only if you need to re-check evidence."
        ),
        expected_output="A ranked root-cause analysis referencing finding evidence values.",
    )
    report = Task(
        agent=writer,
        context=[analyze],
        description=(
            f"Write the final diagnostic report for '{app_id}'. Include a concise summary, keep the "
            "original findings unchanged, and add at least one concrete recommendation per warning or "
            "critical finding with an exact spark.conf key and suggested value. Set status to 'full'."
        ),
        expected_output="A DiagnosticReport object with summary, findings, and recommendations.",
        output_pydantic=DiagnosticReport,
    )

    crew = Crew(agents=[analyst, writer], tasks=[analyze, report], process=Process.sequential)
    result = crew.kickoff()
    produced = result.pydantic
    if produced is None:
        raise ValueError("Crew did not return a typed DiagnosticReport")
    produced.app_id = app_id
    produced.status = "full"
    # The findings are deterministic detector output and drive max_severity()
    # (persisted to spark_diagnostic_reports). The LLM's job is summary +
    # recommendations only; it must never add/drop/reorder findings, so we always
    # restore the original list rather than trusting whatever the model echoed
    # back (previously only restored when the model returned an empty list).
    produced.findings = findings
    return produced


def analyze(app_id: str, client: CHClient, thresholds: DiagnosticsThresholds) -> DiagnosticReport:
    """Full pipeline: detectors -> Crew A (if configured) -> DiagnosticReport.

    Never raises on LLM problems; degrades to a detectors-only report so
    callers like `make spark-logs` stay green (AT-005).
    """
    from apex_diagnostics import detectors
    from apex_diagnostics.crew.llm import build_llm

    findings = detectors.run_all(client, app_id, thresholds)
    llm = build_llm()
    if llm is None:
        return detectors_only_report(app_id, findings)
    try:
        return run_crew(app_id, findings, llm, client, thresholds)
    except Exception as exc:
        logger.warning(f"Crew analysis failed for {app_id}; storing detectors-only report: {exc}")
        return detectors_only_report(app_id, findings)
