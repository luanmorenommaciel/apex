from apex_mcp.models import Diagnosis
from apex_mcp.service import ApexReadService
from apex_mcp.store import FINDINGS_SQL, KB_SEARCH_SQL, STAGES_SQL, ReadStore


class FakeResult:
    def __init__(self, rows):
        self.rows = rows

    def named_results(self):
        return self.rows


class FakeClient:
    def __init__(self, stages, findings):
        self.stages_data = stages
        self.findings_data = findings
        self.calls = []

    def query(self, query, parameters):
        self.calls.append((query, parameters))
        return FakeResult(self.stages_data if query == STAGES_SQL else self.findings_data)


def stage(job_id="before"):
    return {"stage_id": 2, "app_id": f"app-{job_id}", "shuffle_read_bytes": 1_000,
            "spilled_bytes": 200, "p50_ms": 100, "p99_ms": 2_000}


def finding(job_id="before"):
    return {"finding_id": "finding-1", "job_id": job_id, "stage_id": 2, "type": "SKEW_ON_JOIN",
            "severity": "critical", "evidence": "p99/p50=20x", "impact": "slow", "fix": "enable AQE",
            "confidence": "HIGH", "detected_by": "skew_watcher"}


def test_store_parameterizes_job_id():
    client = FakeClient([], [])
    ReadStore(client).stages("job'quoted")
    assert "{job_id:String}" in STAGES_SQL
    assert "job'quoted" not in STAGES_SQL
    assert client.calls[0][1] == {"job_id": "job'quoted"}


def test_analyze_run_returns_structured_read_only_diagnosis():
    service = ApexReadService(ReadStore(FakeClient([stage()], [finding()])))
    result = service.analyze_run("before")
    assert isinstance(result, Diagnosis)
    assert result.status == "findings"
    assert result.findings[0].type == "SKEW_ON_JOIN"
    assert result.stages[0].p99_p50_ratio == 20


def test_analyze_run_reports_not_found_without_querying_findings():
    client = FakeClient([], [])
    result = ApexReadService(ReadStore(client)).analyze_run("missing")
    assert result.status == "not_found"
    assert len(client.calls) == 1


def test_compare_runs_reports_improvement():
    class ComparisonStore:
        def stages(self, job_id):
            return [stage(job_id)] if job_id == "before" else [{**stage(job_id), "spilled_bytes": 0, "p99_ms": 100}]

        def findings(self, job_id):
            return [finding(job_id)] if job_id == "before" else []

    result = ApexReadService(ComparisonStore()).compare_runs("before", "after")
    assert result.status == "improved"
    assert {item.metric for item in result.comparisons} == {"finding_count", "max_p99_p50_ratio", "total_spilled_bytes"}


def test_mcp_server_exposes_only_read_only_diagnosis_tools():
    mcp = create_server(ApexReadService(ReadStore(FakeClient([], []))))
    tools = asyncio.run(mcp.list_tools())
    assert [tool.name for tool in tools] == ["analyze_run", "compare_runs", "search_kb", "suggest_fix"]
    by_name = {tool.name: tool for tool in tools}
    assert all(by_name[name].annotations.readOnlyHint is True for name in ("analyze_run", "compare_runs", "search_kb"))
    assert by_name["suggest_fix"].annotations.readOnlyHint is False
    assert by_name["suggest_fix"].annotations.destructiveHint is False
    assert all(tool.annotations and tool.annotations.openWorldHint is False for tool in tools)


def test_search_kb_is_parameterized_and_returns_persisted_remediation():
    client = FakeClient([], [{**finding(), "fix": "review shuffle spill"}])
    result = ApexReadService(ReadStore(client)).search_kb("shuffle spill")
    assert result.hits[0].fix == "review shuffle spill"
    query, parameters = client.calls[0]
    assert query == KB_SEARCH_SQL
    assert "shuffle spill" not in KB_SEARCH_SQL
    assert parameters == {"pattern": "%shuffle spill%", "top_k": 5}


def test_suggest_fix_never_applies_and_returns_a_reviewable_proposal():
    service = ApexReadService(ReadStore(FakeClient([], [finding()])))
    result = service.suggest_fix("before", min_confidence=0.75)
    assert result.status == "proposed"
    assert result.applied is False
    assert result.requires_human_approval is True
    assert "--- a/<operator-selected-spark-job.py>" in result.diff
    assert "did not change files, Git state, or a running Spark job" in result.pr_body


def test_low_confidence_suggestion_is_advisory_only():
    low = {**finding(), "confidence": "LOW"}
    result = ApexReadService(ReadStore(FakeClient([], [low]))).suggest_fix("before")
    assert result.status == "advisory"
    assert result.applied is False
import asyncio

from apex_mcp.server import create_server
