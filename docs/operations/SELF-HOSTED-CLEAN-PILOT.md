# Self-hosted clean pilot runner

## Purpose

This runner executes the manual `Apex initial package` real-stack job. Its
default path runs `pilot-clean`, which proves the package on a clean Windows
Docker runtime and uploads only `clean-pilot-summary.json` as a GitHub Actions
artifact.

## One-time host preparation

1. Use a Windows 10/11 machine or VM with Docker Desktop in Linux-container
   mode, PowerShell 7, Python 3.11+ and `uv`.
2. Allocate at least 4 CPUs and 8 GB RAM to Docker Desktop.
3. Register the GitHub Actions self-hosted runner for this repository with
   labels `Windows`, `X64` and `apex`.
4. Keep this runner dedicated to APEX clean pilots. Do not run a developer
   stack on it between pilot executions.

The repository workflow will reject an occupied runtime on purpose. It does
not attempt to delete Docker resources, volumes or runtime configuration.

## Running the pilot

1. Open **Actions** in the APEX repository.
2. Select **Apex initial package** and choose **Run workflow**.
3. Keep **Run all four real Spark pathologies** disabled for the initial pilot.
4. Select the branch `base-project-e2e-augusto`.
5. After completion, download the artifact `apex-clean-pilot-summary`.

A passing artifact contains the commit, fresh Spark `job_id`, component health
and gate statuses. It never contains `.apex` files, environment variables,
credentials, prompts or raw telemetry.

## Failure handling

| Result | Meaning | Operator action |
|---|---|---|
| `APEX_CLEAN_PILOT=refused` | Runner contains prior APEX package resources | Re-provision or explicitly dispose of the dedicated runner; do not edit the repository to bypass the check. |
| Docker unavailable | Docker Desktop is stopped or inaccessible to the runner service | Start Docker Desktop for the runner account and rerun. |
| No eligible runner | GitHub cannot find `self-hosted`, `Windows`, `X64`, `apex` | Verify runner registration and labels. |
| Artifact absent | Pilot stopped before the success report | Read the job summary; the workflow intentionally uploads no broader runtime files. |

## Full E2E

Enable the full-E2E input only after the clean pilot passes. It is a separate
90-minute budget and runs all four real pathologies. Its detailed evidence is
reviewed on the dedicated runner; it does not upload Docker logs or secrets.
