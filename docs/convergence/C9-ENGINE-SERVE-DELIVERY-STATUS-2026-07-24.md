# C9 - ENGINE and SERVE delivery status (2026-07-24)

This document is the review checkpoint for the two remaining APEX V1 lanes.
It records verified behavior and the dependency order; it does not claim that
the changes below are already merged into `feat/base-project-e2e`.

## Delivery state

| Lane | Pull request | State at this checkpoint | Verified scope |
|---|---|---|---|
| ENGINE / C5 | [#52](https://github.com/luanmorenommaciel/apex/pull/52) | Open, clean | Gated CrewAI correlation and adversarial Judge |
| SERVE / C4 | [#53](https://github.com/luanmorenommaciel/apex/pull/53) | Open, clean | Knowledge search and human-approved fix proposal |

## ENGINE / C5 evidence

- Tier 1 remains the deterministic source of telemetry, metrics, findings and
  validation.
- Tier 2 can only run for a validated `LOW` confidence candidate with
  `critical` or `blocker` severity.
- The external Anthropic provider smoke completed successfully. The Judge
  rejected the intentionally weak skew candidate, cited only the supplied
  `p99/p50=29.5x` and `task_count=8` evidence, and performed no mutation.
- Unit validation: `14 passed`.
- Raw evidence:
  [`../../evidence/engine-c5-crewai-provider-2026-07-24.log`](../../evidence/engine-c5-crewai-provider-2026-07-24.log).

## SERVE / C4 evidence

- `search_kb` queries persisted finding evidence/remediation through bound
  ClickHouse parameters.
- `suggest_fix` returns a diff and PR body as data only. It always declares
  `applied=false` and `requires_human_approval=true`; it cannot write a file,
  Git state, Spark job or database.
- Unit validation: `8 passed`.
- The real MCP stdio client listed and called all four tools:
  `analyze_run`, `compare_runs`, `search_kb`, and `suggest_fix`.
- Raw evidence:
  [`../../evidence/serve-c4-stdio-mcp-2026-07-24.log`](../../evidence/serve-c4-stdio-mcp-2026-07-24.log).

## Required merge order

1. Review and merge #52 (ENGINE/C5).
2. Review and merge #53 (SERVE/C4).
3. Rebase the integration gate on the updated base and run the four-tool MCP
   validation again. That result becomes the follow-up C9 integration PR.

## Deliberate scope boundary

No automatic remediation, rerun orchestration, product UI, installer or remote
CI is introduced by these deliveries. Those are later product evolutions, not
substitutes for the V1 lane exits.
