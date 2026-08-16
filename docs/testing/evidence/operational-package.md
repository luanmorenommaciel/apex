# Local operational package (#62) — real evidence, 2026-08-12

Port of `Makefile` + `scripts/apex.ps1` + `scripts/apex.sh` +
`dev/docker-compose.package.yml` onto `origin/main` (branch
`candidate/local-operational-package`, created clean from `origin/main`, no
other open PR merged in). Tested against the real stack on this machine —
8 real `bootstrap` attempts, 4 real bugs found and fixed along the way.

## Attempt-by-attempt

1. **Dry-run** (`apex.ps1 bootstrap -DryRun`) — `APEX_DRY_RUN=passed`, no
   Docker touched.
2. **Bootstrap #1** — failed: `apex-infra-hyperdx is unhealthy`. Compose's
   `--wait` treats a transient "unhealthy" as terminal even though hyperdx's
   own baked-in healthcheck settles a few seconds later (confirmed via
   `docker inspect ... State.Health`: 4 failed checks, 5th passed). hyperdx
   is UI-only — `doctor` never requires it healthy.
   **Fix**: stopped blocking `up --wait` on hyperdx; start it separately,
   best-effort.
3. **Bootstrap #2** — failed: `apex-infra-mongodb is unhealthy`. Same class
   of issue: `mongosh` (the healthcheck client) exceeded its 5s timeout
   under the CPU/disk contention of a fresh multi-service bring-up, even
   though `mongod` itself was accepting connections fine (confirmed in its
   own logs — real connections, real checkpoints, no errors).
   **Fix**: same treatment — mongodb started best-effort, uncoupled from
   `--wait`; `Invoke-Doctor`'s own `Wait-ContainerReady` loop (150 × 2s) is
   the real, more patient gate for both.
4. **Bootstrap #3** — failed: `apply_ddl.sh` → `Code: 210, Connection
   refused (localhost:9000)`. ClickHouse's HTTP healthcheck (what Compose
   `--wait` watches) can report Healthy a moment before the native TCP port
   9000 (what `clickhouse-client`/`apply_ddl.sh` use) finishes binding.
   **Fix**: added a settle-retry (up to 10 × 2s `SELECT 1` via
   `clickhouse-client`) before invoking `apply_ddl.sh`.
5. **Bootstrap #4** — failed: `apply_ddl.sh` →
   `AUTHENTICATION_FAILED: password is incorrect`. Root cause: a leftover
   `infra/.env` from earlier manual testing this session
   (`CLICKHOUSE_PASSWORD=apex_local_dev`), silently sourced by
   `apply_ddl.sh`'s own `[ -f .env ] && . ./.env`, overriding the real
   random password `apex.ps1` had just generated and used to create the
   container. **Not a port bug** — residue from this session's own earlier
   manual testing. Removed the stray file.
6. **Bootstrap #5** — failed again on the *fresh* volume created moments
   before, same auth error — because the previous failed attempt's
   container had already baked in a *different* random password before the
   `.env` fix landed. Cleaned the just-created bad volume, retried.
7. **Bootstrap #6** — infra + collect + dev all came up; `spark-history`
   crashed (`exit 1`) with an `S3Exception ... 403` reading
   `s3a://spark-logs/events/`. Root cause: `apex.ps1` generates a **fresh
   random** `MINIO_ROOT_USER`/`MINIO_ROOT_PASSWORD` per bootstrap, but
   `Write-GeneratedSparkDefaults` was copying `dev/conf/spark-defaults.conf`
   verbatim — which ships with the static `minioadmin`/`minioadmin` correct
   for `dev/`'s own compose file, but wrong for this package's dynamically
   generated MinIO credential. `spark-master`/`worker` never noticed (their
   healthchecks don't touch S3); `spark-history` does, on its own startup
   (`FsHistoryProvider.startPolling`), so it's the one that failed.
   **Fix**: `Write-GeneratedSparkDefaults` now substitutes the real
   generated `MINIO_ROOT_USER`/`MINIO_ROOT_PASSWORD` into the
   `fs.s3a.access.key`/`fs.s3a.secret.key` lines of the generated config.
8. **Bootstrap #7** — infra + collect passed cleanly (no hyperdx/mongodb
   block, no auth error); `spark-history` still crashed the same way — this
   attempt reused an already-generated `.apex/dev.env` from before the S3A
   fix was written, so the stale credentials were still in play. Torn down
   dev, kept infra/collect running.
9. **Bootstrap #8 — full pass.** Reused the already-up infra/collect,
   rebuilt dev with the S3A-credential fix in place:

   ```
   Name                    Status  Health   ExitCode
   ----                    ------  ------   --------
   apex-infra-clickhouse   running healthy  0
   apex-infra-mongodb      running healthy  0
   apex-infra-hyperdx      running healthy  0
   apex-otel-collector     running -        0
   apex-dev-minio-1        running healthy  0
   apex-dev-spark-master-1 running healthy  0
   apex-dev-spark-worker-1 running healthy  0
   apex-dev-spark-history-1 running healthy 0

   APEX_DOCTOR=ready spark=4.0.1 schema=3/3 secrets=local
   ```

