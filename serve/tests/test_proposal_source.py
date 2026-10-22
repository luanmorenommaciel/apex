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
from apex_mcp.models import JS_TRIM_CHARS, FixSuggestion, VerificationView
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
    branch (front/src/contract/rules.ts). ``None`` = not an overlay.

    ``trim()`` is JavaScript's set (``JS_TRIM_CHARS``), not ``str.strip()``.
    The authoritative cross-door check is contract/fixtures/proposal_parity.json
    (tests/test_proposal_parity.py), which drives the real parsers."""
    trimmed = stored.strip(JS_TRIM_CHARS)
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
def test_an_unusable_stored_overlay_shows_the_recipe_but_hands_over_nothing(stored):
    """Whatever the console cannot render as an overlay is not authoritative.

    The recipe stays visible as data, but a verification row sits beside it
    whose verdict never assessed those settings — so no diff and no PR body,
    the same pattern as a refusal."""
    suggestion = _suggest([_row(stored)])

    assert console_overlay(stored) in (None, {})
    assert suggestion.verification is not None
    assert suggestion.proposed_config == SKEW_RECIPE
    assert list(suggestion.proposed_config) == sorted(SKEW_RECIPE)
    assert suggestion.proposed_diff == ""
    assert suggestion.pr_body == ""
    assert suggestion.advisory_only is True
    assert suggestion.applied is False
    assert any("does not transfer to the recipe" in w for w in suggestion.warnings)
    assert not any("verify lane's stored overlay" in n for n in suggestion.notes)


# -- SRP-22 coordinator decisions: empty overlay, whitespace, key order -------
@pytest.mark.parametrize("stored", ["{}", "  {}  ", "\ufeff{ }\u00a0"])
def test_an_empty_overlay_proposes_nothing_and_gets_no_diff(stored):
    suggestion = _suggest([_row(stored)])

    assert suggestion.proposed_diff == ""
    assert suggestion.pr_body == ""
    assert suggestion.advisory_only is True
    assert suggestion.gated is False
    assert suggestion.applied is False
    # the recipe stays visible as data, in code-point order
    assert suggestion.proposed_config == SKEW_RECIPE
    assert list(suggestion.proposed_config) == sorted(SKEW_RECIPE)
    assert suggestion.verification is not None
    assert suggestion.verification.proposed_config == {}
    empty = [w for w in suggestion.warnings if "empty overlay" in w]
    assert len(empty) == 1
    assert "proposed nothing" in empty[0]
    assert "No diff or PR body is offered" in empty[0]
    assert "does not transfer to the recipe" in empty[0]
    assert not any("no readable overlay" in w for w in suggestion.warnings)


def test_an_ungated_empty_overlay_says_the_recipe_is_data_only():
    suggestion = _suggest([_row("{}")])
    empty = [w for w in suggestion.warnings if "empty overlay" in w]
    assert "in proposed_config as data only" in empty[0]


@pytest.mark.parametrize(
    ("stored", "needle"),
    [("{}", "empty overlay"), ("{not json", "no readable overlay")],
)
def test_a_gated_empty_or_unreadable_overlay_claims_nothing_is_in_proposed_config(
    stored, needle
):
    """On the confidence-gated path proposed_config is {}, so no warning may
    say the settings are in it."""
    suggestion = _suggest(
        [_row(stored)],
        findings=[finding_row(finding_id="finding-1", confidence_score=0.40)],
    )

    assert suggestion.gated is True
    assert suggestion.advisory_only is True
    assert suggestion.proposed_config == {}
    assert suggestion.proposed_diff == ""
    assert suggestion.pr_body == ""
    assert suggestion.applied is False
    hits = [w for w in suggestion.warnings if needle in w]
    assert len(hits) == 1
    assert "does not transfer to the recipe" in hits[0]
    assert not any("proposed_config as data" in w for w in suggestion.warnings)


def test_a_gated_unrenderable_overlay_claims_nothing_is_in_proposed_config():
    suggestion = _suggest(
        [_row(json.dumps({"spark a": "1"}))],
        findings=[finding_row(finding_id="finding-1", confidence_score=0.40)],
    )

    assert suggestion.gated is True
    assert suggestion.proposed_config == {}
    assert any("single conf line" in w for w in suggestion.warnings)
    assert not any("proposed_config as data" in w for w in suggestion.warnings)


def test_an_unparseable_overlay_is_named_differently_from_an_empty_one():
    suggestion = _suggest([_row("{not json")])

    assert any("no readable overlay" in w for w in suggestion.warnings)
    assert not any("empty overlay" in w for w in suggestion.warnings)
    assert suggestion.proposed_diff == ""


def test_no_verification_row_still_hands_over_the_recipe_diff():
    suggestion = _suggest([])

    assert suggestion.advisory_only is False
    assert _diff_pairs(suggestion.proposed_diff) == sorted(SKEW_RECIPE.items())
    assert suggestion.pr_body != ""


# Keys whose code-point order differs from JS insertion order (integer-like
# keys first) and from UTF-16 code-unit order (astral before U+FFFF).
CODE_POINT_KEYS = {
    "spark.z": "1",
    "10": "a",
    "9": "b",
    "2": "c",
    "Spark.B": "d",
    "spark.b": "e",
    "\uff21": "bmp",  # FULLWIDTH A: printable, above every surrogate unit
    "\U0001F600": "astral",
}


def _pr_bullets(body: str) -> list[tuple[str, str]]:
    import re

    return re.findall(r"^- `([^`]*)` = `([^`]*)`$", body, re.M)


def test_a_multi_key_overlay_renders_in_code_point_order_everywhere():
    stored = json.dumps(
        dict(reversed(list(CODE_POINT_KEYS.items()))), ensure_ascii=False
    )
    suggestion = _suggest([_row(stored)])

    expected = sorted(CODE_POINT_KEYS.items())  # Python: code-point order
    assert [k for k, _ in expected] == [
        "10", "2", "9", "Spark.B", "spark.b", "spark.z", "\uff21", "\U0001F600",
    ]
    assert list(suggestion.proposed_config.items()) == expected
    assert _diff_pairs(suggestion.proposed_diff) == expected
    assert _pr_bullets(suggestion.pr_body) == expected
    assert suggestion.advisory_only is False


@pytest.mark.parametrize("wrap", ["\u00a0", "\ufeff", "\u3000", "\u2028"])
def test_a_js_trim_wrapped_overlay_is_the_stored_overlay_not_the_recipe(wrap):
    stored = f"{wrap}{STORED}{wrap}"
    suggestion = _suggest([_row(stored)])

    assert suggestion.proposed_config == console_overlay(STORED)
    assert suggestion.proposed_config != SKEW_RECIPE
    assert _diff_pairs(suggestion.proposed_diff) == sorted(console_overlay(STORED).items())
    assert "overlay the verify lane evaluated" in suggestion.pr_body
    assert suggestion.advisory_only is False


@pytest.mark.parametrize("wrap", ["\u0085", "\u180e", "\u200b", "\u001c"])
def test_a_non_trim_wrapped_overlay_is_unreadable_on_both_doors(wrap):
    stored = f"{wrap}{STORED}"
    suggestion = _suggest([_row(stored)])

    assert console_overlay(stored) is None
    assert suggestion.verification.proposed_config == {}
    assert suggestion.proposed_diff == ""
    assert any("no readable overlay" in w for w in suggestion.warnings)


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
        (float(2**53 - 1), "9007199254740991"),  # node: String(MAX_SAFE_INTEGER)
        (-float(2**53 - 1), "-9007199254740991"),
        (5.0, "5"),
        (0.5, "0.5"),
        (1e-7, "1e-7"),  # node: String(1e-7)
    ],
)
def test_safe_floats_render_like_javascript(value, expected):
    view = VerificationView.model_validate(_row(json.dumps({"spark.a": value})))
    assert view.proposed_config == {"spark.a": expected}


# Each of these is a number the console's parseProposal rejects as
# invalid-overlay (front/src/contract/rules.test.ts mirrors this list): either
# non-finite after parsing, or beyond Number.MAX_SAFE_INTEGER, where JSON.parse
# would silently round the stored value. Both doors must reject, not render.
UNFAITHFUL_NUMBERS = [
    '{"spark.a": 1e400}',
    '{"spark.a": -1e400}',
    '{"spark.a": 9007199254740993}',  # JSON.parse -> 9007199254740992
    '{"spark.a": 9007199254740992}',  # 2**53: first unsafe integer
    '{"spark.a": -9007199254740992}',
    '{"spark.a": 1e20}',
    '{"spark.a": 1.5e300}',
    '{"spark.a": "1", "spark.b": 18446744073709551616}',
]


@pytest.mark.parametrize("stored", UNFAITHFUL_NUMBERS)
def test_an_unfaithful_number_is_rejected_like_the_console(stored):
    view = VerificationView.model_validate(_row(stored))
    assert view.proposed_config == {}

    suggestion = _suggest([_row(stored)])
    assert suggestion.proposed_config == SKEW_RECIPE
    assert any("no readable overlay" in w for w in suggestion.warnings)
    assert "verify lane evaluated" not in suggestion.pr_body


@pytest.mark.parametrize(
    ("stored", "expected"),
    [
        ('{"spark.a": 9007199254740991}', "9007199254740991"),
        ('{"spark.a": -9007199254740991}', "-9007199254740991"),
        ('{"spark.a": 800}', "800"),
    ],
)
def test_a_safe_integer_literal_is_kept_exactly(stored, expected):
    view = VerificationView.model_validate(_row(stored))
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


# -- review follow-up b: the chosen finding's row, not a capped job-wide list --
def test_a_lookup_fetches_the_chosen_findings_row_by_its_id():
    asked: list[str] = []

    def lookup(finding_id: str) -> list[dict]:
        asked.append(finding_id)
        return [_row()]

    # verification_rows is a job-wide list that no longer holds finding-1
    suggestion = diagnose.suggest_fix(
        "job-1",
        None,
        0.75,
        [FINDING],
        [stage_row(2, p50_ms=20, p99_ms=460)],
        [],
        [_row(finding_id="finding-other")] * 3,
        verification_lookup=lookup,
    )

    assert asked == ["finding-1"]
    assert suggestion.proposed_config == console_overlay(STORED)
    assert suggestion.verification is not None
    assert suggestion.verification.verification_id == "v-1"


def test_no_finding_no_lookup():
    """The heuristic path has no finding, so it must not query verifications."""
    def lookup(finding_id: str) -> list[dict]:  # pragma: no cover - must not run
        raise AssertionError("looked up a verification without a finding")

    suggestion = diagnose.suggest_fix(
        "job-1", None, 0.75, [], [stage_row(2, p50_ms=20, p99_ms=460)], [],
        verification_lookup=lookup,
    )
    assert suggestion.source == "spark_events_heuristic"
    assert suggestion.verification is None


class _ManyVerificationsClient:
    """fix_verifications honouring the finding filter and the LIMIT, the way
    ClickHouse does: 60 newer rows for another finding bury finding-1's row
    beyond the store's default 50-row job-wide cap."""

    def __init__(self) -> None:
        from tests.conftest import FakeClient

        self._base = FakeClient(
            stages={"job-1": [stage_row(2, p50_ms=20, p99_ms=460)]},
            findings={"job-1": [FINDING]},
        )
        other = [
            _row(
                json.dumps({"spark.other": str(i)}),
                verification_id=f"v-other-{i:03d}",
                finding_id="finding-other",
                verified_at=f"2026-08-21T10:00:{i:02d}.000",
            )
            for i in range(60)
        ]
        self.rows = other + [_row()]  # newest first; finding-1's row is last

    def query(self, query: str, parameters: dict | None = None):
        from tests.conftest import FakeResult, reads

        parameters = parameters or {}
        if reads(query, "fix_verifications") and "system.columns" not in query:
            fid = parameters.get("finding_id", "")
            rows = [r for r in self.rows if not fid or r["finding_id"] == fid]
            return FakeResult(rows[: int(parameters.get("limit", 50))])
        return self._base.query(query, parameters)


