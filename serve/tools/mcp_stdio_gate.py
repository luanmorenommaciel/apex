"""Exercise the packaged Apex MCP server through the official stdio client.

Verifies what only a real client can verify:
  * the server survives `initialize` over stdio (no stray stdout byte),
  * it lists exactly the five contracted tools with the right annotations,
  * it exposes apex://runs as a resource and NOT as a tool,
  * every tool returns schema-valid structured output,
  * `suggest_fix` reports `applied=False` / `requires_human_approval=True`.

Run against a live ClickHouse:
    uv run python tools/mcp_stdio_gate.py
    APEX_GATE_JOB_ID=app-... uv run python tools/mcp_stdio_gate.py
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_TOOLS = [
    {"name": "analyze_run", "readOnlyHint": True},
    {"name": "compare_runs", "readOnlyHint": True},
    {"name": "list_runs", "readOnlyHint": True},
    {"name": "search_kb", "readOnlyHint": True},
    {"name": "suggest_fix", "readOnlyHint": False},
]

# A resource is not a tool. It must appear here and NOT in EXPECTED_TOOLS.
EXPECTED_RESOURCES = ["apex://runs"]


def _payload(result) -> dict:  # noqa: ANN001
    """Structured output if the SDK gave us one, else the JSON text block."""
    if getattr(result, "structuredContent", None):
        return result.structuredContent
    return json.loads(result.content[0].text)


async def main() -> int:
    # Unset by default: the gate discovers its own subject through list_runs
    # rather than hardcoding a fixture id that exists on exactly one machine.
    # An override still wins, for pointing the gate at a specific production run.
    job_id = os.getenv("APEX_GATE_JOB_ID", "")
    baseline_id = os.getenv("APEX_GATE_BASELINE_ID", "")

    environment = {
        **os.environ,
        "CLICKHOUSE_HOST": os.getenv("CLICKHOUSE_HOST", "127.0.0.1"),
        "CLICKHOUSE_PORT": os.getenv("CLICKHOUSE_PORT", "8123"),
        "CLICKHOUSE_USER": os.getenv("CLICKHOUSE_USER", "apex"),
        "CLICKHOUSE_PASSWORD": os.getenv("CLICKHOUSE_PASSWORD", "apex_local_dev"),
        "CLICKHOUSE_DATABASE": os.getenv("CLICKHOUSE_DATABASE", "apex"),
    }
    parameters = StdioServerParameters(
        command="uv", args=["run", "apex-mcp"], env=environment, cwd=str(ROOT)
    )

    async with stdio_client(parameters) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            listed = await session.list_tools()
            tool_metadata = [
                {
                    "name": tool.name,
                    "readOnlyHint": tool.annotations.readOnlyHint
                    if tool.annotations
                    else None,
                }
                for tool in listed.tools
            ]
            assert tool_metadata == EXPECTED_TOOLS, tool_metadata

            # Discover a subject with the very capability under test. Before
            # list_runs existed this gate could only run where a known job_id
            # had been seeded by hand.
            if not job_id:
                discovered = _payload(
                    await session.call_tool("list_runs", {"limit": 5})
                )["runs"]
                assert discovered, (
                    "list_runs returned nothing — seed a run, or set "
                    "APEX_GATE_JOB_ID"
                )
                job_id = discovered[0]["job_id"]
                baseline_id = baseline_id or discovered[-1]["job_id"]

            # The lane's first resource. Orientation must not cost a tool call,
            # and a resource must never inflate the tool surface a model sees.
            resources = await session.list_resources()
            resource_uris = sorted(str(r.uri) for r in resources.resources)
            assert resource_uris == EXPECTED_RESOURCES, resource_uris
            runs_doc = await session.read_resource("apex://runs")
            runs_payload = json.loads(runs_doc.contents[0].text)
            assert "runs" in runs_payload and "untrusted_fields" in runs_payload, runs_payload
            assert "runs[].app_name" in runs_payload["untrusted_fields"]

            suggest = next(t for t in listed.tools if t.name == "suggest_fix")
            assert suggest.annotations is not None
            assert suggest.annotations.destructiveHint is False
            assert suggest.annotations.idempotentHint is True

            analyze = await session.call_tool("analyze_run", {"job_id": job_id})
            compare = await session.call_tool(
                "compare_runs",
                {"baseline_job_id": baseline_id, "current_job_id": job_id},
            )
            search = await session.call_tool(
                "search_kb", {"query": "skew join", "top_k": 3}
            )
            fix = await session.call_tool("suggest_fix", {"job_id": job_id})

            for name, result in (
                ("analyze_run", analyze),
                ("compare_runs", compare),
                ("search_kb", search),
                ("suggest_fix", fix),
            ):
                assert not result.isError, f"{name} returned an error result"

            diagnosis = _payload(analyze)
            comparison = _payload(compare)
            hits = _payload(search)
            suggestion = _payload(fix)

            assert diagnosis["job_id"] == job_id
            assert diagnosis["stages"], "no stage telemetry for the gate job_id"
            assert suggestion["applied"] is False
            assert suggestion["requires_human_approval"] is True

    print(
        json.dumps(
            {
                "gate": "serve-stdio-mcp",
                "job_id": job_id,
                "tools": tool_metadata,
                "analyze_run": {
                    "status": diagnosis["status"],
                    "stage_count": diagnosis["stage_count"],
                    "worst_stage_id": diagnosis["worst_stage_id"],
                    "primary_symptom": diagnosis["primary_symptom"],
                    "summary": diagnosis["summary"],
                    "aqe_ground_truth": diagnosis["aqe_ground_truth"],
                },
                "compare_runs": {
                    "status": comparison["status"],
                    "regressions": len(comparison["regressions"]),
                    "plan_fingerprint_changed": comparison["plan_fingerprint_changed"],
                },
                "search_kb": {"total": hits["total"], "tokens": hits["tokens"]},
                "suggest_fix": {
                    "source": suggestion["source"],
                    "confidence": suggestion["confidence"],
                    "gated": suggestion["gated"],
                    "applied": suggestion["applied"],
                    "requires_human_approval": suggestion["requires_human_approval"],
                    "diff_lines": len(suggestion["proposed_diff"].splitlines()),
                },
                "status": "passed",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
