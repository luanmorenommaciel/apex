"""`verify_fix` — the MCP surface over the verify lane.

Serve does not decide whether a fix works; the verify lane already did, and
wrote the answer to apex.fix_verifications. These tests pin what this tool is
allowed to say about that answer:

  * a safety BLOCK is surfaced as a block, never softened into low confidence;
  * "no rows" is reported as `not_assessed`, never as an empty success;
  * the SIGNED delta is rendered with negative meaning faster.
"""

from __future__ import annotations

import asyncio

import pytest

from apex_mcp import diagnose
from apex_mcp.ch import ReadStore
from apex_mcp.server import create_server


class _VerifyClient:
    """Serves apex.fix_verifications plus its table probe, nothing else.

    conftest's FakeClient routes on job_id and falls through to spark_events,
    which would silently answer the verifications query with stage rows.
    """

    def __init__(self, rows: list[dict] | None = None, table: bool = True) -> None:
        self.rows = rows or []
        self.table = table

    def query(self, query: str, parameters: dict | None = None):
        if "system.columns" in query:
            payload = [{"name": "verification_id"}] if self.table else []
        elif "apex.fix_verifications" in query:
            finding_id = (parameters or {}).get("finding_id") or ""
            payload = [
                r for r in self.rows
                if not finding_id or r["finding_id"] == finding_id
            ]
        else:
            payload = []
        return type("R", (), {"named_results": lambda _self: list(payload)})()


def _row(verification_id: str = "v-1", **overrides) -> dict:
    row = {
        "verification_id": verification_id,
        "finding_id": "finding-1",
        "job_id": "job-1",
        "app_id": "app-job-1",
        "proposed_config": '{"spark.sql.shuffle.partitions": "200"}',
        "method": "predicted",
        "predictor": "partition_sizing",
        "predicted_delta_pct": -18.0,
        "predicted_low_pct": -25.0,
        "predicted_high_pct": -8.0,
        "measured_delta_pct": None,
        "baseline_ms": None,
        "treatment_ms": None,
        "noise_floor_pct": None,
        "replay_reps": 0,
        "bench": "",
        "shape_fidelity": 0.0,
        "safe": 1,
        "safety_verdict": "allow",
        "safety_detail": "",
        "confidence": "MEDIUM",
        "confidence_score": 0.62,
        "evidence": "tail share 0.41; partition sizing model",
        "caveats": "not replayed",
        "verify_version": "0.3.0",
        "verified_at": "2026-08-20T10:00:00.000",
    }
    row.update(overrides)
    return row


def _call(rows, table=True, **arguments):
    server = create_server(ReadStore(_VerifyClient(rows, table=table)))
    arguments.setdefault("job_id", "job-1")
    result = asyncio.run(server.call_tool("verify_fix", arguments))
    return result[1] if isinstance(result, tuple) else result


# -- B-1: registered, and registered read-only ------------------------------
def test_verify_fix_is_registered_read_only():
    server = create_server(ReadStore(_VerifyClient()))
    tool = {t.name: t for t in asyncio.run(server.list_tools())}["verify_fix"]

    assert tool.annotations is not None
    assert tool.annotations.readOnlyHint is True
    assert tool.annotations.openWorldHint is False
    assert tool.outputSchema


def test_verify_fix_docstring_states_the_sign_convention():
    server = create_server(ReadStore(_VerifyClient()))
    tool = {t.name: t for t in asyncio.run(server.list_tools())}["verify_fix"]

    assert "negative means FASTER" in (tool.description or "")


# -- B-2: the prediction, the safety verdict and the confidence -------------
def test_predicted_verification_reports_range_safety_and_confidence():
    payload = _call([_row()])

    assert payload["status"] == "verified"
    assert payload["verification_count"] == 1
    assert "18.0% faster" in payload["summary"]
    assert "25.0% faster" in payload["summary"]   # interval low
    assert "8.0% faster" in payload["summary"]    # interval high
    assert "MEDIUM confidence" in payload["summary"]
    assert "safety: allow" in payload["summary"]
    assert payload["evidence"] == ["tail share 0.41; partition sizing model"]
    assert payload["caveats"] == ["not replayed"]


