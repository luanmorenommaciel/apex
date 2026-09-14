# Task-Spec — Compare, Memory and Verify read-only surfaces

## Identity

- `task_spec_id`: `UI43-B-COMPARE-MEMORY-VERIFY-READ-ONLY`
- `issue`: `#43`
- `status`: `owner_decision`
- `base_commit`: `7c5460c87421d7f9493a664acb1cfbcc54259b51`
- `runtime_authorized`: `false`

## Goal

Define truthful, offline visual contracts for the future **Compare**, **Memory**
and **Verify** screens. This increment makes their states, data boundaries and
security rules reviewable; it does not choose a front-end stack or connect a
browser to Apex.

## Sources of authority

- [`../../serve/src/apex_mcp/models.py`](../../serve/src/apex_mcp/models.py) and
  [`../../serve/src/apex_mcp/diagnose.py`](../../serve/src/apex_mcp/diagnose.py)
  — `RunComparison` and `compare_runs`.
- [`../../memory/src/apex_memory/schema.py`](../../memory/src/apex_memory/schema.py)
  and [`../../memory/src/apex_memory/recall.py`](../../memory/src/apex_memory/recall.py)
  — `RecallResult` and `recall`.
- [`../../verify/src/apex_verify/models.py`](../../verify/src/apex_verify/models.py)
  — `Prediction`, `Guardrail` and `Measurement`.
- [`../../CONTRACT.md`](../../CONTRACT.md) — identities and measured-noise rule.
- [`../architecture/UI43-B-COMPARE-MEMORY-VERIFY-READ-ONLY.md`](../architecture/UI43-B-COMPARE-MEMORY-VERIFY-READ-ONLY.md)
  — screen contracts and visual wireflows.

## Current data and boundaries

| Area | Available now | Missing for a browser screen |
|---|---|---|
| Compare | Typed `RunComparison` from the read-only `compare_runs` MCP tool | A browser-safe, versioned transport and browser session model |
| Memory | Typed Python `recall(...) -> RecallResult` and a CLI | A versioned, browser-consumable `RecallResult` surface |
| Verify | In-process typed evidence models and synthetic-replay semantics | A versioned public result contract, exposure path and runtime-gated increment |

`apex-mcp` uses **stdio**. A browser is not a stdio client, and this Task-Spec
does not invent a browser-to-MCP bridge. HyperDX at localhost port 8090 is an
observability product, not the APEX front end or an APEX browser API.

## Required states

Every screen specifies these mutually distinguishable states: `loading`,
`empty`, `error`, `evidence_insufficient` and `result`. A refusal or missing
evidence is a valid result; it must not be converted into a diagnosis,
recommendation, runtime result or zero delta.

### Compare semantics

- `status=not_comparable` and missing telemetry are valid outcomes.
- A missing baseline must not select an arbitrary run or fabricate a regression.
- Metric deltas remain measurements unless a measured, applicable noise floor
  is supplied; a UI must not fabricate one.

### Memory semantics

- Insufficient history is an `evidence_insufficient` result, not a failure.
- `best_known_config.available=false` is an explicit refusal, not a default.
- LOW evidence starts investigation; it does not trigger an automatic action.
- `predicted_delta` is a prediction, never a measured outcome.

### Verify semantics

- A `Prediction` is neither a `Measurement` nor a replay; a replay is not
  certification by itself.
- `Measurement.resolved_delta_pct is null` is not zero and must not display the
  raw delta as a result.
- `mechanism_confirmed` and `runtime_certified` are independent verdicts.
- No UI control may start, repeat or imply a replay.

## Untrusted content and fixtures

Observed or returned strings including `app_name`, findings, evidence, fixes,
snippets, errors, transitions and data names are untrusted. Render them as
escaped plain text only: never raw HTML, executable Markdown, a URL/action,
route, selector, SQL, tool call or instruction.

Any later offline fixtures must be typed by the real models, visibly labelled
**Demo data**, and contain hostile text. They may cover absence, refusal and
evidence-insufficient states, but may not invent runtime fields or claim replay,
certification, AQE stage attribution or execution-stage relations absent from a
real contract.

## Authorized scope

- This Task-Spec.
- The proportional visual contract at
  [`../architecture/UI43-B-COMPARE-MEMORY-VERIFY-READ-ONLY.md`](../architecture/UI43-B-COMPARE-MEMORY-VERIFY-READ-ONLY.md).
- Offline Markdown/link/whitespace validation only.

## Explicitly excluded

- Choosing a framework, package manager, app location or design system.
- Dependencies, UI implementation, endpoints, payloads, metrics or browser/MCP
  adapters.
- Changes to Serve, MCP, Memory, Verify, Engine, Spark, Collector, ClickHouse,
  Docker, HyperDX, DDL, harness or telemetry.
- Runtime execution, replay controls, recommendations or reported runtime
  results.

## Acceptance criteria

1. Each screen maps only current typed fields, and separately names unavailable
   data.
2. All five required states are defined per screen.
3. The browser/MCP and browser data-exposure boundaries remain explicit owner
   decisions.
4. Compare, prediction, replay, mechanism evidence and runtime certification
   cannot be visually conflated.
5. A future fixture policy is typed, hostile-content-safe and marked Demo data.
6. No production code, dependency or runtime surface changes.

## PR split

1. **PR1:** this Task-Spec, visual contracts, proportional wireflows and owner
   decisions.
2. **PR2:** after stack decisions, offline `/compare`, `/memory` and `/verify`
   shell routes, common components, typed fixtures and state tests.
3. **PR3:** Compare integration only after an approved transport.
4. **PR4:** Memory integration only after versioned `RecallResult` exposure.
5. **PR5:** Verify integration only after its public contract; keep any
   runtime-gated increment separate.

## Owner decisions required before PR2

1. Browser transport: MCP-aware host, local BFF/adapter, or a versioned HTTP
   surface.
2. Front-end stack and package manager.
3. Application location and deployment host.
4. Design system and accessibility baseline.
5. Which owner exposes Memory and Verify as versioned browser-consumable data.

## Validation and rollback

```bash
git diff --check
git diff -- docs/task-specs/UI43-B-COMPARE-MEMORY-VERIFY-READ-ONLY.md \
  docs/architecture/UI43-B-COMPARE-MEMORY-VERIFY-READ-ONLY.md
git status --short
```

Rollback removes only these two documentation files.
