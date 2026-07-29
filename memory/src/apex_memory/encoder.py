"""Structural encoder for redacted Catalyst logical-plan tree-strings.

WHY THIS IS NOT A TEXT EMBEDDING
--------------------------------
ZEST (arXiv 2503.03826) embeds the logical plan as *text* with a general-purpose
sentence embedder (jina-embeddings-v3) and retrieves by cosine similarity. That
works because ZEST reads plans straight out of Spark, with column names, table
names and literals intact -- exactly the tokens a language model has learned to
find meaningful.

Apex's plans do not look like that. CONTRACT.md § Redaction requires the jar to
strip literals and identifiers in-JVM *before* egress, so what actually lands in
`apex.spark_events.plan_json` is (verified against the live store):

    'Aggregate [count(null) AS #0L]
    +- 'Aggregate [none#0]
       +- 'Project [none#2]
          +- 'Join Inner, (none#1L = cast(none#0 as bigint))
             :- Project [none#1]
             :  +- Filter isnotnull(none#1)
             :     +- Relation [none#0L,none#1,none#2] parquet

Every column is `none#N` and every literal is `null`. A text embedder pointed at
this would spend most of its capacity on placeholder tokens that are identical
across all plans -- high cosine similarity between unrelated queries, which is
worse than useless for retrieval.

What survives redaction is precisely the part that predicts performance:
operator names, operator multiplicity, join types, and tree shape. So we encode
those directly. The result is deterministic, costs nothing, needs no model
download and no network call, and -- unlike an opaque 1024-dim embedding -- every
dimension can be named when a human asks "why did these two plans match?".

ZEST's *architecture* is preserved exactly (embed plan -> cosine top-k -> pool
neighbour configs); only the encoder is swapped for one suited to our input.
`plan_memory.encoder_version` + `embedding_kind` exist so a text embedding can be
indexed alongside this one later and compared head-to-head.

VECTOR LAYOUT (encoder_version = "struct-v1")
---------------------------------------------
Four independently L2-normalised blocks, each scaled by a weight, concatenated,
then L2-normalised as a whole. Normalising per-block first is what stops a plan
with forty `Project` nodes from swamping the join-type and shape signal.

    [ operator hist | join-type hist | function hist | edge hist | shape scalars ]
      len(OP_VOCAB)+1  len(JOIN_VOCAB)+1 len(FUNC_VOCAB)+1 EDGE_DIM   len(SHAPE_FEATURES)

KNOWN LIMIT (measured, not theorised)
-------------------------------------
The histogram blocks are permutation-invariant. Six distinct fingerprints in the
live store encode to cosine exactly 1.0000: their redacted texts are genuinely
different (six different MD5s, all 1011 chars) but they share an operator tree,
a function multiset AND an edge set, differing only in how arguments are
arranged inside expressions. Redaction has erased everything that separated
them, so no encoder reading this column can tell them apart -- the information
is gone at the source, not lost here.

This is exactly why recall() is two-tiered. Exact `plan_fingerprint` equality
still separates all six perfectly and is always reported as the higher-confidence
tier; a fuzzy hit at similarity 1.0 means "structurally indistinguishable after
redaction", NOT "the same query", and recall() labels it that way and counts
distinct fingerprints so the difference stays visible in the evidence.

The function block was added after measuring the operator-only encoder against
the live store: six DISTINCT fingerprints scored cosine 1.0000 against each
other because they shared the tree `Project / Filter / LogicalRDD` and differed
only inside their expressions. Calling six different queries "identical" would
inflate the evidence count that confidence scoring is built on. Function names
are not redacted -- `collect_set`, `count`, `coalesce`, `UDF` all survive -- and
aggregate class is a first-order driver of memory and spill, so this block buys
discrimination and predictive signal at the same time.

All vectors are unit-length, so `cosineDistance` in ClickHouse is a true angular
distance and `similarity = 1 - cosineDistance` lands in [0, 1] for our
non-negative features.
"""

from __future__ import annotations

import math
import re
import zlib
from dataclasses import dataclass, field

from .config import EMBEDDING_KIND, ENCODER_VERSION

