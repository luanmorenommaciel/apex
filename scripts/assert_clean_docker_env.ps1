#Requires -Version 7.0
<#
Detects APEX Docker residues (infra/collect/dev lanes) from a previous
run and REFUSES to proceed if any are found — it never removes anything.

Ported from the Augusto line's scripts/apex.ps1 (Get-CleanPilotResidues /
Assert-CleanPilotEnvironment). Resource names verified against this
repo's own compose files rather than copied — infra/dev/collect all
declare an explicit top-level `name:` (apex-infra / apex-dev /
apex-collect), so container/volume naming is deterministic even for
compose-generated (non-`container_name`) services.

Usage:
  pwsh scripts/assert_clean_docker_env.ps1
  Exit 0  -> environment is clean, safe to bootstrap
  Exit 1  -> residues found, printed, nothing touched

This intentionally does NOT check a `.apex/` runtime directory or git
worktree cleanliness — those are part of a broader operational-package
proposal (tracked separately) that doesn't exist on this line yet. This
script covers exactly the Docker-resource class of incident it was
written to prevent.
#>

$ErrorActionPreference = 'Stop'

function Get-DockerResidues {
    $residues = [Collections.Generic.List[string]]::new()

    $containerPatterns = @(
        'apex-infra-*',
        'apex-dev-*',
        'apex-clickhouse',
        'apex-otel-collector',
        'apex-queue-init'
    )
    $containerNames = @(& docker ps -a --format '{{.Names}}')
    if ($LASTEXITCODE -ne 0) {
        throw 'Unable to inventory Docker containers.'
    }
    foreach ($name in $containerNames) {
        if ($containerPatterns | Where-Object { $name -like $_ }) {
            $residues.Add("container:$name")
        }
    }

    $networkNames = @(& docker network ls --format '{{.Name}}')
    if ($LASTEXITCODE -ne 0) {
        throw 'Unable to inventory Docker networks.'
    }
    foreach ($name in @('apex-infra-net', 'apex-collect-net', 'apex-dev_default')) {
        if ($networkNames -contains $name) {
            $residues.Add("network:$name")
        }
    }

    $volumeNames = @(& docker volume ls --format '{{.Name}}')
    if ($LASTEXITCODE -ne 0) {
        throw 'Unable to inventory Docker volumes.'
    }
    foreach ($name in @(
        'apex-infra_ch-data',
        'apex-infra_mongo-data',
        'apex-collect_clickhouse-data',
        'apex-collect_otel-queue',
        'apex-dev_minio-data'
    )) {
        if ($volumeNames -contains $name) {
            $residues.Add("volume:$name")
        }
    }

    return @($residues | Sort-Object -Unique)
}

$residues = @(Get-DockerResidues)
if ($residues.Count -gt 0) {
    $summary = $residues -join ','
    Write-Host "APEX_CLEAN_DOCKER=refused residues=$summary" -ForegroundColor Yellow
    Write-Host 'Existing APEX Docker resources found. Nothing was removed.' -ForegroundColor Yellow
    Write-Host 'Re-provision, or explicitly dispose of them yourself, before continuing.' -ForegroundColor Yellow
    exit 1
}

Write-Host 'APEX_CLEAN_DOCKER=passed residues=none' -ForegroundColor Green
exit 0
