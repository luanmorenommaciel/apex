from apex_diagnostics.models import DiagnosticReport, Finding, Recommendation, Severity


def make_finding(severity: Severity) -> Finding:
    return Finding(
        detector="skew",
        severity=severity,
        app_id="app-1",
        stage_id=1,
        title="t",
        evidence={"ratio": 3.5},
    )


def test_report_json_round_trip():
    report = DiagnosticReport(
        app_id="app-1",
        status="full",
        summary="s",
        findings=[make_finding(Severity.WARNING)],
        recommendations=[Recommendation(conf_key="spark.sql.shuffle.partitions", suggested_value="64", rationale="r")],
    )
    restored = DiagnosticReport.model_validate_json(report.model_dump_json())
    assert restored == report


def test_max_severity_ranks_critical_over_warning():
    report = DiagnosticReport(
        app_id="app-1",
        status="detectors_only",
        summary="s",
        findings=[make_finding(Severity.WARNING), make_finding(Severity.CRITICAL), make_finding(Severity.INFO)],
    )
    assert report.max_severity() == "critical"


def test_max_severity_none_without_findings():
    report = DiagnosticReport(app_id="app-1", status="detectors_only", summary="s")
    assert report.max_severity() == "none"
