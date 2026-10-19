---
id: T-20261006-dev-c3-driver-host
title: "Advertise the Spark driver by service name on the C3 overlay"
status: in-progress
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: []
supersedes: (none)
touches_paths: [dev/Makefile, tests/e2e/run.sh]
creates_paths: []
source_note: "dev/scripts/e2e_canonical.sh"
created: "2026-10-06T00:00:00Z"
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

# Advertise the Spark driver by service name on the C3 overlay

> **Why:** On the C3 overlay the Spark master has two networks. The driver advertises itself by the container's hostname, which Docker DNS resolves to one network's address, while its RPC binds to the first interface - so executors connect to an address nothing listens on, are refused, and the job spins on "Initial job has not accepted any resources" forever, relaunching an executor per second. Which run hits it depends on interface order, so it looks intermittent - the first run of the session passed and the second did not. dev/scripts/e2e_canonical.sh already passes spark.driver.host and spark.driver.bindAddress for this reason; the Makefile's c3 and c4 targets and tests/e2e/run.sh did not.

## Goal

Every C3 and C4 submit in the dev Makefile and the submit in tests/e2e/run.sh pass spark.driver.host=spark-master and spark.driver.bindAddress=0.0.0.0, and the Makefile says why.

## Context

Reproduced 2026-10-06 - the same job on the same image, with and without the plugin, failed identically, and passed once the two confs were added, in 25 seconds. The fix mirrors e2e_canonical.sh exactly.

## Behavior

- **B-1** — GIVEN make -n on each c3 and c4 target WHEN the printed spark-submit is read THEN it carries both confs
- **B-2** — GIVEN tests/e2e/run.sh WHEN its submit is read THEN it carries both confs and the script parses

## Success Criteria

```bash
# eval_1: all four targets and run.sh carry the driver conf
eval_1() {
  ( cd dev && for t in c3-plugin-skew c4-aqe-skew c4-aqe-skewsplit c4-aqe-probe; do make -n $t | grep -q "spark.driver.host=spark-master --conf spark.driver.bindAddress=0.0.0.0" || exit 1; done && cd .. && bash -n tests/e2e/run.sh && grep -q "spark.driver.bindAddress=0.0.0.0" tests/e2e/run.sh )
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "all four targets and run.sh carry the driver conf"
    runnable: bash
    check_type: deterministic
    verifies: [B-1, B-2]
    terminal: true
    expected_duration_sec: 20
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
eval_1
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- Setting spark.driver.host in spark-defaults.conf; local-mode runs such as fp-test have no spark-master to advertise.

## Do-Not-Touch

- `dev/conf/`
- `dev/docker-compose.yml`

## Open Questions

(none — this task is fully specified)
