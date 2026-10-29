"""Populated and empty stores answer differently for the SAME request.

The B-4 test in test_tool_transport_parity.py compares the populated payload
for job "j" with the empty payload for job "missing". In the six tools that
echo the job id, that echo alone makes the two differ, so the comparison would
still pass if the populated store answered with an absence. Here both calls get
the same arguments, the fields that echo them are asserted equal, and each side
must carry its own content: an answer over populated data, an absence over the
empty store.

suggest_fix has no absence status, so it gets its own predicate: over
populated data, a findings-backed, ungated proposal with a diff and the
verification disclosed; over the empty store, the no-telemetry refusal.
"""

from __future__ import annotations

from typing import Any

import pytest

from tests.test_tool_transport_parity import (
    TOOLS,
    _is_absence,
    _NoVerificationTable,
    _over_mcp,
    _populated,
    _vectors,
)
from tests.test_verify_fix import _row as verification_row


def _no_proposal(payload: dict[str, Any]) -> bool:
    """suggest_fix's absence: the no-telemetry branch, with nothing to apply."""
    return payload["source"] == "none" and payload["gated"] is True and payload["proposed_diff"] == ""


@pytest.mark.parametrize("tool", TOOLS)
def test_populated_and_empty_payloads_differ_for_the_same_arguments(tool):
    """B-4 — one set of arguments for both stores, so only the data can make
    the payloads differ, and the difference is an answer against an absence."""
    arguments, _, _ = _vectors("j")[tool]

    populated = _over_mcp(_populated(), tool, arguments)
    empty = _over_mcp(_NoVerificationTable(), tool, arguments)

    echoed = arguments.keys() & populated.keys()
    assert echoed, f"{tool} echoes none of its arguments"
    assert {key: populated[key] for key in echoed} == {key: empty[key] for key in echoed}
    assert populated != empty
    if tool == "suggest_fix":
        assert _no_proposal(empty)
        assert not _no_proposal(populated)
    else:
        assert _is_absence(tool, empty)
        assert not _is_absence(tool, populated), f"{tool} answered with an absence over populated data"


def test_suggest_fix_proposes_from_the_populated_rows():
    """B-4 — for suggest_fix, differing is not enough: over populated data the
    proposal comes from the findings row, is not gated, offers a diff, and
    discloses the verification the populated table serves."""
    arguments, _, _ = _vectors("j")["suggest_fix"]

    proposal = _over_mcp(_populated(), "suggest_fix", arguments)

    assert proposal["source"] == "findings_table"
    assert proposal["gated"] is False
    assert proposal["target_stage_id"] == 2
    assert proposal["proposed_diff"] and proposal["proposed_config"]
    assert proposal["verification"], "suggest_fix did not disclose the verification the populated table serves"
    assert proposal["verification"]["verification_id"] == verification_row()["verification_id"]