# ── Vocabulary (frozen for struct-v1) ────────────────────────────────────────
# Logical operators first, then the physical/AQE node types that legitimately
# appear in this column: engine's `code` watcher already greps plan text for
# CartesianProduct and BroadcastNestedLoopJoin, so they demonstrably show up.
# Anything unseen lands in the OTHER bucket AND is reported by
# `unknown_operators` so the vocabulary can be grown deliberately in struct-v2
# rather than silently drifting.
OP_VOCAB: tuple[str, ...] = (
    # relational core
    "Aggregate", "Project", "Filter", "Join", "Sort", "Window", "Union",
    "Distinct", "Deduplicate", "Expand", "Generate", "Sample", "Intersect",
    "Except", "Pivot", "Unpivot", "LateralJoin", "Offset", "Tail",
    # limits
    "GlobalLimit", "LocalLimit",
    # sources / sinks
    "Relation", "LogicalRDD", "Scan", "FileScan", "Range", "OneRowRelation",
    "SubqueryAlias", "View", "InsertIntoStatement",
    "InsertIntoHadoopFsRelationCommand", "CreateDataSourceTableAsSelectCommand",
    "AppendData", "OverwriteByExpression",
    # Spark 3.4+ splits the write into its own logical node; observed in the
    # live corpus, so it belongs in the vocabulary rather than the OTHER bucket.
    "WriteFiles",
    # partitioning
    "Repartition", "RepartitionByExpression", "Coalesce",
    # CTEs
    "WithCTE", "CTERelationDef", "CTERelationRef",
    # object / UDF plumbing
    "MapPartitions", "SerializeFromObject", "DeserializeToObject",
    "MapInPandas", "FlatMapGroupsInPandas", "CollectMetrics",
    # physical + AQE node types that reach this column
    "Exchange", "ShuffleExchange", "BroadcastExchange", "AQEShuffleRead",
    "BroadcastHashJoin", "SortMergeJoin", "ShuffledHashJoin",
    "CartesianProduct", "BroadcastNestedLoopJoin",
    "HashAggregate", "SortAggregate", "ObjectHashAggregate",
)
OP_INDEX = {name: i for i, name in enumerate(OP_VOCAB)}
OP_OTHER = len(OP_VOCAB)
OP_DIM = len(OP_VOCAB) + 1

JOIN_VOCAB: tuple[str, ...] = (
    "Inner", "LeftOuter", "RightOuter", "FullOuter",
    "LeftSemi", "LeftAnti", "Cross", "ExistenceJoin",
)
JOIN_INDEX = {name: i for i, name in enumerate(JOIN_VOCAB)}
JOIN_OTHER = len(JOIN_VOCAB)
JOIN_DIM = len(JOIN_VOCAB) + 1

# Expression functions that survive redaction. Grouped by what they cost, since
# that is why they are here: a plan doing `collect_set` has a completely
# different memory profile from one doing `count`, even with an identical
# operator tree. `multicommutativeop` is included because it appears verbatim in
# the live store's Delta-sourced plans.
FUNC_VOCAB: tuple[str, ...] = (
    # cheap reductions
    "count", "sum", "avg", "min", "max", "first", "last",
    # unbounded / memory-hungry accumulators
    "collect_set", "collect_list", "approx_count_distinct",
    "stddev", "variance", "percentile", "percentile_approx",
    # null / type plumbing
    "coalesce", "cast", "isnotnull", "isnull", "nullif", "nvl",
    # structural
    "struct", "array", "map", "explode", "size", "get_json_object",
    # windowing
    "row_number", "rank", "dense_rank", "lag", "lead", "ntile",
    # string / hashing
    "concat", "substring", "length", "upper", "lower", "trim", "split",
    "regexp_replace", "regexp_extract", "hash", "md5", "sha2",
    # temporal
    "to_date", "date_add", "datediff", "year", "month", "unix_timestamp",
    "from_unixtime",
    # conditionals + user code
    "if", "when", "case", "greatest", "least",
    "UDF", "multicommutativeop",
)
FUNC_INDEX = {name: i for i, name in enumerate(FUNC_VOCAB)}
FUNC_OTHER = len(FUNC_VOCAB)
FUNC_DIM = len(FUNC_VOCAB) + 1

