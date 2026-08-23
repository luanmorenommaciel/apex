# Issue #65 — combined AQE re-plan detection

Status: candidate; owner decision required before publication.

## Problem

Positional comparison of join lists reports false `join_switch` transitions
after a join is inserted or removed. A separate edit-alignment implementation
fixes that defect but does not contain the current accumulator-based skewed
partition counting.

## Behavioral contract

- Align join lists structurally and emit `join_switch` only for a strict
  substitution in a minimum edit alignment.
- Preserve `skew_split`, `coalesce`, and `local_read` detection.
- Preserve the current accumulator-ID flow and true skewed-partition count,
  including the existing execution-end fallback when a metric never arrives.
- Do not expose raw plan text or change transition schemas.

## Proof

Tests cover insertion, removal, substitution, identical and empty lists,
repeated joins, skew accumulator IDs, alignment/skew integration, and retained
coalesce/local-read semantics. The existing four Spark/Scala build cells remain
the compatibility gate. A JVM benchmark measures edit alignment at 100 joins.

## Scope and rollback

Only the JAR listener, tests, and public decision documentation change. Rollback
is code-only; no schema or data migration is involved.

## Evidence boundary

The automated matrix and benchmark are offline JVM evidence. No Spark submit,
Collector, ClickHouse, or production trace is executed by this candidate.
