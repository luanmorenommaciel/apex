"""The verify_fix payload types.

A verdict about whether a fix works is exactly the payload a client must be
able to reject if it is malformed, so the shape is asserted here rather than
left to whatever the store happens to return.

The one convention this file exists to protect: ``predicted_delta_pct`` is
SIGNED and negative means FASTER. A sign error reports a regression as an
improvement, which is the worst wrong answer this lane can give.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from apex_mcp.models import FixVerdict, VerificationView


def _predicted_row(**overrides) -> dict:
    row = {
        "verification_id": "v-1",
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


# -- B-1: a prediction that was never replayed -----------------------------
def test_predicted_only_row_validates():
    view = VerificationView.model_validate(_predicted_row())

    assert view.method == "predicted"
    assert view.measured_delta_pct is None
    assert view.baseline_ms is None
    assert view.replay_reps == 0
    assert view.predicted_delta_pct == -18.0


def test_measured_zero_is_not_the_same_answer_as_unmeasured():
    """0.0 means "measured, no change"; None means never replayed."""
    unmeasured = VerificationView.model_validate(_predicted_row())
    measured = VerificationView.model_validate(
        _predicted_row(method="replayed", measured_delta_pct=0.0, replay_reps=5)
    )

    assert unmeasured.measured_delta_pct is None
    assert measured.measured_delta_pct == 0.0


def test_uint8_safety_gate_becomes_a_boolean():
    assert VerificationView.model_validate(_predicted_row(safe=0)).safe is False
    assert VerificationView.model_validate(_predicted_row(safe=1)).safe is True


def test_proposed_config_is_exposed_as_a_mapping():
    view = VerificationView.model_validate(_predicted_row())
    assert view.proposed_config == {"spark.sql.shuffle.partitions": "200"}


def test_unparseable_proposed_config_does_not_hide_the_safety_verdict():
    """A malformed overlay must not fail the row that carries the refusal."""
    view = VerificationView.model_validate(
        _predicted_row(
            proposed_config="{not json",
            safe=0,
            safety_verdict="block_size",
        )
    )

    assert view.proposed_config == {}
    assert view.safety_verdict == "block_size"


def test_driver_datetimes_are_coerced_to_strings():
    view = VerificationView.model_validate(
        _predicted_row(verified_at=datetime(2026, 8, 20, 10, 0, 0))
    )
    assert view.verified_at == "2026-08-20T10:00:00"


# -- B-2: the sign convention is in the schema, not just in a comment ------
@pytest.mark.parametrize(
    "field",
    ["predicted_delta_pct", "predicted_low_pct", "predicted_high_pct",
     "measured_delta_pct"],
)
def test_sign_convention_is_documented(field):
    """FastMCP publishes these descriptions; a client reads them, not our
    source comments. Every delta field must state that negative = faster."""
    description = VerificationView.model_fields[field].description or ""

    assert "negative" in description.lower(), field
    assert "faster" in description.lower(), field


def test_the_interval_bounds_say_they_are_ordered_numerically():
    """`low` is the MOST improvement, because negative means faster — naming
    them by optimism instead of by number is how the sign gets flipped."""
    low = VerificationView.model_fields["predicted_low_pct"].description or ""
    high = VerificationView.model_fields["predicted_high_pct"].description or ""

    assert "MOST improvement" in low
    assert "LEAST improvement" in high


def test_a_safety_block_is_documented_as_distinct_from_low_confidence():
    description = VerificationView.model_fields["safety_verdict"].description or ""
    assert "not a low confidence" in description.lower()


# -- B-3: the verdict carries its derivation, and claims nothing untrusted --
def test_verdict_carries_evidence_and_caveats():
    verdict = FixVerdict(
        job_id="job-1",
        finding_id="finding-1",
        status="verified",
        verification_count=1,
        summary="predicted 18.0% faster (range 25.0%..8.0% faster), MEDIUM confidence",
        verifications=[VerificationView.model_validate(_predicted_row())],
        evidence=["tail share 0.41; partition sizing model"],
        caveats=["not replayed"],
    )

    payload = verdict.model_dump()

    assert payload["evidence"] == ["tail share 0.41; partition sizing model"]
    assert payload["caveats"] == ["not replayed"]
    # Every field here is Apex-authored: the verify lane writes evidence and
    # caveats, and proposed_config holds Spark conf only. Marking any of it
    # untrusted would devalue the marker where it actually matters.
    assert payload["untrusted_fields"] == []


def test_not_assessed_is_a_status_and_not_an_empty_success():
    verdict = FixVerdict(job_id="job-1", status="not_assessed")

    assert verdict.status == "not_assessed"
    assert verdict.verifications == []
    assert verdict.verification_count == 0


def test_blocked_is_a_separate_field_from_confidence():
    """A safety block and a weak prediction are different claims."""
    verdict = FixVerdict(
        job_id="job-1",
        status="verified",
        blocked=True,
        blocked_reason="block_size: optimizedPlan.stats.sizeInBytes unknown",
    )

    assert verdict.blocked is True
    assert "block_size" in verdict.blocked_reason
