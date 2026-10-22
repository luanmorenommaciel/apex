"""SRP-22 / P7.10 — both doors read the SAME overlay out of the same stored text.

contract/fixtures/proposal_parity.json is shared with the console's vitest
suite (front/src/contract/proposalParity.test.ts), so the two parsers cannot
drift: each case's ``expected`` is asserted against the real
``VerificationView`` parser here and the real ``parseProposal`` +
``overlayEntries`` there.

The three rules the fixture pins:
  1. whitespace around the JSON — exactly JavaScript's ``trim`` set;
  2. ``{}`` proposes nothing (``empty-overlay``), on both doors;
  3. keys in Unicode code-point order.
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess

import pytest

from apex_mcp.models import JS_TRIM_CHARS, VerificationView, read_overlay

REPO = pathlib.Path(__file__).resolve().parents[2]
FIXTURE = REPO / "contract" / "fixtures" / "proposal_parity.json"
CASES = json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"]


def _view(proposed_config: object) -> VerificationView:
    return VerificationView.model_validate(
        {
            "verification_id": "v-1",
            "finding_id": "finding-1",
            "job_id": "job-1",
            "proposed_config": proposed_config,
        }
    )


def _kind(overlay: dict[str, str] | None) -> str:
    if overlay is None:
        return "none"
    return "overlay" if overlay else "empty-overlay"


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_mcp_reads_every_shared_case_as_expected(case):
    expected = case["expected"]
    overlay = read_overlay(case["input"])

    assert _kind(overlay) == expected["kind"]
    entries = [list(pair) for pair in (overlay or {}).items()]
    assert entries == expected["entries"]

    # The model field the wire carries: {} whenever nothing usable is stored,
    # keys in the same (dict) order.
    view = _view(case["input"])
    assert [list(p) for p in view.proposed_config.items()] == expected["entries"]


def test_the_fixture_covers_the_three_rules():
    names = " | ".join(c["name"] for c in CASES)
    for needle in ("js-trim", "non-trim", "empty object", "integer-like", "astral"):
        assert needle in names
    kinds = {c["expected"]["kind"] for c in CASES}
    assert kinds == {"overlay", "empty-overlay", "none"}


def test_the_trim_set_is_exactly_javascripts():
    expected = {
        0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x20, 0xA0, 0x1680,
        *range(0x2000, 0x200B), 0x2028, 0x2029, 0x202F, 0x205F, 0x3000, 0xFEFF,
    }
    assert {ord(c) for c in JS_TRIM_CHARS} == expected
    for not_trimmed in (0x85, 0x180E, 0x200B, 0x1C, 0x1D, 0x1E, 0x1F):
        assert chr(not_trimmed) not in JS_TRIM_CHARS


@pytest.mark.parametrize("depth", [1500])
def test_deep_nesting_is_unreadable_not_an_error(depth):
    nested = '{"spark.a":' + "[" * depth + "]" * depth + "}"
    assert read_overlay(nested) is None
    assert _view(nested).proposed_config == {}


# -- optional: the real console parser over the same fixture --------------------
_NODE_SCRIPT = r"""
import { readFileSync } from "node:fs";
const { parseProposal, overlayEntries } = await import(process.argv[3]);
const cases = JSON.parse(readFileSync(process.argv[2], "utf8")).cases;
const out = cases.map((c) => {
  const p = parseProposal(c.input);
  if (p.kind === "overlay") return { kind: "overlay", entries: overlayEntries(p.config) };
  if (p.kind === "empty-overlay") return { kind: "empty-overlay", entries: [] };
  return { kind: "none", entries: [] };
});
process.stdout.write(JSON.stringify(out));
"""


def test_zero_disagreement_with_the_console_parser(tmp_path):
    """Runs the console's real parseProposal under node (type stripping, Node
    >= 22.6) when available. Skipped when node is absent or cannot load it."""
    front = REPO / "front"
    node = shutil.which("node")
    if node is None:
        pytest.skip("node not available")
    script = tmp_path / "parity.mjs"
    script.write_text(_NODE_SCRIPT, encoding="utf-8")
    rules = (front / "src" / "contract" / "rules.ts").as_uri()
    proc = subprocess.run(
        [node, "--experimental-strip-types", "--no-warnings", str(script), str(FIXTURE), rules],
        capture_output=True, text=True, timeout=120, check=False,
    )
    if proc.returncode != 0:
        pytest.skip(f"console parser could not run: {proc.stderr[-400:]}")
    console = json.loads(proc.stdout)
    mcp = []
    for case in CASES:
        overlay = read_overlay(case["input"])
        mcp.append(
            {"kind": _kind(overlay), "entries": [list(p) for p in (overlay or {}).items()]}
        )
    disagreements = [
        (case["name"], c, m) for case, c, m in zip(CASES, console, mcp) if c != m
    ]
    assert disagreements == []
