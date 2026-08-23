# Issue #90 — retry-safe `skew_ratio`

Status: candidate; owner decision required before publication.

## Problem

The shipped skew watcher computes p99/p50 from all task attempts. Retries and
speculative attempts can therefore create a false positive or hide a real tail,
even though the retry-safe successful-task duration population is available.

## Behavioral contract

- When `successful_task_sample_count > 0`, `skew_ratio`, tail-bound evaluation,
  evidence, and historical noise measurements use the successful-task p50/p99.
- Historical rows without a successful sample retain the legacy all-attempt
  fallback.
- `legacy_skew_ratio` remains available in finding details for explanation.
- Historical observations from different duration populations are never pooled
  into one known noise floor.
- Existing task-count, volume, tail-bound, headroom, and severity thresholds do
  not change.

## Scope

Engine models, ClickHouse read projections, skew evaluation, offline tests, and
this public contract note only. There is no schema, DDL, JAR, Collector,
Serve/MCP, Memory, or Verify change.

## Discriminating proof

The offline suite covers raw-high/successful-low, raw-low/successful-high,
historical fallback, mixed history populations, SQL/model compatibility, and
the behavior already present on PR #89.

## Compatibility and rollback

Rows with no successful-task sample keep their previous result. Rollback is a
code-only revert; no data or schema migration is involved.

## Evidence boundary

These tests prove deterministic Engine behavior only. They do not execute Spark
retry/speculation, ClickHouse, Collector, or any other runtime integration.
