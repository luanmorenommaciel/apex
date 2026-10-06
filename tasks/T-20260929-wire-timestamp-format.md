---
id: T-20260929-wire-timestamp-format
title: "Return timestamps in one format, the API's, from every data source"
status: in-progress
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [serve/src/apex_api/routes/resources.py, serve/src/apex_api/app.py, serve/tests/test_api_resources.py, front/src/data/repository.ts, front/src/data/httpRepository.test.ts, front/src/contract/types.ts]
creates_paths: [serve/src/apex_api/wire.py, serve/tests/test_api_wire.py, front/src/data/timestamp.ts, front/src/data/timestamp.test.ts]
source_note: "front/src/data/repository.ts"
created: "2026-09-29T00:00:00Z"
tags: []
owner: (none)
priority: P2
severity: feature
due_date: (none)
precondition: (none)
blocked_reason: (none)
security_class: (none)
source_action_item: (none)
tracker_ref: (none)
execution_backend: any
signed_off: false
signed_off_by: (none)
signed_off_at: (none)
accepted: false
accepted_by: (none)
accepted_at: (none)
---

# Return timestamps in one format, the API's, from every data source

> **Why:** The same row carries a different timestamp depending on which door it came through. Every time column in the contract is DateTime64(3). The browser path reads ClickHouse's JSON and gets `2026-09-20 10:00:00.123`; the API hands FastAPI a Python datetime and gets whatever isoformat() makes of it - `2026-09-20T10:00:00.123000`, or `2026-09-20T10:00:00` with no fraction at all when the milliseconds are zero, or a `+00:00` suffix if the driver ever returns an aware value, which relativeAge() then breaks by appending Z. Nothing on screen shows it today only because one consumer normalises (relativeAge) and the other slices ten characters (MemoryScreen). The sweep of PR 129 found it and nothing pinned it.

## Goal

One wire format, the API's - ISO 8601 with a T, UTC, millisecond precision, no offset, `2026-09-20T10:00:00.123` - emitted deliberately by the API rather than by an encoder's default, and returned by ClickHouseRepository, HttpRepository and FixtureRepository alike, so a screen cannot tell which source a timestamp came from.

## Context

The owner's decision, recorded 2026-09-29 - the format the API serves is the target, and the other paths move to it. The API's T form is kept; what changes on the API side is only that the precision stops depending on the value - milliseconds always, because the columns are DateTime64(3), so the format is fixed-width and sorts as text. That is a proposed refinement of "the API's format", open for review - the alternative is to reproduce isoformat()'s variable width on the console side, which would make the console emulate an accident. Two normalisers, one per host, and a test that ties them - the serve test reads WIRE_TIMESTAMP out of front/src/data/timestamp.ts and asserts every timestamp the resource routes emit matches it, the same way the projection parity test reads the row types. On the serve side the conversion lives at the HTTP boundary (apex_api/wire.py), NOT in ReadStore - the MCP tools read ReadStore's rows as datetimes and do arithmetic on them, so ch.py is do-not-touch. Datetime VALUES are converted wherever they appear in a resource payload; timestamp STRINGS are normalised only under the known timestamp keys, because evidence, detail and fix are untrusted text and must never be pattern-matched into something else. On the console side the conversion lives in the repository mappers, the one place all three sources pass through; fixtures.ts keeps its recorded literals and FixtureRepository normalises on the way out, so the recording stays a recording. A value the normaliser does not recognise is carried verbatim - never replaced with a guess. The diagnostics tier is out of scope - its payloads are the MCP tools' own models with their own timestamp fields, and server.py is do-not-touch. The SQL is deliberately NOT where this is fixed - formatDateTime() in both rollups would make the two hosts agree by construction, but it rewrites every projection in two files that a live store has not yet confirmed, and every alias it adds is a candidate for the ILLEGAL_AGGREGATION shadowing this codebase has already hit four times.

## Behavior

