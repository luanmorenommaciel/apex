import http.client
import json
from threading import Thread

import pytest

from apex.commander.ui_server import create_ui_server


@pytest.fixture()
def ui_server(tmp_path):
    evidence = tmp_path / "evidence"
    generated = evidence / "generated" / "mcp-ide-subprocess-smoke"
    generated.mkdir(parents=True)
    (evidence / "apex-product-readiness-2026-07-19-summary.json").write_text(
        json.dumps({"status": "ready", "score": 100, "f7": {}}), encoding="utf-8"
    )
    (generated / "store.ndjson").write_text("", encoding="utf-8")
    (generated / "findings.ndjson").write_text("", encoding="utf-8")
    (evidence / "crew-judge-external-llm-success-final-2026-07-19.json").write_text(
        json.dumps({"crew_ai": {}}), encoding="utf-8"
    )
    server = create_ui_server(tmp_path, port=0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()


def request(server, method, path):
    connection = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=3)
    connection.request(method, path)
    response = connection.getresponse()
    payload = response.read().decode("utf-8")
    connection.close()
    return response.status, response.getheader("Content-Type"), payload


def test_ui_server_serves_html_and_read_only_api(ui_server):
    status, content_type, html = request(ui_server, "GET", "/")
    assert status == 200
    assert content_type == "text/html; charset=utf-8"
    assert "Apex Commander UI" in html

    status, content_type, payload = request(ui_server, "GET", "/api/snapshot")
    assert status == 200
    assert content_type == "application/json; charset=utf-8"
    assert json.loads(payload)["read_only"] is True


def test_ui_server_health_and_mutations_are_blocked(ui_server):
    status, _, payload = request(ui_server, "GET", "/api/health")
    assert status == 200
    assert json.loads(payload)["mode"] == "read_only"

    status, _, payload = request(ui_server, "POST", "/api/snapshot")
    assert status == 405
    assert json.loads(payload)["status"] == "method_not_allowed"


def test_ui_server_live_demo_preview_is_fixed_and_sanitized(tmp_path):
    evidence = tmp_path / "evidence" / "generated" / "mcp-ide-subprocess-smoke"
    evidence.mkdir(parents=True)
    (evidence / "store.ndjson").write_text("", encoding="utf-8")
    (evidence / "findings.ndjson").write_text(
        json.dumps({"finding": {"job_id": "job-42", "kind": "shuffle_skew_candidate", "severity": "high", "confidence": "medium", "evidence": {}}, "validation": {"accepted": True}}) + "\n",
        encoding="utf-8",
    )
    target = tmp_path / "examples" / "apex_ui_demo_skew_job.py"
    target.parent.mkdir()
    target.write_text("df.join(dim, \"id\").count()\n", encoding="utf-8")
    server = create_ui_server(tmp_path, port=0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, _, payload = request(server, "GET", "/api/recommendations")
        assert status == 200
        assert json.loads(payload)["count"] == 1
        assert json.loads(payload)["case_id"] == "job-42"

        status, _, payload = request(server, "GET", "/api/preview?path=outside.py")
        preview = json.loads(payload)
        assert status == 200
        assert preview["status"] == "preview_ready"
        assert preview["case_id"] == "job-42"
        assert preview["approval_token_exposed"] is False
        assert "approval" not in preview
        assert str(target) == preview["target"]
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()


def test_ui_server_rejects_non_loopback_host(tmp_path):
    with pytest.raises(ValueError, match="loopback"):
        create_ui_server(tmp_path, host="0.0.0.0", port=0)
