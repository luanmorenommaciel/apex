"""Plan-shape evidence. What the stage's plan proves is physically in it.

This exists because engine labelled stage 4 of `app-20260724160310-0000`
`SKEW_ON_JOIN` when that stage's logical plan is a Delta-metadata
`!Aggregate [collect_set(...)]` with **no Join node at all** and
`shuffle_read_bytes = 0`. A join-skew tail appears on the shuffle READ side of a
join; a stage that reads no shuffle and contains no join cannot have one. The
finding was not a mis-scored heuristic, it was a fabricated *type*.

So a SKEW_ON_JOIN claim now requires two independent pieces of plan evidence:

  * a Join node in the plan, AND
  * `shuffle_read_bytes > 0` — the side a sort-merge/shuffled-hash join skew
    actually lands on.

SECURITY: `plan_json` is written by the OBSERVED Spark job, not by Apex — the
indirect-injection vector `serve/README.md` documents. It is treated here as
OPAQUE DATA exactly as `watchers/code.py` treats it: only fixed operator names
are searched for, no plan text is echoed into evidence, and nothing from it ever
reaches an LLM prompt through this module. A plan containing "ignore previous
instructions" is a string that matches no operator name.

The node list is kept in step with `verify/`'s `guardrails._JOIN_NODE`, which
gates the same claim from the other side.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .schema import StageAggregate

# Logical AND physical node names that mean "a join happens here". The contract
# ships the LOGICAL tree-string (`'Join Inner, (…)`), but dev's Python listener
# and future emitters may differ, so the physical spellings are included too.
JOIN_NODE = re.compile(
    r"\bJoin\b"
    r"|\bSortMergeJoin\b"
    r"|\bShuffledHashJoin\b"
    r"|\bBroadcastHashJoin\b"
    r"|\bBroadcastNestedLoopJoin\b"
    r"|\bCartesianProduct\b"
)


@dataclass(frozen=True)
class JoinEvidence:
    """Whether a join-skew claim is admissible for this stage, and why not."""

    has_join_node: bool
    reads_shuffle: bool
    plan_available: bool

    @property
    def supports_join_skew(self) -> bool:
        return self.plan_available and self.has_join_node and self.reads_shuffle

    def why_not(self) -> str:
        """The disqualifying fact, as a clause. Never quotes plan text."""
        if not self.plan_available:
            return "no plan text was captured for this stage, so no join can be evidenced"
        reasons = []
        if not self.has_join_node:
            reasons.append("its logical plan contains no Join node")
        if not self.reads_shuffle:
            reasons.append(
                "it reads 0 shuffle bytes, and join skew appears on the shuffle READ side"
            )
        return " and ".join(reasons)


def join_evidence(stage: StageAggregate) -> JoinEvidence:
    return JoinEvidence(
        has_join_node=bool(stage.plan_json) and bool(JOIN_NODE.search(stage.plan_json)),
        reads_shuffle=stage.shuffle_read_bytes > 0,
        plan_available=bool(stage.plan_json),
    )