- **B-1** — GIVEN a resource route whose store returns a datetime - naive, aware in another zone, with or without milliseconds WHEN the route is called THEN the JSON carries `YYYY-MM-DDTHH:MM:SS.mmm` in UTC with no offset, the aware value converted rather than truncated
- **B-2** — GIVEN WIRE_TIMESTAMP as declared in front/src/data/timestamp.ts WHEN every timestamp field of every resource route is checked against it THEN all match, and the check fails when the API's precision or separator changes
- **B-3** — GIVEN a ClickHouse JSON timestamp `2026-09-20 10:00:00.123`, an isoformat one with six digits, one with no fraction, one with Z and one with a +02:00 offset WHEN toWireTimestamp is called THEN each returns the wire form of the SAME instant, and an already-wire value is returned unchanged
- **B-4** — GIVEN each of ClickHouseRepository, HttpRepository and FixtureRepository WHEN any method returning rows with a timestamp field is called THEN every such field matches WIRE_TIMESTAMP - started_at, ts, observed_at, first_run and last_run
- **B-5** — GIVEN a string the normaliser does not recognise, null, or an untrusted text field that happens to contain a date WHEN a row passes through either normaliser THEN the value is carried verbatim
- **B-6** — GIVEN the MCP tools and the diagnostics routes WHEN their tests run THEN they pass unchanged, and ch.py and server.py have no diff

## Success Criteria

```bash
# eval_1: the API emits the wire format whatever the driver hands it
eval_1() {
  ( cd serve && uv run --extra dev pytest tests/test_api_wire.py )
}

# eval_2: every route's timestamps match the pattern the console declares
eval_2() {
  ( cd serve && uv run --extra dev pytest "tests/test_api_resources.py::test_every_timestamp_leaves_in_the_wire_format" )
}

# eval_3: the console normaliser converts every input form to the same instant
eval_3() {
  ( cd front && npm run test -- --run src/data/timestamp.test.ts )
}

# eval_4: all three repositories return wire timestamps
eval_4() {
  ( cd front && npm run test -- --run src/data/httpRepository.test.ts -t "wire timestamp" && npm run typecheck && npm run lint )
}

# eval_5: the MCP side and ReadStore did not move
eval_5() {
  ( cd serve && uv run --extra dev pytest tests/test_server_tools.py tests/test_api_diagnostics.py tests/test_ch.py && git diff --exit-code --stat -- src/apex_mcp )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "the API emits the wire format whatever the driver hands it"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-5]
    terminal: true
    expected_duration_sec: 60
  - id: eval_2
    description: "every route's timestamps match the pattern the console declares"
    runnable: bash
    check_type: deterministic
    verifies: [B-2]
    terminal: true
    expected_duration_sec: 60
  - id: eval_3
    description: "the console normaliser converts every input form to the same instant"
    runnable: bash
    check_type: deterministic
    verifies: [B-3, B-5]
    terminal: true
    expected_duration_sec: 120
  - id: eval_4
    description: "all three repositories return wire timestamps"
    runnable: bash
    check_type: deterministic
    verifies: [B-4]
    terminal: true
    expected_duration_sec: 180
  - id: eval_5
    description: "the MCP side and ReadStore did not move"
    runnable: bash
    check_type: deterministic
    verifies: [B-6]
    terminal: true
    expected_duration_sec: 180
retry_policy:
  max_iterations: 15
  circuit_breaker_no_progress: 3
  on_terminal_failure: park_with_context
agent_contract:
  version: 2
  read: [intent, behavior, contract, guardrails]
  produce: [code, tests]
  required_tools: [git, bash]
  timeout_minutes: 30
  sandbox_type: host
  output_artifacts: []
  mcp_dependencies: []
  emit: [pass, fail, retry_with_reason, parked_with_context]
  backend_metadata: {}
```

## Exit Check

```bash
eval_1 && eval_2 && eval_3 && eval_4 && eval_5
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- Converting in ReadStore; the MCP tools do arithmetic on those datetimes and would receive strings.
- Regex-matching every string in a payload; evidence, detail and fix are untrusted text written by the observed job.
- Dropping an offset instead of converting it; a plus-two-hours value with its offset stripped is a timestamp two hours wrong that still looks valid.
- Rewriting the fixtures' literals; the recording is a recording, and the repository is where a source becomes a row.
- formatDateTime() in the SQL of both hosts before a live store has confirmed the statements that are already there.

## Do-Not-Touch

- `serve/src/apex_mcp/`
- `front/src/data/fixtures.ts`
- `front/src/screens/`

## Open Questions

(none — this task is fully specified)
