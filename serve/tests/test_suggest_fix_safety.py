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
             stages=None, transitions=None) -> FixSuggestion:
    return diagnose.suggest_fix(
        job_id,
        finding_id,
        min_confidence,
        findings if findings is not None else [],
        stages if stages is not None else [stage_row(4, p50_ms=20, p99_ms=460)],
        transitions or [],
    )


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