# Parent->child operator edges, hashed into a fixed number of buckets.
#
# Without this block the encoder is a pure bag of operators, so `Filter(Join(a,b))`
# and `Join(Filter(a), b)` -- same operators, materially different plans with
# materially different shuffle behaviour -- score a perfect 1.0. Edges are the
# cheapest representation of topology that fixes that.
#
# Hashing rather than a (vocab x vocab) matrix keeps the block small: the full
# cross product would be ~3.5k mostly-empty dimensions. 64 buckets over an
# alphabet this size collides rarely, and a collision only ever makes two plans
# look slightly MORE similar -- it cannot invent a difference, which is the safe
# direction for a retrieval index that feeds a confidence score.
EDGE_DIM = 64

SHAPE_FEATURES: tuple[str, ...] = (
    "log_node_count", "log_max_depth", "branch_ratio", "leaf_ratio",
    "join_density", "agg_density", "has_udf", "log_plan_chars",
)
SHAPE_DIM = len(SHAPE_FEATURES)

VECTOR_DIM = OP_DIM + JOIN_DIM + FUNC_DIM + EDGE_DIM + SHAPE_DIM

# Block weights. The operator histogram carries the most signal, so it is the
# reference at 1.0. Join types matter disproportionately for Spark performance
# (join strategy drives shuffle) so they get half weight despite being a much
# smaller block. Functions get half weight too: they discriminate and they
# predict cost, but an operator tree mismatch is still the stronger evidence
# that two plans are unrelated. Shape is a modifier, not a discriminator -- two
# plans with identical operators but different depth are still close relatives.
W_OPS, W_JOIN, W_FUNC, W_EDGE, W_SHAPE = 1.0, 0.5, 0.5, 0.6, 0.35

