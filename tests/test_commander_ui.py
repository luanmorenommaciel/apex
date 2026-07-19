import json

from apex.commander.commander_ui import build_commander_ui_snapshot, render_commander_ui


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def build_sources(tmp_path, *, app_id="app-before", evidence_value="29.5"):
    write(
        tmp_path / "evidence" / "readiness.json",
        json.dumps({
            "status": "ready", "score": 100, "latency_ms": 226.991,
            "f7": {"before_app_id": app_id, "after_app_id": "app-after", "status": "improved", "comparisons": [{"metric": "max_skew_ratio", "before": 29.5, "after": 1.0, "status": "improved"}]},
            "strengths": ["T1 green"], "gaps": [], "OPENAI_API_KEY": "must-not-render",
        }),
    )
    write(
        tmp_path / "evidence" / "store.ndjson",
        json.dumps({"job_id": "before-job", "app_id": app_id, "stages": [{"stage_id": 2, "task_count": 8, "ratio": 29.5, "disk_bytes_spilled": 10, "jvm_gc_time_ms": 2, "evidence_status": "valid"}]}) + "\n",
    )
    write(
        tmp_path / "evidence" / "findings.ndjson",
        json.dumps({"finding": {"job_id": "job-42", "kind": "shuffle_skew_candidate", "severity": "high", "confidence": "medium", "evidence": {"ratio": evidence_value}}, "validation": {"accepted": True}}) + "\n",
    )
    write(
        tmp_path / "evidence" / "judge.json",
        json.dumps({"crew_ai": {"provider": "crew_ai", "status": "judged", "decision": "manual_review", "rationale": "Evidence cited", "cited_evidence": ["finding.evidence.ratio=29.5"]}}),
    )


def snapshot_for(tmp_path):
    return build_commander_ui_snapshot(
        tmp_path,
        readiness_file="evidence/readiness.json",
        telemetry_file="evidence/store.ndjson",
        findings_file="evidence/findings.ndjson",
        judge_file="evidence/judge.json",
    )


def test_ui_snapshot_reads_approved_evidence_shapes(tmp_path):
    build_sources(tmp_path)

    snapshot = snapshot_for(tmp_path)

    assert snapshot["read_only"] is True
    assert snapshot["overview"]["score"] == 100
    assert snapshot["jobs"][0]["stages"][0]["ratio"] == 29.5
    assert snapshot["findings"][0]["kind"] == "shuffle_skew_candidate"
    assert snapshot["judge"]["provider"] == "crew_ai"
    assert snapshot["fix_center"]["preview_status"] == "not_persisted_in_approved_sources"


def test_ui_html_escapes_external_evidence_and_hides_sensitive_fields(tmp_path):
    build_sources(tmp_path, app_id="<script>alert(1)</script>", evidence_value="<img src=x onerror=alert(1)>")

    rendered = render_commander_ui(snapshot_for(tmp_path))

    assert "<script>alert(1)</script>" not in rendered
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in rendered
    assert "<img src=x" not in rendered
    assert "must-not-render" not in rendered
    assert "OPENAI_API_KEY" not in rendered


def test_ui_offers_only_read_only_live_actions(tmp_path):
    build_sources(tmp_path)

    rendered = render_commander_ui(snapshot_for(tmp_path))

    assert "Fix Center" in rendered
    assert "MCP preview_fix" in rendered
    assert "Carregar recomendacao real" in rendered
    assert "Gerar preview real" in rendered
    assert 'loadDemo("/api/recommendations")' in rendered
    assert '"/api/apply' not in rendered
    assert "approval_token" not in rendered
