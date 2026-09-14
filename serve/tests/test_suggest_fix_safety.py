"""T9/T14 — `suggest_fix` proposes and never applies.

The whole safety argument for the one non-read-only tool rests on this: it
returns a diff as *data*. If it ever wrote a file, ran git, or reported
`applied=True`, the human-in-the-loop guarantee — and with it the primary
defense against tool poisoning — would be gone.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from pydantic import ValidationError

from apex_mcp import diagnose
from apex_mcp.models import FixSuggestion
from tests.conftest import finding_row, stage_row, transition_row

REPO_ROOT = Path(__file__).resolve().parents[2]
MB = 1 << 20


def _suggest(job_id="job-1", finding_id=None, min_confidence=0.75, findings=None,
             stages=None, transitions=None, verifications=None) -> FixSuggestion:
    return diagnose.suggest_fix(
        job_id,
        finding_id,
        min_confidence,
        findings if findings is not None else [],
        stages if stages is not None else [stage_row(4, p50_ms=20, p99_ms=460)],
        transitions or [],
        verifications or [],
    )


def verification_row(
    *,
    finding_id: str = "finding-1",
    method: str = "predicted",
    safe: int = 1,
    safety_verdict: str = "allow",
    safety_detail: str = "",
    measured_delta_pct: float | None = None,
    replay_reps: int = 0,
    proposed_config: str = '{"spark.sql.adaptive.skewJoin.enabled": "true"}',
) -> dict:
    """One apex.fix_verifications row, shaped like the v0.3 DDL."""
    return {
        "verification_id": "v-1",
        "finding_id": finding_id,
        "job_id": "job-1",
        "app_id": "app-job-1",
        "proposed_config": proposed_config,
        "method": method,
        "predictor": "amdahl_tail_share",
        "predicted_delta_pct": -18.0,
        "predicted_low_pct": -25.0,
        "predicted_high_pct": -8.0,
        "measured_delta_pct": measured_delta_pct,
        "baseline_ms": None,
        "treatment_ms": None,
        "noise_floor_pct": None,
        "replay_reps": replay_reps,
        "bench": "dev:skew_join" if replay_reps else "",
        "shape_fidelity": 0.8 if replay_reps else 0.0,
        "safe": safe,
        "safety_verdict": safety_verdict,
        "safety_detail": safety_detail,
        "confidence": "MEDIUM",
        "confidence_score": 0.62,
        "evidence": "tail share 0.41; amdahl bound",
        "caveats": "single bench shape",
        "verify_version": "0.3.0",
        "verified_at": "2026-08-20T10:00:00.000",
    }


# -- the gate is structural, not conventional ------------------------------
def test_applied_and_approval_flags_cannot_be_overridden():
    """Not "we remember to set it" — the schema forbids the other value."""
    with pytest.raises(ValidationError):
        FixSuggestion(
            job_id="j", source="none", title="t", rationale="r",
            confidence=1.0, min_confidence=0.0, applied=True,
        )
    with pytest.raises(ValidationError):
        FixSuggestion(
            job_id="j", source="none", title="t", rationale="r",
            confidence=1.0, min_confidence=0.0, requires_human_approval=False,
        )


@pytest.mark.parametrize(
    "case",
    [
        {"findings": [finding_row(confidence_score=0.99)]},   # findings path
        {"findings": []},                                      # heuristic path
        {"min_confidence": 0.99},                              # gated path
        {"min_confidence": 0.0},                               # wide-open path
        {"stages": []},                                        # no telemetry
        {"findings": [], "stages": [stage_row(1, p50_ms=100, p99_ms=100)]},  # healthy
        {"transitions": [transition_row("skew_split")]},       # ground-truth path
        {"finding_id": "does-not-exist"},                      # bad finding_id
    ],
)
def test_every_path_returns_applied_false(case):
    suggestion = _suggest(**case)
    assert suggestion.applied is False
    assert suggestion.requires_human_approval is True


def test_calling_suggest_fix_leaves_the_working_tree_untouched():
    before = subprocess.run(
        ["git", "status", "--porcelain"], cwd=REPO_ROOT,
        capture_output=True, text=True, check=True,
    ).stdout
    _suggest(findings=[finding_row(confidence_score=0.99)])
    _suggest(findings=[])
    after = subprocess.run(
        ["git", "status", "--porcelain"], cwd=REPO_ROOT,
        capture_output=True, text=True, check=True,
    ).stdout
    assert before == after


def test_the_proposed_file_does_not_exist_on_disk():
    suggestion = _suggest(findings=[finding_row(confidence_score=0.99)])
    assert "conf/apex-suggested.conf" in suggestion.proposed_diff
    assert not (REPO_ROOT / "conf" / "apex-suggested.conf").exists()
    assert not (Path.cwd() / "conf" / "apex-suggested.conf").exists()


# -- the confidence gate ---------------------------------------------------
def test_below_min_confidence_downgrades_to_advisory_with_no_diff():
    suggestion = _suggest(
        findings=[finding_row(confidence_score=0.55)], min_confidence=0.75
    )
    assert suggestion.gated is True
    assert suggestion.advisory_only is True
    assert suggestion.proposed_diff == ""
    assert suggestion.pr_body == ""
    assert any("min_confidence" in w for w in suggestion.warnings)


def test_at_or_above_min_confidence_yields_a_diff():
    suggestion = _suggest(
        findings=[finding_row(confidence_score=0.90)], min_confidence=0.75
    )
    assert suggestion.gated is False
    assert suggestion.proposed_diff
    assert suggestion.pr_body
    assert suggestion.proposed_config


def test_confidence_comes_from_the_raw_score_not_the_tier():
    low_score_high_tier = _suggest(
        findings=[finding_row(confidence="HIGH", confidence_score=0.30)],
        min_confidence=0.75,
    )
    assert low_score_high_tier.confidence == 0.3
    assert low_score_high_tier.gated is True


def test_pre_v0_2_rows_fall_back_to_the_enum_tier():
    suggestion = _suggest(
        findings=[finding_row(confidence="HIGH", confidence_score=0.0)]
    )
    assert suggestion.confidence == 0.9
    assert suggestion.source == "findings_table"


# -- the stub path ---------------------------------------------------------
def test_heuristic_path_is_labelled_as_a_stub():
    suggestion = _suggest(findings=[])
    assert suggestion.source == "spark_events_heuristic"
    assert any("STUB" in note for note in suggestion.notes)


def test_findings_path_is_preferred_over_heuristics():
    suggestion = _suggest(findings=[finding_row(confidence_score=0.99)])
    assert suggestion.source == "findings_table"
    assert not any("STUB" in note for note in suggestion.notes)


def test_specific_finding_id_selects_that_finding():
    findings = [
        finding_row(finding_id="f1", stage_id=2, confidence_score=0.9),
        finding_row(finding_id="f2", stage_id=7, type="SPILL", confidence_score=0.9),
    ]
    suggestion = _suggest(findings=findings, finding_id="f2")
    assert suggestion.target_stage_id == 7
    assert "spark.memory.fraction" in suggestion.proposed_config


def test_unknown_finding_id_falls_back_and_says_so():
    suggestion = _suggest(
        findings=[finding_row(finding_id="f1")], finding_id="nope"
    )
    assert any("was not found" in note for note in suggestion.notes)


def test_no_telemetry_returns_a_zero_confidence_advisory():
    suggestion = _suggest(stages=[], findings=[])
    assert suggestion.source == "none"
    assert suggestion.confidence == 0.0
    assert suggestion.advisory_only is True


def test_healthy_run_proposes_nothing():
    suggestion = _suggest(findings=[], stages=[stage_row(1, p50_ms=100, p99_ms=100)])
    assert suggestion.title == "Nothing to fix"
    assert suggestion.proposed_diff == ""


# -- the diff itself -------------------------------------------------------
def test_diff_creates_a_new_file_so_applying_it_destroys_nothing():
    suggestion = _suggest(findings=[finding_row(confidence_score=0.99)])
    lines = suggestion.proposed_diff.splitlines()
    assert lines[0] == "--- /dev/null"
    assert lines[1].startswith("+++ b/")
    # every content line is an addition — no deletions, no context to clobber
    assert all(line.startswith("+") for line in lines[3:])


def test_diff_is_inert_config_not_an_executable_script():
    suggestion = _suggest(findings=[finding_row(confidence_score=0.99)])
    body = suggestion.proposed_diff
    assert "#!" not in body
    for token in ("rm ", "curl", "sh -c", "$(", "`", "&&", "|"):
        assert token not in body


def test_hunk_header_line_count_matches_the_body():
    suggestion = _suggest(findings=[finding_row(confidence_score=0.99)])
    lines = suggestion.proposed_diff.splitlines()
    declared = int(lines[2].split("+1,")[1].split(" ")[0])
    assert declared == len(lines) - 3


# -- provenance: what verify already concluded -----------------------------
# suggest_fix used to propose a diff with no idea the same fix had already been
# predicted, measured, or refused as unsafe. These tests pin the disclosure —
# and pin that disclosing is ALL it does, except for withholding the diff on a
# refusal.
_VERIFIED_FINDING = finding_row(finding_id="finding-1", confidence_score=0.99)


def test_suggestion_reports_prior_verification():
    """B-1 — the predicted range and any measurement reach the caller."""
    suggestion = _suggest(
        findings=[_VERIFIED_FINDING],
        verifications=[
            verification_row(method="replayed", measured_delta_pct=-11.0,
                             replay_reps=5)
        ],
    )

    assert suggestion.verification is not None
    assert suggestion.verification.predicted_delta_pct == -18.0
    assert suggestion.verification.measured_delta_pct == -11.0

    notes = " ".join(suggestion.notes)
    assert "predicted 18.0% faster" in notes
    assert "range 25.0% faster to 8.0% faster" in notes
    assert "measured 11.0% faster" in notes
    assert "5 rep(s)" in notes


def test_an_unreplayed_prediction_is_labelled_as_unmeasured():
    suggestion = _suggest(
        findings=[_VERIFIED_FINDING], verifications=[verification_row()]
    )

    assert suggestion.verification.measured_delta_pct is None
    assert any("never replayed" in note for note in suggestion.notes)


def test_refused_fix_is_not_presented_as_ready():
    """B-2 — proposing a fix verify refused is the worst output this lane can
    produce, so the refusal leads the warnings and no diff is handed over."""
    suggestion = _suggest(
        findings=[_VERIFIED_FINDING],
        verifications=[
            verification_row(
                method="refused", safe=0, safety_verdict="block_size",
                safety_detail="optimizedPlan.stats.sizeInBytes=8.0 EiB (unknown)",
            )
        ],
    )

    assert suggestion.warnings[0].startswith("REFUSED BY THE VERIFY LANE")
    assert "block_size" in suggestion.warnings[0]
    assert suggestion.advisory_only is True
    assert suggestion.proposed_diff == ""
    assert suggestion.pr_body == ""
    # the recipe is still named — the user must be able to see WHAT was refused
    assert suggestion.proposed_config


def test_a_refusal_is_not_collapsed_into_low_confidence():
    """The confidence gate and the safety gate mean different things."""
    suggestion = _suggest(
        findings=[_VERIFIED_FINDING],
        verifications=[verification_row(safe=0, safety_verdict="block_ast")],
    )

    assert suggestion.gated is False          # confidence was never the problem
    assert suggestion.confidence == 0.99
    assert suggestion.advisory_only is True   # but it is still not ready to apply
    assert "not a low confidence score" in suggestion.warnings[0]


def test_unverified_finding_output_is_unchanged():
    """B-3 — a finding the verify lane never looked at behaves exactly as before."""
    without = _suggest(findings=[_VERIFIED_FINDING])
    with_empty = _suggest(findings=[_VERIFIED_FINDING], verifications=[])

    assert without.model_dump() == with_empty.model_dump()
    assert without.verification is None
    assert without.proposed_diff
    assert without.advisory_only is False


def test_a_verification_for_a_different_finding_is_not_attached():
    """Verifications are keyed to a finding; the wrong one must not leak in."""
    suggestion = _suggest(
        findings=[_VERIFIED_FINDING],
        verifications=[verification_row(finding_id="some-other-finding")],
    )

    assert suggestion.verification is None
    assert suggestion.proposed_diff


def test_a_verification_of_a_different_overlay_says_so():
    """A verdict on other settings does not transfer to these ones."""
    suggestion = _suggest(
        findings=[_VERIFIED_FINDING],
        verifications=[
            verification_row(proposed_config='{"spark.executor.memory": "8g"}')
        ],
    )

    assert any("DIFFERENT overlay" in note for note in suggestion.notes)


def test_the_heuristic_path_carries_no_verification():
    """No finding means no finding_id to key a verification to."""
    suggestion = _suggest(findings=[], verifications=[verification_row()])

    assert suggestion.source == "spark_events_heuristic"
    assert suggestion.verification is None


def test_a_gated_suggestion_still_discloses_its_verification():
    suggestion = _suggest(
        findings=[finding_row(finding_id="finding-1", confidence_score=0.40)],
        min_confidence=0.75,
        verifications=[verification_row()],
    )

    assert suggestion.gated is True
    assert suggestion.verification is not None


@pytest.mark.parametrize(
    "verifications",
    [
        [],
        [verification_row()],
        [verification_row(method="replayed", measured_delta_pct=0.0, replay_reps=3)],
        [verification_row(method="refused", safe=0, safety_verdict="block_size")],
        [verification_row(finding_id="unrelated")],
    ],
)
def test_disclosure_never_weakens_the_never_applies_guarantee(verifications):
    """B-4 — the whole safety argument survives every disclosure path."""
    suggestion = _suggest(findings=[_VERIFIED_FINDING], verifications=verifications)

    assert suggestion.applied is False
    assert suggestion.requires_human_approval is True


def test_disclosing_a_verification_leaves_the_working_tree_untouched():
    """B-4 — reading a verdict is still a read."""
    before = subprocess.run(
        ["git", "status", "--porcelain"], cwd=REPO_ROOT,
        capture_output=True, text=True, check=True,
    ).stdout
    _suggest(findings=[_VERIFIED_FINDING], verifications=[verification_row()])
    _suggest(
        findings=[_VERIFIED_FINDING],
        verifications=[verification_row(safe=0, safety_verdict="block_size")],
    )
    after = subprocess.run(
        ["git", "status", "--porcelain"], cwd=REPO_ROOT,
        capture_output=True, text=True, check=True,
    ).stdout
    assert before == after
