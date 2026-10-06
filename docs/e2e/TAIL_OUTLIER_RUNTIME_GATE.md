# Tail-outlier runtime gate — delivery record

This record distinguishes the `tail_outlier` proof that has been run from the
package, CI, and deployment checks that still need independent evidence. It is
the delivery companion to [issue #123](https://github.com/luanmorenommaciel/apex/issues/123)
and does not change the Engine detector policy or the telemetry contract.

## What changed

`tail_outlier` is now an opt-in canonical DEV scenario. The default canonical
run remains the existing four scenarios (`skew_join`, `spill`, `bad_shuffle`,
and `driver_oom`), so routine runs do not become longer unexpectedly.

When explicitly requested, the path is:

```text
tail_outlier Spark workload
  -> Apex plugin -> OTLP Collector -> canonical ClickHouse
  -> canonical telemetry assertion -> Engine tail_outlier_watcher
```

The new assertion deliberately proves the duration-tail shape that the Engine
uses rather than accepting generic stage telemetry:

- at least 100 tasks and 100 effective duration samples;
- the retry-safe successful-task population when it exists, otherwise the
  declared legacy all-attempts fallback;
- a positive, finite p50; and
- a strict `max / p50 > 10` tail.

It rejects an exact 10× ratio, a p99-only signal, incomplete telemetry, and
small distributions. It also waits for the terminal qualifying row instead of
treating the first asynchronously ingested stage row as proof.

The public package command remains:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/apex.ps1 tail-outlier
```

It runs the PowerShell canonical scenario and then checks that Engine emits
`tail_outlier_watcher` in dry-run/no-Crew mode. PowerShell 7+ (`pwsh`) is
therefore required for this particular public package gate.

### Prerequisites on a clean checkout

`tail-outlier` does not create or start anything. It validates a package that
`bootstrap` has already built, and refuses to run otherwise:

1. `bootstrap` must have completed first (`make bootstrap`, `./scripts/apex.sh bootstrap`,
   or `scripts/apex.ps1 bootstrap`). It generates the ignored `.apex` runtime
   configuration and starts the INFRA, COLLECT and DEV containers. Without
   it the gate stops at "Run bootstrap first" before any Spark work.
2. Docker, `uv`, `pwsh` and `bash` must be on `PATH`, and the Docker engine
   must be running.
3. A real Python 3 executable must be on `PATH` (`python` on Windows,
   `python3` on macOS/Linux). The canonical runner resolves it before any
   Docker or Spark work and fails closed with a clear message if it is missing;
   shell aliases and functions are not used.

### Which Spark version the public gate exercises

The public gate runs against the Spark version configured by the package
bootstrap. `doctor`, which the gate runs first, currently requires
`SPARK_VERSION=4.0.1` and fails closed on anything else, so a default
`bootstrap` followed by `tail-outlier` exercises Spark 4.0.1. The 4.1.2 overlay
(`make env-spark41` in `dev/`) is not what the package wrapper runs.

### Do not run it over an operator-owned `dev/.env`

Before invoking the canonical runner, the package copies its generated
`.apex/dev.env` over the ignored `dev/.env` unconditionally
(`Sync-DevEnvForCanonicalScript` in `scripts/apex.ps1`). `smoke` and `e2e` do
the same. If you keep your own `dev/.env` for lane-level work, the gate will
replace it without warning. Move or back it up first; use a separate
checkout if you need both. This is a known limitation, tracked under
[Follow-ups](#follow-ups-not-part-of-this-change).

## Evidence completed locally

On 2026-09-20, the core path was run in an isolated, disposable local Docker
environment. It used the branch's `tail_outlier.py` workload, canonical
assertion, and Engine code; no pre-existing Apex container, network, volume, or
configuration was reused, stopped, removed, or reconfigured.

The real Spark application `app-20260920130100-0001` completed 200 tasks. Its
telemetry reached the temporary Collector and ClickHouse. The canonical
assertion passed with the retry-safe successful-task population:

```json
{
  "status": "passed",
  "scenario": "tail_outlier",
  "task_count": 200,
  "duration_sample_count": 200,
  "duration_sample_source": "successful_tasks",
  "max_tail_ratio": 373.364,
  "p99_p50_ratio": 2.982
}
```

Engine was then run directly against that fresh job in dry-run/no-Crew mode and
emitted one `TAIL_OUTLIER` result through `tail_outlier_watcher`, with zero LLM
calls. The temporary containers and network were removed immediately after the
proof.

### Public package-wrapper proof

On 2026-09-21, the public PowerShell package path was run on macOS in a
dedicated Colima daemon against the exact candidate content later committed as
`754f45e` and `5b41c77`. The package used its configured Spark 4.0.1 stack and
resolved a real `python3` application before Docker or Spark work. The two
ignored `dev/secrets/apex_s3_*` bridge files were absent; the package overlay
instead consumed the generated `.apex/secrets/s3_*` paths exported by the
wrapper.

The commands ran serially and returned:

```text
bootstrap    exit 0  APEX_DOCTOR=ready spark=4.0.1 schema=3/3 secrets=local
doctor       exit 0  APEX_DOCTOR=ready spark=4.0.1 schema=3/3 secrets=local
tail-outlier exit 0  APEX_TAIL_OUTLIER_GATE=passed job_id=app-20260921024421-0001 llm_calls=0
```

The canonical scenario generated 10,000,000 rows, reached ClickHouse, and the
Engine emitted `TAIL_OUTLIER` through `tail_outlier_watcher`. This proves the
public wrapper, its Spark 4.0.1 preconditions, the macOS Python preflight, and
the local Spark-to-Engine path for this candidate.

This was not a fresh registry-backed cold start. Docker Hub would not serve the
two immutable MinIO references, so their exact linux/arm64 identities were
verified in an existing Docker Desktop cache, transferred to the dedicated
daemon, and exposed to this process through local tags. The daemon also held
partial APEX resources from the earlier fail-closed bootstrap attempts; the
successful rerun recreated Spark services but reused the already-running
MinIO service. No image pin or repository configuration was weakened. The run
therefore does not prove upstream registry availability or a cold bootstrap
from an empty daemon.

The deterministic local checks also passed:

| Check | Result | What it covers |
|---|---:|---|
| `python3 -m unittest dev/tests/test_canonical_e2e_assert.py` | 20 passed | tail shape, retry-safe source selection, finite-input, boundary and delayed-ingestion cases |
| `uv run --project dev python -m unittest discover -s dev/tests` | 20 passed | DEV test environment compatibility |
| `cd dev && uv run --extra dev pytest -q` | 27 passed | DEV test runner coverage, including the opt-in POSIX selector and unchanged default scenario list |
| `cd engine && uv run --extra dev pytest -q ../tests/test_tail_outlier_package.py -p no:warnings` | 3 passed | public package routing contract |
| `uv run --offline --frozen --project dev --extra dev pytest dev/tests/test_e2e_canonical_runner.py` | 5 passed | Python preflight and package-overlay secret source contract |
| `bash -n dev/scripts/e2e_canonical.sh` | passed | POSIX entry-point syntax |
| `git diff --check` | passed | whitespace integrity |

## Evidence still required, and why

This is deliberately not presented as a green release or a replacement for the
following gates.

| Required next check | Why it is still open | Safe completion condition |
|---|---|---|
| Fresh registry-backed cold start | The public wrapper passed on the configured Spark 4.0.1 stack, but MinIO came from an identity-verified local cache and the daemon retained partial resources from earlier fail-closed attempts. | From an empty daemon with the immutable MinIO references available from an authoritative registry, run `bootstrap`, `doctor`, and `tail-outlier` serially and retain the markers. |
| Python preflight on Windows | The resolver ran successfully on macOS and is covered by source-level tests for Windows ordering, but it has not run on a real Windows host. | Include the package gate in a supported Windows-host validation when one is available. |
| Remote CI | GitHub Actions jobs did not receive runners or execute steps because the repository account is blocked by billing. This is external to the code change. | After billing is resolved, rerun CI and require real runner assignment, steps, and green results. |
| Human review and merge | Local proof and automated tests do not replace an independent maintainer review. | Request review after the preceding evidence is available; merge only under the repository's normal policy. |

## Operator guidance

Use `tail_outlier` as a targeted runtime gate, not as a claim that every
canonical run has covered it. Do not point it at an unrelated Docker stack just
to make the command pass. A missing configuration or canonical topology should
fail closed; provision a clean environment instead.

The gate does not deploy code, change a remote environment, or prove GitHub
Actions. Its purpose is narrower and testable: demonstrate that a real sparse
duration tail survives the local Spark-to-Engine route and is detected by the
existing deterministic watcher.

## Follow-ups (not part of this change)

These need a new task with its own sign-off, because the signed
[`T-20260920-tail-outlier-runtime-gate`](../../tasks/T-20260920-tail-outlier-runtime-gate.md)
Task-Spec lists `scripts/apex.ps1` as Do-Not-Touch and is not edited here.

- **Stop the silent `dev/.env` overwrite.** In `Sync-DevEnvForCanonicalScript`,
  refuse (fail closed, without printing values) when `dev/.env` already exists
  and differs from `.apex/dev.env`, and copy only when it is absent or
  identical. Fail before the first `apex-*` container is inspected, and add
  offline tests for: absent, identical, differing (refused, file untouched),
  and message contents (no values). Until then the warning above is the only
  protection.
- **Confirm the fixed-name resources belong to this checkout.** The gate
  addresses `apex-*` containers and networks by name, so a stack from another
  checkout would be reused silently. The same task should add an ownership
  check before `Invoke-Doctor` that refuses unrelated resources instead of
  reusing them; `pilot-clean` already has a fail-closed inventory that can be
  reused as the pattern.
