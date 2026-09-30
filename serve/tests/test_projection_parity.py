"""The two projections of fix_verifications stay one statement.

``FIX_VERIFICATION_SQL`` (serve) and ``FIX_VERIFICATIONS`` (front) both turn a
fix_verifications row into runtime_certified / runtime_verdict, so the noise
floor boundary lives in two files. Any change to that rule has to land in both
at once; this pins that it did.

Static on purpose: the front's text is READ from ``front/src/data/queries.ts``
and compared verbatim with serve's, after renaming the one binding the two
sides spell differently. Nothing else is normalised, so a moved boundary
operator, a reordered column or a reworded predicate on either side fails
here. It proves the two projections agree, not that the rule they share is
the right one, and it does not execute either against ClickHouse.
"""

from __future__ import annotations

import pathlib
import re

from apex_mcp import ch

QUERIES_TS = (
    pathlib.Path(__file__).resolve().parents[2] / "front" / "src" / "data" / "queries.ts"
)

# The only difference the two sides are allowed: the name of the binding.
FRONT_BINDING = "{finding:String}"
SERVE_BINDING = "{finding_id:String}"


def front_fix_verifications() -> str:
    """The exact text of front's ``export const FIX_VERIFICATIONS = `...`;``."""
    matches = re.findall(
        r"export const FIX_VERIFICATIONS = `(.*?)`;",
        QUERIES_TS.read_text(),
        flags=re.DOTALL,
    )
    assert len(matches) == 1, "front/src/data/queries.ts must export FIX_VERIFICATIONS once"
    return matches[0]


def bindings(sql: str) -> list[str]:
    return re.findall(r"\{[^{}]*\}", sql)


def test_each_side_binds_only_the_finding():
    """The rename below is total: one binding per side, and nothing else to rename."""
    assert bindings(front_fix_verifications()) == [FRONT_BINDING]
    assert bindings(ch.FIX_VERIFICATION_SQL) == [SERVE_BINDING]


def test_serve_projection_is_the_fronts_verbatim():
    """Same text byte for byte once the binding carries serve's name."""
    theirs = front_fix_verifications().replace(FRONT_BINDING, SERVE_BINDING)
    assert ch.FIX_VERIFICATION_SQL == theirs
