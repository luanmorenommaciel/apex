# Issue #65 — AQE re-plan detection decision

Status: owner decision; candidate not published.

## Options

1. Keep positional join comparison and accumulator-based skew counts.
2. Use edit alignment without accumulator-based skew counts.
3. Combine edit alignment with the current accumulator-based skew counts.

## Candidate evaluated here

Option 3. It fixes false join-switch cascades caused by insertion/removal while
retaining the current `numSkewedPartitions` accumulator IDs, pending transition
queue, and execution-end fallback. The four transition categories keep their
current meanings: `join_switch`, `skew_split`, `coalesce`, and `local_read`.

## Trade-off

Edit alignment uses O(n²) time and memory in the number of joins. A reproducible
JVM benchmark at 100 joins is included. That synthetic result is evidence about
the algorithm on the test JVM, not a claim about production latency or plan-size
distribution.

## Compatibility and rollback

The candidate is exercised across all supported Spark/Scala build cells. It
does not change schema, DDL, event payloads, or consumers, so rollback is a
code-only revert.

## Decision required

The owner must explicitly choose the combined behavior before publication.
Offline correctness and cost evidence do not constitute product acceptance.
