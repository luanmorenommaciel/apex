# Gate 10 Design: Recommend/Preview Loop

Date: 2026-07-11
Branch: `gustocezar/feature/codex-desacoplamento-geradores`
Prepared by: Codex

## Decision

Add a deterministic recommendation layer over persisted findings and expose a preview-only flow through MCP.

## Why This Shape

Gate 8 persists validated findings. Gate 9 exposes those findings through MCP. Gate 10 should not jump directly to mutation. The safe next step is to create a recommendation contract that can be audited, previewed, and later connected to explicit apply/verify gates.

## Components

- `apex.commander.recommendations`
  - `recommend_fix(finding_store, job_id)`
  - `preview_recommendation(finding_store, job_id, recommendation_id, path, replacement)`
- `CommanderToolContract`
  - exposes `recommend_fix`
  - exposes `preview_recommendation`
- `mcp_stdio_server`
  - inherits the new tools through `tools/list` and `tools/call`

## Recommendation Contract

```json
{
  "id": "job-42:shuffle_skew_candidate:stage-2:0",
  "job_id": "job-42",
  "finding_kind": "shuffle_skew_candidate",
  "action": "validate_aqe_then_consider_salting_or_repartition",
  "summary": "Validate AQE skew join settings and the join key distribution before previewing salting or repartition changes.",
  "preview": {
    "mode": "manual_replacement",
    "tool": "preview_recommendation",
    "requires_approval_before_apply": true
  }
}
```

## Safety Rules

- Use only accepted validations.
- Keep recommendations deterministic and versioned.
- Require a selected `recommendation_id` before preview.
- Require an explicit replacement body for preview.
- Return a unified diff without writing the target file.
- Do not expose `apply_fix`.
- Do not call an LLM in the baseline path.

## Why Replacement Is Human-Provided

The Commander can identify the finding and recommend the fix strategy, but it does not yet own source-code semantics for every Spark job. A human or later code-aware agent supplies the proposed replacement, and Commander validates the preview loop around it.

That keeps this gate real without pretending the system can safely patch arbitrary Spark code.

## Next Gate

Gate 11 adds guarded apply/verify:

```text
preview_ready -> explicit approval token -> apply -> re-run -> compare before/after evidence
```