def test_the_server_finds_the_chosen_findings_row_beyond_the_job_wide_cap():
    import asyncio

    from apex_mcp.ch import ReadStore
    from apex_mcp.server import create_server

    server = create_server(ReadStore(_ManyVerificationsClient()))
    result = asyncio.run(server.call_tool("suggest_fix", {"job_id": "job-1"}))
    payload = result[1] if isinstance(result, tuple) else result

    assert payload["verification"]["finding_id"] == "finding-1"
    assert payload["proposed_config"] == console_overlay(STORED)
    assert payload["verification"]["verification_id"] == "v-1"
    assert payload["applied"] is False


# -- review follow-up c: both doors break verified_at ties the same way ---------
def _order_by(sql: str) -> str:
    import re

    match = re.search(r"ORDER BY\s+(.+?)\s*\n\s*LIMIT", sql, re.S)
    assert match, "no ORDER BY ... LIMIT in statement"
    # the console projection aliases the table as v.; compare column order
    return " ".join(match.group(1).replace("v.", "").split())


def test_every_door_breaks_verified_at_ties_on_verification_id():
    import pathlib
    import re

    from apex_mcp import ch

    queries_ts = (
        pathlib.Path(__file__).resolve().parents[2] / "front" / "src" / "data" / "queries.ts"
    ).read_text()
    match = re.search(r"export const FIX_VERIFICATIONS = `(.*?)`;", queries_ts, re.S)
    assert match, "front/src/data/queries.ts no longer exports FIX_VERIFICATIONS"

    expected = "verified_at DESC, verification_id ASC"
    assert _order_by(ch.VERIFICATIONS_SQL) == expected  # MCP suggest_fix source
    assert _order_by(ch.FIX_VERIFICATION_SQL) == expected  # console API door
    assert _order_by(match.group(1)) == expected  # console browser door


