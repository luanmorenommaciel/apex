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
- Full four-pathology `e2e` remains a separate, more expensive command.
- The real-stack GitHub workflow requires a team-owned self-hosted Windows
  runner with Docker; it does not run automatically on a hosted runner.
