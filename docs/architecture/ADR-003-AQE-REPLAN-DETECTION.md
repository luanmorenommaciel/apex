# ADR-003 — AQE re-plan detection

- Status: proposed; maintainer decision required
- Date: 2026-08-27
- Decision owner: Luan
- Origin: issue #65
- Lineage: PR #93 (design evidence) and PR #98 (combined candidate)

## Context

Issue #65 identified two defects that cannot be resolved by either existing
approach alone. Positional comparison of join sequences can turn one inserted
or removed join into a cascade of false `join_switch` transitions. The separate
edit-alignment approach corrects that structural comparison but, by itself,
does not retain the accumulator-based `numSkewedPartitions` precision already
used for `skew_split`.

PR #93 documented the alternatives, cross-test evidence, cost evidence, risks,
and rollback conditions without implementing a detector. PR #98 contains a
candidate that combines edit alignment with the existing skew-count flow. This
ADR consolidates those contributions into one canonical proposal. It does not
approve the product behavior, publish either PR, or change the tested JAR code.

## Proposed decision

Adopt the combined detector, subject to Luan's explicit approval:

1. align consecutive join sequences with a minimum edit alignment;
2. classify only strict substitutions as `join_switch`;
3. treat insertions and deletions as structural edits, not strategy switches;
4. preserve the accumulator IDs, pending transition queue, and execution-end
   fallback that produce the true `numSkewedPartitions` value; and
5. preserve the meanings and payload contracts of `join_switch`, `skew_split`,
   `coalesce`, and `local_read`.

The proposal changes detector internals only. It does not authorize schema,
DDL, event-payload, Collector, ClickHouse, engine, serve, or contract changes.

## Alternatives considered

### Keep positional comparison with skew-count

This preserves current skew-count precision and has the smallest implementation
change. It retains the known false cascade when a join is inserted or removed.
The PR #93 record reports that the variant without edit alignment failed 3 of 5
cross-accuracy tests.

### Use edit alignment without skew-count

This fixes insertion and removal alignment. It does not independently satisfy
the current precision contract for skewed partitions. The PR #93 record reports
that the variant without skew-count did not compile against that specification.

### Combine edit alignment and skew-count

This is the only option in the recorded comparison that preserves both
properties. It adds an O(n²) time-and-memory alignment in the number of joins,
so its cost and plan-size boundary must remain visible during review and any
future rollout.

## Evidence

### Directly inspectable in the local PR #98 candidate

- Focused tests cover insertion, removal, genuine substitution, identical and
  empty lists, repeated joins, accumulator IDs, alignment/skew integration,
  coalesce, and local-read behavior.
- The candidate preserves the existing accumulator-based skew flow while
  replacing positional join comparison with minimum edit alignment.
- Its benchmark is an offline, non-gating JVM test at 100 joins; it does not run
  Spark submit, Collector, ClickHouse, or a production trace.
- The recorded local four-cell run is classified `offline_green` and explicitly
  records `runtime_proof=false`.

### Reported evidence retained from PR #93 and issue #65

- The combined candidate passed 34/34 tests across the four recorded
  Spark/Scala build cells.
- The 100-join JVM measurement was 0.72 ms.
- No production trace with materially more than approximately 100 joins was
  available, so this measurement cannot establish production behavior at
  larger scales.

### Reported scale benchmark required by the consolidation contract

The authorized Task-Spec records **53 ms at 2000 joins**. This is synthetic,
offline benchmark evidence. The raw benchmark output and its complete machine,
JVM, warm-up, iteration, and aggregation metadata are not part of this
document-only consolidation, and the 2000-join case is not exercised by the
focused test command below. Therefore 53 ms must not be presented as production
latency, runtime coverage, an SLO, or a universal upper bound.

Together these results support the technical recommendation to combine the
detectors. They do not constitute owner approval or production validation.

## Consequences

### Positive

- Insertions and removals no longer create positional false-switch cascades.
- Genuine join-strategy substitutions remain visible with their existing high
  confidence.
- Skew partition counts retain their current accumulator-based precision and
  fallback behavior.
- No downstream schema or migration is required.

### Negative and risks

- Alignment cost grows quadratically with the number of joins.
- Repeated join names can admit multiple minimum alignments; deterministic
  tie-breaking and adversarial tests remain part of the correctness boundary.
- Offline synthetic results do not establish production plan-size distribution
  or latency.
- Maintaining both semantics increases implementation and review surface.

## Verification and rollout conditions

Before publication or merge, the candidate must:

1. keep focused insertion, removal, substitution, repeated-join, skew-count,
   coalesce, and local-read tests green;
2. pass the supported Spark/Scala matrix or its explicitly documented
   successor;
3. retain reproducible 100-join and larger synthetic benchmark evidence with
   raw output and environment metadata;
4. define a maintainer-approved regression threshold before treating benchmark
   results as a gate; and
5. avoid claiming runtime coverage until a separately authorized runtime test
   exercises the detector through the required infrastructure.

## Compatibility and rollback

The proposed detector keeps schemas, DDL, event payloads, and consumers
unchanged. If approved code regresses accuracy, compatibility, or the agreed
cost threshold, revert the detector change and its focused tests. No data or
schema migration is required. Reverting this documentation alone restores the
previous documentation state but does not make either competing record
canonical.

## Lineage and supersession

- Issue #65 remains the origin and decision tracker.
- PR #93 remains evidence for alternatives, cross-tests, benchmarks, risks, and
  rollback, but its decision document is superseded by this ADR.
- PR #98 remains the source of the combined implementation candidate and its
  focused tests; this ADR does not approve or publish it.
- `ISSUE-65-AQE-REPLAN-DETECTION-DECISION.md` is a stable index to this ADR.
- `docs/task-specs/ISSUE-65-AQE-REPLAN-DETECTION.md` remains the implementation
  behavior and verification contract, not a competing decision.

## Pending owner decision

Luan must explicitly accept or reject the combined detector as the product
direction for issue #65. Until that decision is recorded, this ADR remains
**proposed**, PR #98 remains an unpublished/unapproved candidate, and PR #93 is
superseded only as a competing decision document—not as evidence.
