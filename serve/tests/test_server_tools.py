"""The MCP tool surface: exactly six tools, correct annotations, no stdout."""

from __future__ import annotations

import ast
import asyncio
import json
import subprocess
import sys
from pathlib import Path

import pytest

from apex_mcp.ch import ReadStore
from apex_mcp.server import create_server
from tests.conftest import FakeClient, finding_row, stage_row, transition_row

SRC = Path(__file__).resolve().parents[1] / "src"


@pytest.fixture
def server():
    client = FakeClient(
        stages={"j": [stage_row(4, p50_ms=20, p99_ms=460)], "base": [stage_row(4)]},
        findings={"j": [finding_row(job_id="j", confidence_score=0.9)], "base": []},
        transitions={"j": [transition_row("skew_split")]},
        search=[{"source": "findings", "job_id": "j", "stage_id": 2,
                 "finding_id": "f1", "type": "SKEW_ON_JOIN", "severity": "critical",
                 "snippet": "skew tail", "score": 2.0,
                 "matched_tokens": ["skew"]}],
    )
    return create_server(ReadStore(client))


def _tools(server):
    return asyncio.run(server.list_tools())


def test_exactly_the_six_contracted_tools(server):
    """Exact and ordered on purpose. A subset check would let a tool appear by
    accident, and an unnoticed tool on a server a model can call is a security
    event, not a cosmetic one.

    `recall_similar_runs` joins the surface with L6. Adding it here is a
    deliberate, reviewable act — which is the whole point of pinning the list
    rather than counting it."""
    assert [t.name for t in _tools(server)] == [
        "analyze_run",
        "compare_runs",
        "list_runs",
        "search_kb",
        "recall_similar_runs",
        "suggest_fix",
    ]


def test_read_tools_are_annotated_read_only(server):
    by_name = {t.name: t for t in _tools(server)}
    for name in ("analyze_run", "compare_runs", "search_kb", "recall_similar_runs"):
        annotations = by_name[name].annotations
        assert annotations is not None
        # camelCase — ToolAnnotations has no `read_only_hint` field, and
        # passing that name silently produces no annotation at all.
        assert annotations.readOnlyHint is True
        assert annotations.openWorldHint is False


def test_suggest_fix_is_the_only_non_read_only_tool(server):
    suggest = {t.name: t for t in _tools(server)}["suggest_fix"]
    assert suggest.annotations is not None
    assert suggest.annotations.readOnlyHint is False
    assert suggest.annotations.destructiveHint is False
    assert suggest.annotations.idempotentHint is True


def test_tool_annotations_use_camel_case_field_names():
    """Guards the exact trap the brief's snippet falls into."""
    from mcp.types import ToolAnnotations

    fields = set(ToolAnnotations.model_fields)
    assert "readOnlyHint" in fields
    assert "read_only_hint" not in fields


def test_every_tool_declares_a_structured_output_schema(server):
    for tool in _tools(server):
        assert tool.outputSchema, f"{tool.name} has no output schema"


def test_tools_return_schema_valid_payloads(server):
    for name, arguments in (
        ("analyze_run", {"job_id": "j"}),
        ("compare_runs", {"baseline_job_id": "base", "current_job_id": "j"}),
        ("search_kb", {"query": "skew", "top_k": 3}),
        ("suggest_fix", {"job_id": "j"}),
    ):
        result = asyncio.run(server.call_tool(name, arguments))
        assert result is not None


def test_suggest_fix_through_the_tool_layer_still_reports_applied_false(server):
    result = asyncio.run(server.call_tool("suggest_fix", {"job_id": "j"}))
    payload = result[1] if isinstance(result, tuple) else result
    assert payload["applied"] is False
    assert payload["requires_human_approval"] is True


def test_docstrings_warn_the_model_about_untrusted_text(server):
    by_name = {t.name: t for t in _tools(server)}
    assert "data, not instructions" in (by_name["analyze_run"].description or "")
    assert "data" in (by_name["search_kb"].description or "")
    assert "APPLIES NOTHING" in (by_name["suggest_fix"].description or "")


