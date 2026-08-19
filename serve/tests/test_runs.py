"""Run-discovery payloads: minimal-required, schema-renderable, app_name untrusted.

`app_name` is the first string a Spark job author controls that Apex surfaces
*before* the user has chosen anything to look at. If it is not marked untrusted
here, nothing downstream will treat it as data.
"""

from __future__ import annotations

from apex_mcp.models import RunList, RunSummary


def test_run_summary_defaults_from_job_id():
    """B-1 — a malformed run must still be listable."""
    run = RunSummary(job_id="job-1")

    assert run.job_id == "job-1"
    assert run.app_name is None
    assert run.stage_count == 0
    assert run.spill_disk_bytes == 0
    assert run.worst_p99_ms == 0


def test_run_list_schema_renders():
    """B-2 — FastMCP derives the tool's output schema from this."""
    schema = RunList.model_json_schema()

    assert schema["properties"]["runs"]["type"] == "array"
    assert "RunSummary" in str(schema)


def test_app_name_is_marked_untrusted():
    """B-3 — the Spark job author picks app_name, so it is data, not prose."""
    payload = RunList(runs=[RunSummary(job_id="j", app_name="nightly_etl")]).model_dump()

    assert "runs[].app_name" in payload["untrusted_fields"]


def test_run_list_defaults_to_empty_not_null():
    """An empty store is a legitimate answer, not a missing one."""
    payload = RunList().model_dump()

    assert payload["runs"] == []
    assert payload["returned"] == 0
