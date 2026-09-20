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

The deterministic local checks also passed:

| Check | Result | What it covers |
|---|---:|---|
| `python3 -m unittest dev/tests/test_canonical_e2e_assert.py` | 19 passed | tail shape, retry-safe source selection, boundary and delayed-ingestion cases |
| `uv run --project dev python -m unittest discover -s dev/tests` | 19 passed | DEV test environment compatibility |
| `cd engine && uv run --extra dev pytest -q ../tests/test_tail_outlier_package.py -p no:warnings` | 3 passed | public package routing contract |
| `bash -n dev/scripts/e2e_canonical.sh` | passed | POSIX entry-point syntax |
| `git diff --check` | passed | whitespace integrity |

## Evidence still required, and why

This is deliberately not presented as a green release or a replacement for the
following gates.

| Required next check | Why it is still open | Safe completion condition |
|---|---|---|
| Public package-wrapper run | The isolated proof ran the core route directly, not `scripts/apex.ps1`. The existing Apex Docker environment was preserved rather than being reused or mutated. | In a clean, freshly bootstrapped canonical package environment, run `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/apex.ps1 tail-outlier` and retain its fail-closed output. |
| Exact current-image rebuild | Docker Hub metadata retrieval timed out before the exact image could be rebuilt. The proof used a cached Spark 4.1.2 image; the PR does not change the JAR, while the branch workload, assertion, and Engine were current. | Rebuild the canonical image when the registry is reachable, then repeat the public package-wrapper run. |
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
