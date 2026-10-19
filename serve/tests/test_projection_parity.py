"""fix_verifications is projected the documented way, in its one home.

``FIX_VERIFICATION_SQL`` turns a fix_verifications row into runtime_certified
and runtime_verdict (rule 2), flips the stored delta into a saving, reports
mechanism_confirmed as NULL because nothing stores it, and reads the newest
verification for a finding. ch.py is the only copy (D-api-only, 2026-10-19);
this pins the rule's boundaries so a reworded predicate fails here before a
screen shows a direction the floor cannot support.
"""

from __future__ import annotations

import re

from apex_mcp import ch


def bindings(sql: str) -> list[str]:
    return re.findall(r"\{[^{}]*\}", sql)


def normalise(sql: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"--[^\n]*", "", sql)).strip()


def test_binds_only_the_finding():
    assert bindings(ch.FIX_VERIFICATION_SQL) == ["{finding_id:String}"]


def test_rule_two_lives_in_the_projection():
    sql = normalise(ch.FIX_VERIFICATION_SQL)
    # A delta inside the floor is unresolvable, never a direction.
    assert "abs(v.measured_delta_pct) <= v.noise_floor_pct, 'unresolved'" in sql
    assert "abs(v.measured_delta_pct) > v.noise_floor_pct) AS runtime_certified" in sql
    assert "v.measured_delta_pct < 0, 'improved'" in sql
    assert "'regressed') AS runtime_verdict" in sql
    # A saving is positive when faster; the stored delta is signed the other way.
    assert "-v.predicted_delta_pct AS predicted_saving_pct" in sql
    # Nothing stores whether the fix fired: NULL, never derived from the safety verdict.
    assert "CAST(NULL AS Nullable(UInt8)) AS mechanism_confirmed" in sql
    # The newest verification for the finding, one row.
    assert sql.endswith("ORDER BY v.verified_at DESC LIMIT 1")
