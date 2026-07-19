"""Loopback-only server for the read-only Apex Commander UI."""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from apex.commander.commander_ui import build_commander_ui_snapshot, render_commander_ui

LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


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
