# C13 - Clean pilot readiness (2026-07-25)

## Scope

This record validates the safety and contract of `pilot-clean` on
`base-project-e2e-augusto`. It does not claim a successful clean-machine run
and does not alter Luan's branch.

## Contract validation

```text
POWERSHELL_PARSE=passed
10 passed
WORKFLOW_YAML=passed
APEX_DRY_RUN=passed action=pilot-clean mutations=0 external_calls=0
```

The manual real-stack workflow now uses `pilot-clean` for its default smoke
path. Full E2E remains an explicit manual input.

## Fail-closed runtime proof

The current workstation intentionally contains the running canonical package.
Calling `pilot-clean` therefore returned:

```text
APEX_CLEAN_PILOT=refused residues=...
PILOT_EXIT=1
REFUSAL_MUTATIONS containers=False networks=False volumes=False runtime=False report=False
```

The raw sanitized output is preserved at
[`evidence/clean-pilot-refusal-2026-07-25.log`](../../evidence/clean-pilot-refusal-2026-07-25.log).
Only package resource names are present. No environment dump or secret value
was recorded.

## Honest status

| Capability | Status |
|---|---|
| Detect occupied package runtime | passed |
| Refuse without deleting or changing resources | passed |
| Dry-run contract on hosted Windows | ready |
| Sanitized success-report contract | implemented and tested structurally |
| Fresh clone/dedicated Docker success execution | pending external clean runtime |
| Self-hosted GitHub real-stack observation | pending runner |

The next valid evidence must come from another machine, an ephemeral
self-hosted Windows runner or a deliberately disposable Docker runtime. The
occupied development machine must not be cleaned merely to turn this gate
green.
