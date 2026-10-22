"""SRP-22 / P7.10 — one proposal source across both doors.

The console (``front``) renders ``apex.fix_verifications.proposed_config`` for a
finding — the newest row by ``verified_at`` — through ``parseProposal``
(JSON.parse, then ``String()`` of each scalar). MCP ``suggest_fix`` must hand
over the SAME overlay for the same finding: in ``proposed_config``, in the
diff lines and in the PR body. When no usable row exists, the heuristic recipe
is the proposal, in the same deterministic (sorted-key) order.
"""

from __future__ import annotations

import json
import pytest

from apex_mcp import diagnose
from apex_mcp.models import FixSuggestion, VerificationView
from tests.conftest import finding_row, stage_row

FINDING = finding_row(finding_id="finding-1", confidence_score=0.99)  # SKEW_ON_JOIN
SKEW_RECIPE = diagnose._RECIPES["skew"][1]

# What the verify lane writes: json.dumps(dict[str, str], sort_keys=True).
STORED = json.dumps(
    {
        "spark.sql.shuffle.partitions": "800",
        "spark.sql.adaptive.enabled": "true",
    },
    sort_keys=True,
)


def _row(
    proposed_config: str = STORED,
    *,
    verification_id: str = "v-1",
    finding_id: str = "finding-1",
    method: str = "predicted",
    safe: int = 1,
    safety_verdict: str = "allow",
    verified_at: str = "2026-08-20T10:00:00.000",
) -> dict:
    return {
        "verification_id": verification_id,
        "finding_id": finding_id,
        "job_id": "job-1",
        "app_id": "app-job-1",
        "proposed_config": proposed_config,
        "method": method,
        "predictor": "partition_sizing",
        "predicted_delta_pct": -12.0,
        "predicted_low_pct": -20.0,
        "predicted_high_pct": -4.0,
        "measured_delta_pct": None,
        "safe": safe,
        "safety_verdict": safety_verdict,
        "confidence": "MEDIUM",
        "confidence_score": 0.6,
        "evidence": "partition sizing bound",
        "caveats": "single bench shape",
        "verify_version": "0.3.0",
        "verified_at": verified_at,
    }


def _suggest(verifications, *, min_confidence: float = 0.75, findings=None) -> FixSuggestion:
    return diagnose.suggest_fix(
        "job-1",
        None,
        min_confidence,
        [FINDING] if findings is None else findings,
        [stage_row(2, p50_ms=20, p99_ms=460)],
        [],
        verifications,
    )


