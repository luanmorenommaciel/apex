"""Loopback-only server for the read-only Apex Commander UI."""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from apex.commander.commander_ui import build_commander_ui_snapshot, render_commander_ui
from apex.commander.mcp_stdio_cli import JsonFindingStore
from apex.commander.tool_contract import CommanderToolContract

LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
DEMO_JOB_ID = "job-42"
DEMO_CASE_ID = DEMO_JOB_ID
DEMO_TARGET = Path("examples/apex_ui_demo_skew_job.py")
DEMO_REPLACEMENT = """# Apex Commander UI demo target. This file is never changed by the UI.
# Safe AQE skew join mitigation preview.
spark.conf.set(\"spark.sql.adaptive.enabled\", \"true\")
spark.conf.set(\"spark.sql.adaptive.skewJoin.enabled\", \"true\")
df.join(dim, \"id\").count()
"""


def create_ui_server(root: str | Path, host: str = "127.0.0.1", port: int = 8765):
    """Create a local-only read-only server without starting its event loop."""
    if host not in LOOPBACK_HOSTS:
        raise ValueError("ui_server_requires_loopback_host")

    base = Path(root).resolve()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 - required HTTP handler spelling
            path = urlparse(self.path).path
            snapshot = build_commander_ui_snapshot(base)
            if path in ("/", "/index.html"):
                self._send(HTTPStatus.OK, "text/html; charset=utf-8", render_commander_ui(snapshot))
                return
            if path == "/api/health":
                self._send_json({"status": "ok", "mode": "read_only", "host": host})
                return
            if path == "/api/snapshot":
                self._send_json(snapshot)
                return
            if path == "/api/recommendations":
                self._send_json(_demo_recommendations(base))
                return
            if path == "/api/preview":
                self._send_json(_demo_preview(base))
                return
            self._send_json({"status": "not_found"}, status=HTTPStatus.NOT_FOUND)

        def do_POST(self):  # noqa: N802 - required HTTP handler spelling
            self._send_json(
                {"status": "method_not_allowed", "mode": "read_only"},
                status=HTTPStatus.METHOD_NOT_ALLOWED,
            )

        def log_message(self, format, *args):  # noqa: A002
            return

        def _send_json(self, payload, status=HTTPStatus.OK):
            self._send(status, "application/json; charset=utf-8", json.dumps(payload, ensure_ascii=False))

        def _send(self, status, content_type, body):
            encoded = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(encoded)

    return ThreadingHTTPServer((host, port), Handler)


def _demo_contract(root: Path) -> CommanderToolContract:
    evidence = root / "evidence" / "generated" / "mcp-ide-subprocess-smoke"
    return CommanderToolContract(
        str(evidence / "store.ndjson"),
        finding_store=JsonFindingStore(evidence / "findings.ndjson"),
    )


def _demo_recommendations(root: Path) -> dict:
    """Run the real deterministic recommendation contract for the fixed demo job."""
    payload = _demo_contract(root).call_tool("recommend_fix", {"job_id": DEMO_JOB_ID})
    return {
        "mode": "read_only_demo",
        "case_id": DEMO_CASE_ID,
        "job_id": DEMO_JOB_ID,
        **payload,
    }


def _demo_preview(root: Path) -> dict:
    """Return a real preview, with a fixed target and without its approval token."""
    target = (root / DEMO_TARGET).resolve()
    if not target.is_file():
        return {
            "status": "demo_target_not_found",
            "mode": "read_only_demo",
            "target": str(DEMO_TARGET),
        }

    recommendations = _demo_recommendations(root)
    items = recommendations.get("recommendations") or []
    if not items:
        return {
            "status": "recommendation_not_found",
            "mode": "read_only_demo",
            "target": str(DEMO_TARGET),
        }

    preview = _demo_contract(root).call_tool(
        "preview_recommendation",
        {
            "job_id": DEMO_JOB_ID,
            "recommendation_id": items[0]["id"],
            "path": str(target),
            "replacement": DEMO_REPLACEMENT,
        },
    )
    preview.pop("approval", None)
    preview["case_id"] = DEMO_CASE_ID
    preview["approval_token_exposed"] = False
    preview["mode"] = "read_only_demo"
    return preview