def test_a_positive_delta_is_reported_as_slower():
    """The sign is the whole verdict: +12 must never read as an improvement."""
    payload = _call([_row(predicted_delta_pct=12.0)])

    assert "12.0% slower" in payload["summary"]
    assert "12.0% faster" not in payload["summary"]


def test_a_replayed_verification_reports_the_measurement():
    payload = _call(
        [_row(method="replayed", measured_delta_pct=-11.0, replay_reps=5,
              bench="dev:skew_join")]
    )

    assert "measured 11.0% faster" in payload["summary"]
    assert "5 rep(s)" in payload["summary"]
    assert "dev:skew_join" in payload["summary"]


def test_a_measurement_under_the_noise_floor_is_not_reported_as_a_number():
    payload = _call(
        [_row(method="replayed", measured_delta_pct=-0.4, noise_floor_pct=3.0,
              replay_reps=5)]
    )

    assert "indistinguishable from zero" in payload["summary"]


def test_an_unreplayed_prediction_says_so():
    payload = _call([_row()])
    assert any("never replayed" in note for note in payload["notes"])


def test_finding_id_narrows_the_verdict():
    payload = _call(
        [_row("v-1", finding_id="finding-1"),
         _row("v-2", finding_id="finding-2")],
        finding_id="finding-2",
    )

    assert payload["verification_count"] == 1
    assert payload["verifications"][0]["finding_id"] == "finding-2"


# -- B-3: no rows is an answer, not an empty success ------------------------
def test_no_verification_rows_reports_not_assessed():
    payload = _call([])

    assert payload["status"] == "not_assessed"
    assert payload["verifications"] == []
    assert "has not assessed" in payload["summary"]
    assert "not a clean bill of health" in payload["summary"]


def test_an_unapplied_additive_table_says_which_table_is_missing():
    """v0.3 is additive; an older cluster degrades instead of erroring."""
    payload = _call([_row()], table=False)

    assert payload["status"] == "not_assessed"
    assert any("apex.fix_verifications" in note for note in payload["notes"])


# -- B-4: a block is a block ------------------------------------------------
@pytest.mark.parametrize(
    "row",
    [
        _row(method="refused", safe=0, safety_verdict="block_size",
             safety_detail="optimizedPlan.stats.sizeInBytes=8.0 EiB (unknown)"),
        _row(safe=0, safety_verdict="block_ast", safety_detail="udf in plan"),
        _row(safe=1, safety_verdict="block_no_bench"),
    ],
)
def test_a_safety_block_is_surfaced_not_hidden(row):
    payload = _call([row])

    assert payload["blocked"] is True
    assert payload["blocked_reason"].startswith(row["safety_verdict"])
    assert payload["summary"].startswith("REFUSED by the verify lane")


def test_a_block_is_not_collapsed_into_low_confidence():
    """HIGH confidence in a refused fix is exactly the trap: the block must
    still be the first thing the reader sees."""
    payload = _call(
        [_row(method="refused", safe=0, safety_verdict="block_size",
              confidence="HIGH", confidence_score=0.95)]
    )

    assert payload["blocked"] is True
    assert "REFUSED" in payload["summary"]
    assert "HIGH confidence" in payload["summary"]


def test_an_allowed_verification_is_not_marked_blocked():
    assert _call([_row()])["blocked"] is False


# -- the payload claims nothing untrusted -----------------------------------
def test_the_verdict_marks_no_field_untrusted():
    """Every field here is Apex-authored; the marker must not be diluted."""
    assert _call([_row()])["untrusted_fields"] == []


# -- serve reports, it never re-decides -------------------------------------
def test_build_verdict_is_pure_and_recomputes_no_prediction():
    """The predicted numbers come out exactly as the verify lane wrote them."""
    verdict = diagnose.build_verdict("job-1", None, [_row()])

    view = verdict.verifications[0]
    assert view.predicted_delta_pct == -18.0
    assert view.predicted_low_pct == -25.0
    assert view.predicted_high_pct == -8.0
    assert view.predictor == "partition_sizing"


def test_multiple_verifications_summarize_the_newest_and_keep_the_rest():
    payload = _call([_row("v-new"), _row("v-old", predicted_delta_pct=-2.0)])

    assert payload["verification_count"] == 2
    assert "18.0% faster" in payload["summary"]
    assert any("newest" in note for note in payload["notes"])