def _js_string(value: object) -> str:
    """``String(v)`` for the JSON scalars ``parseProposal`` accepts."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and value.is_integer() and abs(value) < 1e21:
        return str(int(value))
    return str(value)


def console_overlay(stored: str) -> dict[str, str] | None:
    """What the console shows: a faithful port of ``parseProposal``'s overlay
    branch (front/src/contract/rules.ts). ``None`` = not an overlay."""
    trimmed = stored.strip()
    if not trimmed:
        return None

    def _reject(_: str) -> object:  # JSON.parse rejects NaN / Infinity
        raise ValueError

    try:
        parsed = json.loads(trimmed, parse_constant=_reject)
    except ValueError:
        return None
    if not isinstance(parsed, dict):
        return None
    out: dict[str, str] = {}
    for key, value in parsed.items():
        if isinstance(value, (str, bool, int, float)):
            out[key] = _js_string(value)
        else:
            return None
    return out


def _diff_pairs(diff: str) -> list[tuple[str, str]]:
    pairs = []
    for line in diff.splitlines():
        if not line.startswith("+") or line.startswith("+++") or line.startswith("+#"):
            continue
        key, _, value = line[1:].partition(" ")
        pairs.append((key, value))
    return pairs


# -- the divergence this ticket closes ---------------------------------------
def test_both_doors_show_the_same_overlay_for_the_same_finding():
    suggestion = _suggest([_row()])
    console = console_overlay(STORED)

    assert console is not None
    assert suggestion.proposed_config == console
    assert suggestion.proposed_config != SKEW_RECIPE
    # the diff carries exactly that overlay, in canonical (sorted) order
    assert _diff_pairs(suggestion.proposed_diff) == sorted(console.items())
    assert list(suggestion.proposed_config) == sorted(console)
    for key, value in console.items():
        assert f"- `{key}` = `{value}`" in suggestion.pr_body


def test_the_note_names_the_stored_overlay_as_the_source():
    suggestion = _suggest([_row()])

    assert not any("DIFFERENT overlay" in n for n in suggestion.notes)
    assert any(
        "verify lane's stored overlay" in n and "differs from the heuristic recipe" in n
        for n in suggestion.notes
    )


def test_a_matching_overlay_does_not_claim_a_difference():
    stored = json.dumps(SKEW_RECIPE, sort_keys=True)
    suggestion = _suggest([_row(stored)])

    assert suggestion.proposed_config == console_overlay(stored)
    assert any("verify lane's stored overlay" in n for n in suggestion.notes)
    assert not any("differs from the heuristic recipe" in n for n in suggestion.notes)


# -- fallbacks to the recipe -------------------------------------------------
def test_no_row_keeps_the_recipe_in_canonical_order():
    suggestion = _suggest([])

    assert suggestion.verification is None
    assert suggestion.proposed_config == SKEW_RECIPE
    assert list(suggestion.proposed_config) == sorted(SKEW_RECIPE)
    assert _diff_pairs(suggestion.proposed_diff) == sorted(SKEW_RECIPE.items())


@pytest.mark.parametrize(
    "stored",
    ["{not json", "", "[]", '"x"', "{}", '{"a": null}', '{"a": {"b": "c"}}', '{"a": NaN}'],
)
def test_an_unusable_stored_overlay_falls_back_to_the_recipe(stored):
    """Whatever the console cannot render as an overlay is not authoritative."""
    suggestion = _suggest([_row(stored)])

    assert console_overlay(stored) in (None, {})
    assert suggestion.verification is not None
    assert suggestion.proposed_config == SKEW_RECIPE
    assert _diff_pairs(suggestion.proposed_diff) == sorted(SKEW_RECIPE.items())
    assert not any("verify lane's stored overlay" in n for n in suggestion.notes)


def test_scalar_values_are_stringified_like_the_console():
    stored = '{"spark.b": true, "spark.a": 5, "spark.c": 0.7, "spark.d": 5.0}'
    suggestion = _suggest([_row(stored)])

    assert suggestion.proposed_config == console_overlay(stored)
    assert suggestion.proposed_config == {
        "spark.a": "5", "spark.b": "true", "spark.c": "0.7", "spark.d": "5",
    }
    assert list(suggestion.proposed_config) == ["spark.a", "spark.b", "spark.c", "spark.d"]
    # the attached view agrees with the proposal it sits beside
    assert suggestion.verification.proposed_config == suggestion.proposed_config


# -- the gates still hold ----------------------------------------------------
def test_a_refused_row_shows_its_overlay_but_hands_over_nothing():
    suggestion = _suggest(
        [_row(method="refused", safe=0, safety_verdict="block_size")]
    )

    assert suggestion.proposed_config == console_overlay(STORED)
    assert suggestion.proposed_diff == ""
    assert suggestion.pr_body == ""
    assert suggestion.advisory_only is True
    assert suggestion.applied is False


def test_the_confidence_gate_still_withholds_everything():
    suggestion = _suggest(
        [_row()],
        findings=[finding_row(finding_id="finding-1", confidence_score=0.40)],
    )

    assert suggestion.gated is True
    assert suggestion.proposed_config == {}
    assert suggestion.proposed_diff == ""
    assert suggestion.pr_body == ""


def test_the_newest_row_is_the_source_like_the_console():
    """Store order is newest-first (ORDER BY verified_at DESC), and the console
    takes ORDER BY verified_at DESC LIMIT 1 — both pick the first row."""
    newer = json.dumps({"spark.sql.shuffle.partitions": "1200"}, sort_keys=True)
    rows = [
        _row(newer, verification_id="v-2", verified_at="2026-08-21T10:00:00.000"),
        _row(STORED, verification_id="v-1", verified_at="2026-08-20T10:00:00.000"),
    ]
    console_pick = max(rows, key=lambda r: r["verified_at"])["proposed_config"]

    suggestion = _suggest(rows)

    assert suggestion.proposed_config == console_overlay(console_pick)
    assert suggestion.verification.verification_id == "v-2"


def test_the_heuristic_path_is_unchanged():
    suggestion = _suggest([_row()], findings=[])

    assert suggestion.source == "spark_events_heuristic"
    assert suggestion.verification is None
    assert not any("verify lane's stored overlay" in n for n in suggestion.notes)


@pytest.mark.parametrize(
    "overlay",
    [
        {"spark.a": "1\n+spark.injected true"},
        {"spark a": "1"},
        {"spark.a": "`x`"},
        {"spark.a": "a\rb"},
    ],
)
def test_an_overlay_that_cannot_be_one_conf_line_gets_no_diff(overlay):
    """Stored values are data: they stay visible but are never allowed to
    forge extra diff lines or break out of the PR body's code span."""
    stored = json.dumps(overlay, sort_keys=True)
    suggestion = _suggest([_row(stored)])

    assert suggestion.proposed_config == console_overlay(stored)
    assert suggestion.proposed_diff == ""
    assert suggestion.pr_body == ""
    assert suggestion.advisory_only is True
    assert any("single conf line" in w for w in suggestion.warnings)