## `smoke` — real product gate, found and fixed 2 more real bugs

Requested separately, after the write-up above: don't just claim `smoke`/
`e2e`/`tail-outlier` work without having run them. Ran `make smoke` for
real.

**Bug #5 — `e2e_canonical.ps1` parameter mismatch.** `apex.ps1` called it
with `-EnvFile`/`-AdditionalComposeFile`, parameters this repo's real
`dev/scripts/e2e_canonical.ps1` doesn't have (`ValidateSet` is `-Scenario`,
plus `-StartDev`/`-SkipGenerate` only — no env-file or extra-compose-file
support at all). Immediate `ParameterBindingException`. Root cause: this
script is a lane-level tool that reads `dev/.env` directly and hardcodes
its own 2 compose files; it never runs `compose up` (only `exec` into
containers this package already started, correctly configured via the
`docker-compose.package.yml` bind mount) — so no extra compose file was
ever needed. **Fix**: dropped both unsupported parameters; added
`Sync-DevEnvForCanonicalScript`, which copies the package's `.apex/dev.env`
(the real generated MinIO credentials) to `dev/.env` right before invoking
it, so its own `.env`-existence gate and any incidental var reads see the
same values the running stack actually has.

**Bug #6 — `tail-outlier` scenario doesn't exist here.** `'tail_outlier'`
isn't in `e2e_canonical.ps1`'s own `ValidateSet` — `dev/jobs/tail_outlier.py`
and the scenario support are proposed separately (issue #73/PR #74), not
merged into this branch's base. `make tail-outlier` would have hit a
`ParameterBindingValidationException` with a confusing message. **Fix**:
`Invoke-TailOutlierGate` now refuses immediately with a clear message
instead of leaving it to fail confusingly; blocked until that work lands,
same class of gap as the `apply_schema_migrations.ps1` limitation already
noted below.

**Full pass, real evidence** (rebuilt/re-ran after both fixes, stack
already up from the bootstrap validation above):

```
$ make smoke
...
OK E2E CANONICAL PASSED - requested pathologies reached ClickHouse
[apex] Running deterministic six-lane gate for app-20260812224924-0001
{
  "gate": "six-lane-canonical-e2e",
  "status": "passed",
  "lanes": {
    "jar":     {"status": "passed", "canonical_stage_events": 20, "plan_fingerprint_count": 20},
    "collect": {"status": "passed", "otlp_stage_rows_observed": 20},
    "infra":   {"status": "passed", "clickhouse_stage_rows": 20},
    "dev":     {"status": "passed", "submitted_job_observed": true},
    "engine":  {"status": "passed", "accepted_findings": 2, "llm_calls": 0, "mode": "deterministic"},
    "serve":   {"status": "degraded", "finding_count": 2, "tool": "analyze_run"}
  }
}
[apex] Running full MCP stdio client gate
{
  "gate": "serve-stdio-mcp",
  "status": "passed",
  "analyze_run": {"status": "degraded", "worst_stage_id": 21, "primary_symptom": "disk_spill"},
  "suggest_fix": {"applied": false, "requires_human_approval": true, "confidence": 0.75}
}
APEX_PRODUCT_GATE=passed job_id=app-20260812224924-0001
```

Real Spark job (`skew_join`, 10M rows, `hot_keys_~50pct=PASS`), real OTLP
delivery (20 stage rows independently confirmed by both `collect` and
`infra` lanes), real deterministic ENGINE findings (0 LLM calls), real MCP
stdio gate against the actual running stack.

## `status` and `down`

`apex.ps1 status` ran clean, correctly reflecting live container state (one
run caught `mongodb` mid-flake — same known healthcheck-timing class as
above, not a new issue; `doctor` had already confirmed it healthy moments
earlier).

`down` (run manually lane-by-lane — `docker compose down` for dev, collect,
infra, each via its own `.apex/*.env`, not `apex.ps1 down`'s own bundled
call) tore everything down cleanly, volumes preserved, confirmed via
`docker ps -a` showing zero `apex-infra-*`/`apex-dev-*` containers left.

## What's fixed in this branch vs. the fork

- `infra/scripts/apply_schema_migrations.ps1` (fork-only, hardcoded to
  migration filenames `021`-`028` that don't exist under those numbers in
  `main`) replaced with a call to `main`'s real `infra/scripts/apply_ddl.sh`.
- `SPARK_VERSION` assertion changed from `4.1.2` (a separate compatibility
  cell the fork defaulted into) to `4.0.1`, matching what `main` actually
  ships and pins today. The `dev/.env.spark41.example` overlay was dropped
  from the generated `dev/.env` for the same reason.
- The 4 bugs above, all fixed in this branch (not present in the fork's own
  version, since the fork's environment/host apparently never hit these
  timing/credential edge cases, or was tested differently).

## Not touched

`infra/docker-compose.yml`'s own healthcheck definitions were left as-is —
the fixes live entirely in `apex.ps1`'s orchestration (decoupling from
`--wait`, adding the settle-retry), not in the shared compose files other
lanes also use.