def test_a_same_millisecond_tie_picks_the_row_the_console_picks():
    """Rows come back ordered (verified_at DESC, verification_id ASC); the
    first row for the finding is the one both doors show."""
    tied = [
        _row(json.dumps({"spark.a": "1"}), verification_id="v-a"),
        _row(json.dumps({"spark.a": "2"}), verification_id="v-b"),
    ]
    suggestion = _suggest(tied)
    assert suggestion.verification is not None
    assert suggestion.verification.verification_id == "v-a"
    assert suggestion.proposed_config == {"spark.a": "1"}


# -- QA follow-up: a deeply nested overlay must degrade, not raise -------------
@pytest.mark.parametrize(
    "stored",
    [
        '{"a":' + "[" * 5000 + "]" * 5000 + "}",
        '{"a":' + '{"b":' * 5000 + "1" + "}" * 5000 + "}",
        "[" * 5000 + "]" * 5000,
    ],
    ids=["nested-arrays", "nested-objects", "top-level-arrays"],
)
def test_a_deeply_nested_overlay_degrades_to_the_recipe_without_raising(stored):
    view = VerificationView.model_validate(_row(stored))
    assert view.proposed_config == {}

    suggestion = _suggest([_row(stored)])
    assert suggestion.proposed_config == SKEW_RECIPE
    assert any("no readable overlay" in w for w in suggestion.warnings)
    assert suggestion.applied is False
