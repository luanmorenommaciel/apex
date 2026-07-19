param(
    [string]$Repo = "gustocezar/apex-workspace",
    [string]$RunnerRoot = "$env:USERPROFILE\actions-runner-apex-workspace"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "Required command not found: gh"
}

$runnerRootPath = [System.IO.Path]::GetFullPath($RunnerRoot)
$configCmd = Join-Path $runnerRootPath "config.cmd"
if (-not (Test-Path $configCmd)) {
    throw "Runner config.cmd not found at $configCmd"
}

$tokenResponse = gh api "repos/$Repo/actions/runners/remove-token" --method POST | ConvertFrom-Json
$token = $tokenResponse.token
if (-not $token) {
    throw "Could not obtain GitHub Actions runner removal token."
}

Push-Location $runnerRootPath
try {
    & .\config.cmd remove --token $token
    if ($LASTEXITCODE -ne 0) {
        throw "config.cmd remove failed with exit code $LASTEXITCODE"
    }
    Write-Host "Runner unregistered from $Repo."
} finally {
    Pop-Location
}
