"""Encoder invariants. Pure functions — no ClickHouse."""

from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

from apex_memory.encoder import (
    VECTOR_DIM,
    cosine_similarity,
    encode,
    parent_child_edges,
    parse_plan,
)

# A real redacted tree-string from apex.spark_events, verbatim.
REAL_PLAN = """'Aggregate [count(null) AS #0L]
+- 'Aggregate [none#0]
   +- 'Project [none#2]
      +- 'Join Inner, (none#1L = cast(none#0 as bigint))
         :- Project [none#1]
         :  +- Filter isnotnull(none#1)
         :     +- Relation [none#0L,none#1,none#2] parquet
         +- Filter isnotnull(none#0L)
            +- Relation [none#0L,none#1] parquet
"""


def test_vector_is_unit_length_and_correct_dim():
    feats = encode(REAL_PLAN)
    assert len(feats.vector) == VECTOR_DIM
    assert math.isclose(sum(v * v for v in feats.vector) ** 0.5, 1.0, rel_tol=1e-9)


def test_parses_real_catalyst_tree_shape():
    feats = encode(REAL_PLAN)
    assert feats.node_count == 9
    assert feats.max_depth == 6
    assert feats.join_count == 1
    assert feats.agg_count == 2
    assert feats.join_counts == {"Inner": 1}
    assert feats.op_counts["Relation"] == 2


def test_empty_plan_is_not_encodable():
    """A zero vector must never reach the index: cosineDistance against it is
    0/0, and the resulting NaN sorts unpredictably inside ORDER BY."""
    feats = encode("")
    assert feats.encodable is False
    assert feats.vector == []


def test_unresolved_and_invalid_markers_are_stripped():
    # `'` marks unresolved, `!` marks invalid. Both are Catalyst annotations,
    # not part of the operator name.
    assert parse_plan("'Project [x]")[0].operator == "Project"
    assert parse_plan("!Aggregate [x]")[0].operator == "Aggregate"


def test_continuation_lines_are_not_counted_as_nodes():
    # A wrapped expression list belongs to the node above it.
    plan = "Project [none#0,\n  none#1,\n  none#2]\n+- Relation [none#0] parquet"
    assert encode(plan).node_count == 2


def test_edges_distinguish_topology_from_operator_bag():
    """Same operators, same functions, different tree. A bag-of-operators
    encoder scores these 1.0; that is the blind spot edges exist to close."""
    a = "Filter isnotnull(x)\n+- Join Inner, (a = b)\n   :- Relation [x] parquet\n   +- Relation [y] parquet"
    b = "Join Inner, (a = b)\n:- Filter isnotnull(x)\n:  +- Relation [x] parquet\n+- Relation [y] parquet"
    fa, fb = encode(a), encode(b)
    assert fa.op_counts == fb.op_counts, "precondition: operator bags must match"
    similarity = cosine_similarity(fa.vector, fb.vector)
    assert similarity < 0.98, f"topology not discriminated (sim={similarity})"


def test_parent_child_edges_reconstruct_the_tree():
    edges = parent_child_edges(parse_plan(REAL_PLAN))
    assert "Join>Project" in edges
    assert "Filter>Relation" in edges


def test_identical_input_gives_identical_vector():
    assert encode(REAL_PLAN).vector == encode(REAL_PLAN).vector


def test_encoding_is_stable_across_processes():
    """crc32, not builtin hash().

    Python randomises string hashing per process, so an index built before a
    restart would not match queries encoded after one. This test fails loudly
    if someone swaps the stable hash for `hash()`.
    """
    src = Path(__file__).resolve().parents[1] / "src"
    snippet = (
        "import sys; sys.path.insert(0, %r)\n"
        "from apex_memory.encoder import encode\n"
        "print(','.join('%%.9f' %% v for v in encode(%r).vector))\n" % (str(src), REAL_PLAN)
    )
    runs = {
        subprocess.run(
            [sys.executable, "-c", snippet], capture_output=True, text=True, check=True
        ).stdout.strip()
        for _ in range(2)
    }
    assert len(runs) == 1, "vector differs between processes — unstable hash"


def test_unrelated_plans_are_far_apart():
    scan = encode("GlobalLimit null\n+- LocalLimit null\n   +- Relation [none#0] parquet")
    assert cosine_similarity(encode(REAL_PLAN).vector, scan.vector) < 0.5
