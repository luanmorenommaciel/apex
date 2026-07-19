param(
    [string]$Repo = "gustocezar/apex-workspace",
    [string]$RunnerRoot = "$env:USERPROFILE\actions-runner-apex-workspace",
    [string]$RunnerName = "apex-local-$env:COMPUTERNAME",
    [string]$Labels = "apex,docker,spark412",
    [switch]$Start
)

$ErrorActionPreference = "Stop"

function Require-Command($Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command not found: $Name"
    }
}

Require-Command gh
Require-Command docker

$repoUrl = "https://github.com/$Repo"
$runnerRootPath = [System.IO.Path]::GetFullPath($RunnerRoot)
New-Item -ItemType Directory -Force -Path $runnerRootPath | Out-Null

$release = gh api repos/actions/runner/releases/latest | ConvertFrom-Json
$asset = $release.assets | Where-Object { $_.name -match '^actions-runner-win-x64-.*\.zip$' } | Select-Object -First 1
if (-not $asset) {
    throw "Could not find win-x64 GitHub Actions runner asset in latest release."
}

$zipPath = Join-Path $runnerRootPath $asset.name
if (-not (Test-Path $zipPath)) {
    Write-Host "Downloading $($asset.name)..."
    gh release download $release.tag_name --repo actions/runner --pattern $asset.name --dir $runnerRootPath --clobber
}

if (-not (Test-Path (Join-Path $runnerRootPath "config.cmd"))) {
    Write-Host "Extracting runner to $runnerRootPath..."
    Expand-Archive -Path $zipPath -DestinationPath $runnerRootPath -Force
}

$tokenResponse = gh api "repos/$Repo/actions/runners/registration-token" --method POST | ConvertFrom-Json
$token = $tokenResponse.token
if (-not $token) {
    throw "Could not obtain GitHub Actions runner registration token."
}

Push-Location $runnerRootPath
try {
    Write-Host "Configuring runner '$RunnerName' for $repoUrl with labels '$Labels'..."
    & .\config.cmd --unattended --url $repoUrl --token $token --name $RunnerName --labels $Labels --work _work --replace
    if ($LASTEXITCODE -ne 0) {
        throw "config.cmd failed with exit code $LASTEXITCODE"
    }

    Write-Host ""
    Write-Host "Runner configured. To run in the foreground:"
    Write-Host "  cd `"$runnerRootPath`""
    Write-Host "  .\run.cmd"
    Write-Host ""

    if ($Start) {
        Write-Host "Starting runner in foreground. Keep this terminal open while the workflow runs."
        & .\run.cmd
    }
} finally {
    Pop-Location
}
