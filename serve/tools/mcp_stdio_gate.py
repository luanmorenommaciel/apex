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
    {"name": "explain_stage", "readOnlyHint": True},
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

            # The DEFAULT answer, deliberately trimmed to the verdict.
            analyze = await session.call_tool("analyze_run", {"job_id": job_id})
            # ...and the same analysis at full width, to prove the trim is a
            # trim: the verdict must be identical, only the arrays differ.
            analyze_full = await session.call_tool(
                "analyze_run", {"job_id": job_id, "detail": "full"}
            )
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
                ("analyze_run(detail=full)", analyze_full),
                ("compare_runs", compare),
                ("search_kb", search),
                ("suggest_fix", fix),
            ):
                assert not result.isError, f"{name} returned an error result"

            diagnosis = _payload(analyze)
            full = _payload(analyze_full)
            comparison = _payload(compare)
            hits = _payload(search)
            suggestion = _payload(fix)

            assert diagnosis["job_id"] == job_id
            assert full["stages"], "no stage telemetry for the gate job_id"

            # The default is the verdict, not the data dump.
            assert diagnosis["stages"] == [], "summary leaked the stage array"
            assert diagnosis["findings"] == [], "summary leaked the finding array"
            # An emptied array must never read as an empty run.
            assert any("TRIMMED" in note for note in diagnosis["notes"])
            # Coverage survives the trim — that is what keeps [] legible.
            assert diagnosis["coverage"]["stages_observed"] == len(full["stages"])
            # Trimming NEVER re-runs the analysis, so the verdict is identical.
            for field in ("status", "worst_stage_id", "primary_symptom", "summary"):
                assert diagnosis[field] == full[field], field

            # Drill-down: one stage, or a stated miss — never an empty success.
            explained = _payload(
                await session.call_tool(
                    "explain_stage",
                    {"job_id": job_id, "stage_id": full["stages"][0]["stage_id"]},
                )
            )
            assert [s["stage_id"] for s in explained["stages"]] == [
                full["stages"][0]["stage_id"]
            ]
            absent = _payload(
                await session.call_tool(
                    "explain_stage", {"job_id": job_id, "stage_id": 99_999}
                )
            )
            assert absent["status"] == "not_found", absent["status"]
            assert "not observed" in absent["summary"]

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
                    "detail_default": "summary",
                    "stage_count": diagnosis["stage_count"],
                    "worst_stage_id": diagnosis["worst_stage_id"],
                    "primary_symptom": diagnosis["primary_symptom"],
                    "summary": diagnosis["summary"],
                    "tail_dominant_stage_ids": diagnosis["tail_dominant_stage_ids"],
                    "coverage": diagnosis["coverage"],
                    "aqe_ground_truth": diagnosis["aqe_ground_truth"],
                    "summary_stages": len(diagnosis["stages"]),
                    "full_stages": len(full["stages"]),
                    "verdict_identical_across_levels": True,
                },
                "explain_stage": {
                    "stage_id": explained["stages"][0]["stage_id"],
                    "symptoms": len(explained["symptoms"]),
                    "findings": len(explained["findings"]),
                    "unobserved_stage_status": absent["status"],
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