# Aggregation functions that indicate a wide/heavy aggregate, used only for the
# `agg_density` shape scalar (the operator histogram already counts Aggregate).
_UDF_RE = re.compile(r"\b(?:Scala|Python|Java)?UDF\b")
_JOIN_TYPE_RE = re.compile(r"^Join\s+([A-Za-z_]+)")
# An expression function is an identifier immediately followed by `(`. Operator
# names never match: Catalyst separates them from their arguments with a space
# or a bracket (`Filter isnotnull(x)`, `Join Inner, (...)`), so only genuine
# call sites are captured.
_FUNC_CALL_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\(")
_OPERATOR_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
# Tree-drawing characters Catalyst uses for the prefix of a child line.
_PREFIX_CHARS = frozenset(" +-:|")
# Markers Catalyst prepends to an operator: `'` = unresolved, `!` = invalid.
_NODE_MARKERS = frozenset("'!")

# Catalyst indents exactly three characters per tree level ("+- ", ":- ",
# "   ", ":  "), verified against the tree-strings in the live store.
_INDENT_WIDTH = 3


@dataclass(frozen=True)
class PlanNode:
    operator: str
    depth: int
    join_type: str | None
    raw: str


@dataclass
class PlanFeatures:
    """Decoded, nameable features plus the unit vector derived from them."""

    encoder_version: str = ENCODER_VERSION
    embedding_kind: str = EMBEDDING_KIND
    vector: list[float] = field(default_factory=list)
    op_counts: dict[str, int] = field(default_factory=dict)
    join_counts: dict[str, int] = field(default_factory=dict)
    func_counts: dict[str, int] = field(default_factory=dict)
    edge_counts: dict[str, int] = field(default_factory=dict)
    unknown_operators: list[str] = field(default_factory=list)
    node_count: int = 0
    max_depth: int = 0
    join_count: int = 0
    agg_count: int = 0
    exchange_count: int = 0
    scan_count: int = 0
    leaf_count: int = 0
    branch_count: int = 0
    has_udf: bool = False
    plan_chars: int = 0

    @property
    def encodable(self) -> bool:
        """False when the plan yielded no operators at all.

        This is a real state, not a defensive nicety: two stages per job in the
        live store carry `plan_json = ''` (Spark had no plan for them). A
        zero vector must never be indexed -- `cosineDistance` against it is
        undefined (0/0), and ClickHouse would return NaN, which sorts
        unpredictably and would quietly poison the top-k.
        """
        return self.node_count > 0 and any(self.vector)


def parse_plan(plan_text: str) -> list[PlanNode]:
    """Parse a Catalyst tree-string into a pre-order list of nodes.

    Catalyst prints a depth-first pre-order traversal, one node per line, with
    the nesting encoded purely in a fixed-width character prefix. That means the
    tree can be reconstructed from indentation alone -- no bracket matching, no
    recursion, and no assumptions about which operators are binary.
    """
    nodes: list[PlanNode] = []
    seen_root = False
    for raw_line in plan_text.splitlines():
        if not raw_line.strip():
            continue

        # Walk past the tree-drawing prefix to the first content character.
        i = 0
        while i < len(raw_line) and raw_line[i] in _PREFIX_CHARS:
            i += 1
        prefix_len = i

        # Catalyst marks every child node with `+-` or `:-`; only the root has
        # no marker. A line with neither is a CONTINUATION -- the wrapped tail
        # of the previous node's expression list -- and must not become a node.
        # Without this check `Project [none#0,\n  none#1]` parses as two nodes,
        # the second named "none", which both inflates node_count and dumps a
        # junk token into the OTHER bucket of the operator histogram.
        prefix = raw_line[:prefix_len]
        is_child = "+-" in prefix or ":-" in prefix
        if not is_child:
            if seen_root:
                continue
            seen_root = True

        # Skip the unresolved/invalid markers Catalyst prepends.
        while i < len(raw_line) and raw_line[i] in _NODE_MARKERS:
            i += 1

        body = raw_line[i:]
        match = _OPERATOR_RE.match(body)
        if not match:
            # A continuation line (a wrapped expression list, say). It belongs
            # to the previous node and is not a node of its own.
            continue
        operator = match.group(0)

        join_type = None
        if operator == "Join":
            jt = _JOIN_TYPE_RE.match(body)
            if jt:
                join_type = jt.group(1)

        nodes.append(
            PlanNode(
                operator=operator,
                depth=prefix_len // _INDENT_WIDTH,
                join_type=join_type,
                raw=body,
            )
        )
    return nodes


def parent_child_edges(nodes: list[PlanNode]) -> list[str]:
    """Derive `parent>child` operator edges from the pre-order + depth listing.

    A stack keyed on depth reconstructs parentage in one pass: pop until the top
    is shallower than the current node, and whatever remains on top is its
    parent.
    """
    edges: list[str] = []
    stack: list[PlanNode] = []
    for node in nodes:
        while stack and stack[-1].depth >= node.depth:
            stack.pop()
        if stack:
            edges.append(f"{stack[-1].operator}>{node.operator}")
        stack.append(node)
    return edges


def _edge_bucket(edge: str) -> int:
    """Stable hash bucket for an edge.

    `zlib.crc32`, not the builtin `hash()`: Python randomises string hashing per
    process, which would make the same plan encode to a different vector on
    every run and silently corrupt an index built across restarts.
    """
    return zlib.crc32(edge.encode("utf-8")) % EDGE_DIM


def _l2_normalise(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0.0:
        return vec
    return [v / norm for v in vec]


def encode(plan_text: str) -> PlanFeatures:
    """Encode a redacted Catalyst tree-string into a unit feature vector."""
    feats = PlanFeatures(plan_chars=len(plan_text))
    nodes = parse_plan(plan_text)
    if not nodes:
        return feats

    op_hist = [0.0] * OP_DIM
    join_hist = [0.0] * JOIN_DIM
    func_hist = [0.0] * FUNC_DIM
    op_counts: dict[str, int] = {}
    join_counts: dict[str, int] = {}
    func_counts: dict[str, int] = {}
    unknown: set[str] = set()

    for node in nodes:
        op_counts[node.operator] = op_counts.get(node.operator, 0) + 1
        idx = OP_INDEX.get(node.operator)
        if idx is None:
            unknown.add(node.operator)
            op_hist[OP_OTHER] += 1.0
        else:
            op_hist[idx] += 1.0

        if node.join_type is not None:
            join_counts[node.join_type] = join_counts.get(node.join_type, 0) + 1
            jidx = JOIN_INDEX.get(node.join_type, JOIN_OTHER)
            join_hist[jidx] += 1.0

    for name in _FUNC_CALL_RE.findall(plan_text):
        func_counts[name] = func_counts.get(name, 0) + 1
        func_hist[FUNC_INDEX.get(name, FUNC_OTHER)] += 1.0

    edge_hist = [0.0] * EDGE_DIM
    edge_counts: dict[str, int] = {}
    for edge in parent_child_edges(nodes):
        edge_counts[edge] = edge_counts.get(edge, 0) + 1
        edge_hist[_edge_bucket(edge)] += 1.0

    # A node is a leaf iff the next line in the pre-order walk is not deeper.
    leaf_count = sum(
        1
        for i, node in enumerate(nodes)
        if i + 1 == len(nodes) or nodes[i + 1].depth <= node.depth
    )
    # `:-` marks the left child of a binary node, so counting those lines counts
    # the branch points without needing to know which operators are binary.
    branch_count = sum(1 for line in plan_text.splitlines() if ":-" in line)

    node_count = len(nodes)
    max_depth = max(n.depth for n in nodes)
    join_count = sum(1 for n in nodes if "Join" in n.operator)
    agg_count = sum(1 for n in nodes if "Aggregate" in n.operator)
    exchange_count = sum(1 for n in nodes if "Exchange" in n.operator)
    scan_count = sum(
        1 for n in nodes if n.operator in ("Relation", "Scan", "FileScan", "LogicalRDD")
    )
    has_udf = bool(_UDF_RE.search(plan_text))

    # log1p damps multiplicity: a plan with forty Projects is "more projecty"
    # than one with four, but not ten times more -- and raw counts would let a
    # single verbose operator dominate the cosine.
    op_hist = [math.log1p(v) for v in op_hist]
    join_hist = [math.log1p(v) for v in join_hist]
    func_hist = [math.log1p(v) for v in func_hist]
    edge_hist = [math.log1p(v) for v in edge_hist]

    # Shape scalars, each squashed into roughly [0,1] against a plausible
    # ceiling so no single scalar dominates the block.
    shape = [
        min(math.log1p(node_count) / math.log1p(100.0), 1.0),
        min(math.log1p(max_depth) / math.log1p(30.0), 1.0),
        branch_count / node_count,
        leaf_count / node_count,
        join_count / node_count,
        agg_count / node_count,
        1.0 if has_udf else 0.0,
        min(math.log1p(len(plan_text)) / math.log1p(20000.0), 1.0),
    ]

    vector = (
        [W_OPS * v for v in _l2_normalise(op_hist)]
        + [W_JOIN * v for v in _l2_normalise(join_hist)]
        + [W_FUNC * v for v in _l2_normalise(func_hist)]
        + [W_EDGE * v for v in _l2_normalise(edge_hist)]
        + [W_SHAPE * v for v in _l2_normalise(shape)]
    )

    feats.vector = _l2_normalise(vector)
    feats.op_counts = op_counts
    feats.join_counts = join_counts
    feats.func_counts = func_counts
    feats.edge_counts = edge_counts
    feats.unknown_operators = sorted(unknown)
    feats.node_count = node_count
    feats.max_depth = max_depth
    feats.join_count = join_count
    feats.agg_count = agg_count
    feats.exchange_count = exchange_count
    feats.scan_count = scan_count
    feats.leaf_count = leaf_count
    feats.branch_count = branch_count
    feats.has_udf = has_udf
    return feats


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity for two already-unit vectors, clamped to [-1, 1].

    Used by the pure-Python path (tests, and the fallback when the caller wants
    ranking without a round trip). ClickHouse computes the same quantity as
    `1 - cosineDistance(...)` on the server for the indexed path.
    """
    if len(a) != len(b) or not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    return max(-1.0, min(1.0, dot))