def test_spaces_inside_a_value_still_render():
    """extraJavaOptions-style values legitimately contain spaces."""
    stored = json.dumps({"spark.executor.extraJavaOptions": "-XX:+UseG1GC -Dx=1"})
    suggestion = _suggest([_row(stored)])

    assert _diff_pairs(suggestion.proposed_diff) == [
        ("spark.executor.extraJavaOptions", "-XX:+UseG1GC -Dx=1")
    ]


# -- the helper ----------------------------------------------------------------
def test_normalize_overlay_is_sorted_and_stringly_typed():
    out = diagnose.normalize_overlay({"b": "2", "a": "1"})
    assert out == {"a": "1", "b": "2"}
    assert list(out) == ["a", "b"]


def test_view_parse_matches_the_console_for_canonical_rows():
    view = VerificationView.model_validate(_row())
    assert view.proposed_config == console_overlay(STORED)


# -- review follow-ups ---------------------------------------------------------
@pytest.mark.parametrize(
    "raw",
    [
        '{"spark.a": 1e400}',
        '{"spark.a": -1e400}',
        {"spark.a": float("nan")},
        {"spark.a": float("inf")},
        {"spark.a": float("-inf"), "spark.b": "1"},
    ],
)
def test_a_non_finite_number_invalidates_the_overlay_without_raising(raw):
    """1e400 parses to infinity; it must never take the whole row down."""
    row = _row(method="refused", safe=0, safety_verdict="block_size")
    row["proposed_config"] = raw

    view = VerificationView.model_validate(row)
    assert view.proposed_config == {}
    assert view.safe is False
    assert view.safety_verdict == "block_size"

    verdict = diagnose.build_verdict("job-1", "finding-1", [row])
    assert verdict.status == "verified"
    assert verdict.blocked is True

    suggestion = _suggest([row])
    assert suggestion.proposed_config == SKEW_RECIPE
    assert suggestion.advisory_only is True


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1e20, "100000000000000000000"),
        (float(2**60), "1152921504606847000"),  # node: String(2**60)
        (2.0**53, "9007199254740992"),
        (5.0, "5"),
    ],
)
def test_whole_number_floats_render_like_javascript(value, expected):
    view = VerificationView.model_validate(_row(json.dumps({"spark.a": value})))
    assert view.proposed_config == {"spark.a": expected}


def test_the_pr_body_discloses_the_verified_overlay_source():
    suggestion = _suggest([_row()])

    assert "overlay the verify lane evaluated (verification `v-1`" in suggestion.pr_body
    assert "differ from the heuristic recipe" in suggestion.pr_body


def test_the_pr_body_does_not_claim_a_difference_when_there_is_none():
    suggestion = _suggest([_row(json.dumps(SKEW_RECIPE, sort_keys=True))])

    assert "overlay the verify lane evaluated" in suggestion.pr_body
    assert "differ from the heuristic recipe" not in suggestion.pr_body


def test_the_pr_body_neutralizes_the_verification_id():
    suggestion = _suggest([_row(verification_id="v-1`\n+spark.injected true")])

    assert "\n+spark.injected" not in suggestion.pr_body
    assert "v-1' +spark.injected true" in suggestion.pr_body


def test_a_recipe_only_pr_body_carries_no_source_line():
    assert "verify lane evaluated" not in _suggest([]).pr_body


@pytest.mark.parametrize("stored", ["", "{not json", '{"a": null}'])
def test_an_unreadable_overlay_says_the_verdict_does_not_transfer(stored):
    suggestion = _suggest([_row(stored)])

    assert suggestion.proposed_config == SKEW_RECIPE
    assert any(
        "no readable overlay" in w and "does not transfer to the recipe" in w
        for w in suggestion.warnings
    )


def test_an_unreadable_refused_overlay_keeps_the_refusal_first():
    suggestion = _suggest(
        [_row("{not json", method="refused", safe=0, safety_verdict="block_ast")]
    )

    assert suggestion.warnings[0].startswith("REFUSED BY THE VERIFY LANE")
    assert any("no readable overlay" in w for w in suggestion.warnings)
    assert suggestion.proposed_diff == ""


def test_a_readable_overlay_carries_no_unreadable_warning():
    assert not any("no readable overlay" in w for w in _suggest([_row()]).warnings)
