# Issue #65 — combined AQE re-plan detection contract

Status: implementation candidate; owner decision required before publication.

Canonical decision proposal:
[ADR-003 — AQE re-plan detection](../architecture/ADR-003-AQE-REPLAN-DETECTION.md).
This document is the behavioral and verification contract for the PR #98
candidate, not a separate architecture decision.

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

The evidence retained from PR #93 reports 34/34 tests passing across four
Spark/Scala cells and 0.72 ms at 100 joins. The authorized consolidation
contract additionally records a synthetic result of 53 ms at 2000 joins. These
are attributed offline measurements, not runtime or production guarantees; a
future review must preserve the environment and raw-output provenance when
using either number as a merge gate.

## Scope and rollback

Only the JAR listener, tests, and public decision documentation change. Rollback
is code-only; no schema or data migration is involved.

## Evidence boundary

The automated matrix and benchmark are offline JVM evidence. No Spark submit,
Collector, ClickHouse, or production trace is executed by this candidate.

## Decision boundary

PR #93 supplied the design comparison and is superseded only as a competing
decision document. PR #98 supplies the combined candidate. Issue #65 remains
open at the product boundary until Luan explicitly accepts or rejects the
combined behavior recorded in ADR-003.
