"""search_kb answers from the redacted plan text the same way over both transports.

ReadStore.search runs two statements: one over apex.findings and one over the
plan_json tree-string in apex.spark_events. The conftest double answers every
statement that searches with positionCaseInsensitive from ONE list, so the plan
branch is fed the findings rows and no test ever saw a plan_json hit. This
double tells the two statements apart, so the plan branch is exercised on its
own: findings empty, one plan hit, and the payload compared over MCP and HTTP.

Offline only. The rows below stand for what the plan statement projects; this
does not show that the SQL matches anything in a real ClickHouse.
"""

from __future__ import annotations

from typing import Any

from tests.conftest import FakeClient, FakeResult, reads
from tests.test_tool_transport_parity import _over_http, _over_mcp

TOKEN = "planmarker42"
PLAN_SNIPPET = f"SortMergeJoin Inner {TOKEN} +- Exchange hashpartitioning(customer_id)"
FINGERPRINT = "3" * 64
ARGUMENTS = {"query": TOKEN, "top_k": 5}
PATH = f"/v1/diagnostics/search?q={TOKEN}&top_k=5"


def _plan_hit() -> dict[str, Any]:
    """One row in the shape _plans_search_sql projects: no finding_id, type or severity."""
    return {
        "source": "plan_json",
        "job_id": "j",
        "stage_id": 2,
        "snippet": PLAN_SNIPPET,
        "plan_fingerprint": FINGERPRINT,
        "score": 1.0,
        "matched_tokens": [TOKEN],
    }


class _SplitSearch(FakeClient):
    """Answers the findings search and the plan search from separate lists.

    Any other search statement is a failure, so a third or renamed statement
    cannot be served by accident."""

    def __init__(self, findings_hits: list[dict], plan_hits: list[dict]) -> None:
        super().__init__()
        self.findings_hits = findings_hits
        self.plan_hits = plan_hits
        self.searched: list[str] = []

    def query(self, query: str, parameters: dict | None = None) -> FakeResult:
        if "positionCaseInsensitive" not in query:
            return super().query(query, parameters)
        parameters = parameters or {}
        assert parameters.get("t0") == TOKEN, "the token must be bound, never interpolated"
        self.calls.append((query, parameters))
        if "'plan_json' AS source" in query and reads(query, "spark_events"):
            self.searched.append("plan_json")
            return FakeResult(list(self.plan_hits))
        if "'findings' AS source" in query and reads(query, "findings"):
            self.searched.append("findings")
            return FakeResult(list(self.findings_hits))
        raise AssertionError(f"unrecognised search statement: {query}")


def _positive() -> _SplitSearch:
    return _SplitSearch(findings_hits=[], plan_hits=[_plan_hit()])


def _empty() -> _SplitSearch:
    return _SplitSearch(findings_hits=[], plan_hits=[])


def test_a_plan_json_hit_reads_the_same_over_both_transports():
    client = _positive()
    direct = _over_mcp(client, "search_kb", ARGUMENTS)
    response = _over_http(_positive(), "GET", PATH)

    assert response.status_code == 200
    assert response.json() == direct

    assert direct["query"] == TOKEN
    assert direct["tokens"] == [TOKEN]
    assert direct["total"] == 1
    [hit] = direct["hits"]
    assert hit["source"] == "plan_json"
    assert hit["job_id"] == "j"
    assert hit["stage_id"] == 2
    assert hit["finding_id"] is None
    assert hit["type"] == ""
    assert hit["severity"] == ""
    assert hit["score"] == 1.0
    assert hit["matched_tokens"] == [TOKEN]
    assert hit["snippet"] == PLAN_SNIPPET
    assert TOKEN in hit["snippet"]
    assert direct["untrusted_fields"] == ["hits[].snippet"]
    assert not any(note.startswith("No match") for note in direct["notes"])
    assert client.searched == ["findings", "plan_json"]


def test_no_plan_json_hit_reads_as_absence_over_both_transports():
    client = _empty()
    direct = _over_mcp(client, "search_kb", ARGUMENTS)
    response = _over_http(_empty(), "GET", PATH)

    assert response.status_code == 200
    assert response.json() == direct
    assert client.searched == ["findings", "plan_json"]
    assert direct["tokens"] == [TOKEN]
    assert direct["hits"] == []
    assert direct["total"] == 0
    assert any(note.startswith("No match") for note in direct["notes"])


def test_the_plan_json_hit_and_its_absence_differ_for_the_same_arguments():
    assert _over_mcp(_positive(), "search_kb", ARGUMENTS) != _over_mcp(_empty(), "search_kb", ARGUMENTS)