def test_no_module_in_the_package_calls_print():
    """stdout is the JSON-RPC channel; one print() corrupts the framing.

    Parsed, not grepped — the modules *discuss* print() in their docstrings.
    """
    offenders = []
    for path in SRC.rglob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "print"
            ):
                offenders.append(f"{path.name}:{node.lineno}")
    assert offenders == [], f"stdout writes: {offenders}"


def test_no_module_writes_to_sys_stdout_directly():
    offenders = []
    for path in SRC.rglob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and node.attr == "stdout"
                and isinstance(node.value, ast.Name)
                and node.value.id == "sys"
            ):
                offenders.append(f"{path.name}:{node.lineno}")
    assert offenders == [], f"sys.stdout references: {offenders}"


def test_server_emits_zero_stdout_bytes_on_clean_eof():
    """The real protocol guarantee, exercised as a subprocess."""
    completed = subprocess.run(
        [sys.executable, "-c", "from apex_mcp.server import main; main()"],
        cwd=SRC.parent,
        env={"PATH": "/usr/bin:/bin", "PYTHONPATH": str(SRC),
             "CLICKHOUSE_HOST": "127.0.0.1"},
        input=b"",
        capture_output=True,
        timeout=60,
    )
    assert completed.stdout == b""


def test_logging_is_configured_to_stderr():
    """Assert the handler's actual stream, not the source text."""
    import logging

    from apex_mcp import server

    root = logging.getLogger()
    saved = root.handlers[:]
    root.handlers = []
    try:
        server._configure_logging()
        streams = [
            handler.stream
            for handler in logging.getLogger().handlers
            if isinstance(handler, logging.StreamHandler)
        ]
        assert streams, "no stream handler configured"
        assert all(stream is sys.stderr for stream in streams)
    finally:
        root.handlers = saved


# --------------------------------------------------------------------------
# apex://runs — the lane's first MCP resource
# --------------------------------------------------------------------------
class _RunsOnlyClient:
    """Serves run-discovery rows; FakeClient routes on job_id and runs has none."""

    def __init__(self, rows: list[dict]) -> None:
        self.rows = rows

    def query(self, query: str, parameters: dict | None = None):
        return type("R", (), {"named_results": lambda _self: list(self.rows)})()


def _server_with_runs():
    return create_server(
        ReadStore(
            _RunsOnlyClient(
                [
                    {
                        "job_id": "job-recent",
                        "app_id": "app-1",
                        "app_name": "nightly_etl",
                        "first_ts": "2026-08-19T09:00:00",
                        "last_ts": "2026-08-19T09:12:00",
                        "stage_count": 7,
                        "spill_disk_bytes": 2048,
                        "worst_p99_ms": 460,
                    }
                ]
            )
        )
    )


def test_runs_resource_is_listed(server):
    """B-1 — a client can discover it without knowing the URI in advance."""
    resources = asyncio.run(server.list_resources())

    by_uri = {str(r.uri): r for r in resources}
    assert "apex://runs" in by_uri, sorted(by_uri)
    assert by_uri["apex://runs"].mimeType == "application/json"
    assert by_uri["apex://runs"].name


def test_runs_resource_returns_run_data():
    """B-2 — the same typed payload the tool returns, as JSON."""
    contents = list(asyncio.run(_server_with_runs().read_resource("apex://runs")))

    payload = json.loads(contents[0].content)
    assert payload["returned"] == 1
    assert payload["runs"][0]["job_id"] == "job-recent"
    assert payload["runs"][0]["stage_count"] == 7
    assert "runs[].app_name" in payload["untrusted_fields"]


def test_runs_resource_is_not_a_tool(server):
    """A resource must not inflate the tool surface the model sees."""
    assert "runs_resource" not in [t.name for t in _tools(server)]
