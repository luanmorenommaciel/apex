# C12 - Initial package validation (2026-07-25)

## Scope

This record validates the one-command package on
`base-project-e2e-augusto`. It does not alter or claim approval for Luan's
branch. Runtime secrets remained in ignored `.apex/` files and are not present
in this report.

## Bootstrap

Command:

```powershell
.\scripts\apex.ps1 bootstrap -SkipBuild
```

The existing Spark 4.1.2 image was reused for this first operational pass.
The package reported:

```text
APEX_DOCTOR=ready spark=4.1.2 schema=3/3 secrets=local
```

Healthy components:

- canonical ClickHouse, MongoDB and HyperDX;
- redacting OTel Collector connected to canonical INFRA;
- MinIO, Spark master, worker and History Server;
- `spark_events`, `plan_transitions` and `findings`.

The default command was then repeated without `-SkipBuild` and also passed.
Docker rebuilt the integrated image from the `apex_41/assembly` cell, verified
`apex/ApexPlugin.class` and the bundled OTel tracer, restarted DEV and ended
with the same ready doctor result. Cached execution took about five minutes on
this machine.

## Real smoke

Command:

```powershell
.\scripts\apex.ps1 smoke
```

Fresh result:

| Evidence | Result |
|---|---|
| Spark application | `app-20260725234704-0002` |
| Canonical skew assertion | passed; p99/p50 `13.404x` |
| Six-lane gate | passed; 9 canonical events, 9 fingerprints |
| ENGINE | 2 findings, deterministic, 0 LLM calls, 0 validator rejections |
| Finding persistence | inserted 2, observed 2 |
| MCP tools | `analyze_run`, `compare_runs`, `search_kb`, `suggest_fix` passed |
| Fix boundary | confidence `0.88`, 9 diff lines, `applied=false`, human approval required |

The first smoke on this 4-CPU Docker Desktop took about 22 minutes because it
materialized the deterministic five-million-row Delta dataset. The data
generator completed with hot-key fraction `0.5003`. Later runs can reuse the
committed Delta tables.

## Full canonical E2E

Command:

```powershell
.\scripts\apex.ps1 e2e
```

The public package wrapper completed all four real Spark 4.1.2 pathologies,
their canonical ClickHouse assertions, the deterministic six-lane gate and the
MCP stdio product gate. The unabridged output is preserved at
[`evidence/initial-package-e2e-all-2026-07-25.log`](../../evidence/initial-package-e2e-all-2026-07-25.log).

| Scenario | Fresh application | Measured evidence | Result |
|---|---|---|---|
| `skew_join` | `app-20260726005808-0001` | max p99/p50 `12.608x`; 4 stages | passed |
| `spill` | `app-20260726010245-0002` | `103682159` spill-to-disk bytes; 7 stages | passed |
| `bad_shuffle` | `app-20260726010724-0003` | expected pattern matched stage 6; 6 stages | passed |
| `driver_oom` | `app-20260726010950-0004` | expected failure after 7 pre-OOM stages | passed |

The run finished with both:

```text
OK E2E CANONICAL PASSED - requested pathologies reached ClickHouse
APEX_PRODUCT_GATE=passed job_id=app-20260726005808-0001
```

This is a fresh execution: each scenario produced a new Spark application ID
and the assertions queried its own canonical telemetry. The external
CrewAI/LLM path was not required by this deterministic package gate.

## Installation defects found and closed

1. Windows execution policy rejected an unsigned child script. The package now
   uses process-scoped `ExecutionPolicy Bypass`; it does not change machine
   policy.
2. ClickHouse verification SQL was truncated by Windows quoting. Migration and
   doctor now send SQL through stdin.
3. MongoDB's real `mongosh` ping exceeded a five-second Docker Desktop timeout.
   The same check now has a 15-second timeout.
4. Generated MinIO credentials initially differed from committed development
   defaults. The package now mounts an ignored generated Spark defaults file.
5. Docker Compose v5 stalled in `--wait` after a successful one-shot init.
   Long-running DEV components now have bounded explicit doctor waits.
6. Windows PowerShell treated normal Spark stderr logging as a terminating
   error. The package selects PowerShell 7 when available.

## Honesty boundary

- This smoke did not call CrewAI or an external LLM.
- `suggest_fix` returned data only and did not mutate a file or Git.
- Full four-pathology `e2e` passed locally through the package wrapper; it is a
  separate and more expensive command than `smoke`.
- The real-stack GitHub workflow requires a team-owned self-hosted Windows
  runner with Docker; its remote execution has not yet been observed.
- The package still needs one independent pilot from a fresh clone/clean
  machine or isolated clean Docker volumes before claiming team-wide
  installation reproducibility.
