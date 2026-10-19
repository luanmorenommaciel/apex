[CmdletBinding()]
param(
    [ValidateSet('skew_join', 'tail_outlier', 'spill', 'bad_shuffle', 'driver_oom')]
    [string[]]$Scenario = @('skew_join', 'spill', 'bad_shuffle', 'driver_oom'),
    [switch]$StartDev,
    [switch]$ReuseDev,
    [switch]$SkipGenerate,
    [switch]$Build,
    [string]$DriverHost = 'spark-master',
    [string]$EnvFile = '.env',
    [string[]]$AdditionalComposeFile = @()
)

# Native Windows entry point for the canonical Spark -> OTLP -> ClickHouse gate.
# Credentials remain operator/CI environment variables; this script never reads,
# writes, or prints them.
#
# Parity with e2e_canonical.sh (same knobs, same defaults):
#   -StartDev / -ReuseDev   <-> compose up vs E2E_CANONICAL_REUSE_DEV=1
#   -SkipGenerate           <-> E2E_CANONICAL_SKIP_GENERATE=1
#   -Build                  <-> E2E_CANONICAL_BUILD=1 (image is never rebuilt implicitly)
#   -DriverHost             <-> APEX_CANONICAL_DRIVER_HOST
#   -AdditionalComposeFile  <-> E2E_CANONICAL_COMPOSE_FILES
#   -EnvFile                <-> dev/.env (the r9d control arm uses the same parameter)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Test-Path $EnvFile)) {
    throw "Missing dev environment file: $EnvFile. Run: make env-spark41"
}
if ($StartDev -and $ReuseDev) {
    throw '-StartDev and -ReuseDev are mutually exclusive.'
}
if ([string]::IsNullOrWhiteSpace($env:APEX_CANONICAL_CH_PASSWORD)) {
    throw 'APEX_CANONICAL_CH_PASSWORD is required for canonical ClickHouse assertions.'
}

function Get-PythonApplication {
    # `python` is the usual Windows launcher; macOS/Linux normally expose only
    # `python3`. Resolve a real executable (never an alias or function) and
    # require Python 3 so a Python 2 or Store stub cannot be picked up.
    $onWindows = [Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT
    $names = if ($onWindows) { @('python', 'python3') } else { @('python3', 'python') }
    foreach ($name in $names) {
        $application = Get-Command $name -CommandType Application -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if (-not $application) {
            continue
        }
        & $application.Source -c 'import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)' 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            return $application.Source
        }
    }
    throw 'Python 3 is required on PATH (python on Windows, python3 on macOS/Linux) for canonical ClickHouse assertions.'
}

# Resolve Python before any Docker or Spark work so a missing interpreter fails
# fast instead of after the Spark job has already run.
$pythonExe = Get-PythonApplication

$compose = @('compose', '-f', 'docker-compose.yml', '-f', 'docker-compose.c3-otlp.yml')
foreach ($composeFile in $AdditionalComposeFile) {
    $compose += @('-f', $composeFile)
}
$compose += @('--env-file', $EnvFile)
$outDir = Join-Path $root 'out'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

function Invoke-Compose {
    param([string[]]$Arguments)

    & docker @compose @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "docker compose failed with exit code $LASTEXITCODE"
    }
}

function Invoke-SparkJob {
    param(
        [string]$Name,
        [string]$Job,
        [string]$Aqe,
        [string]$DriverMemory = ''
    )

    $log = Join-Path $outDir "e2e-canonical-$Name.log"
    $submit = @(
        'exec', '-T', '-e', "APEX_AQE=$Aqe", '-e', 'APEX_FIX=off', '-e', 'APEX_SAFE=off',
        'spark-master', '/bin/sh', '/opt/apex/scripts/with-s3-credentials.sh',
        '/opt/spark/bin/spark-submit', '--master', 'spark://spark-master:7077',
        '--conf', 'spark.plugins=apex.ApexPlugin',
        '--conf', 'spark.apex.otlp.endpoint=http://apex-otel-collector:4318',
        '--conf', "spark.driver.host=$DriverHost", '--conf', 'spark.driver.bindAddress=0.0.0.0'
    )
    if ($DriverMemory) {
        $submit += @('--driver-memory', $DriverMemory)
    }
    $submit += "/opt/apex/jobs/$Job"

    & docker @compose @submit 2>&1 | Tee-Object -FilePath $log
    return @{ ExitCode = $LASTEXITCODE; Log = $log }
}

function Get-JobId {
    param([string]$Log)

    $match = Select-String -Path $Log -Pattern 'APEX_SESSION job_id=([^ ]+)' | Select-Object -Last 1
    if (-not $match) {
        throw "The Spark job did not emit APEX_SESSION job_id (see $Log)."
    }
    return $match.Matches[0].Groups[1].Value
}

function Assert-Canonical {
    param([string]$Name, [string]$JobId)

    & $pythonExe scripts/canonical_e2e_assert.py --job-id $JobId --scenario $Name
    if ($LASTEXITCODE -ne 0) {
        throw "Canonical ClickHouse assertion failed for $Name ($JobId)."
    }
}

if ((docker network inspect apex-collect-net 2>$null).Count -eq 0) {
    throw 'apex-collect-net is missing. Start COLLECT and INFRA first.'
}
function Test-CollectorAvailable {
    # Parity with e2e_canonical.sh: collect's own apex-otel-collector container,
    # or infra's collector aliased onto apex-collect-net (tests/e2e/run.sh step 2).
    if ((docker inspect -f '{{.State.Running}}' apex-otel-collector 2>$null) -eq 'true') { return $true }
    $members = docker network inspect apex-collect-net -f '{{range .Containers}}{{.Name}} {{end}}' 2>$null
    if ("$members" -match 'apex-infra-otel-collector') {
        return ((docker inspect -f '{{.State.Running}}' apex-infra-otel-collector 2>$null) -eq 'true')
    }
    return $false
}
if (-not (Test-CollectorAvailable)) {
    throw 'No collector reachable as apex-otel-collector on apex-collect-net. Start COLLECT, or alias the INFRA collector (tests/e2e/run.sh step 2).'
}

function Test-DevImagePresent {
    $rendered = & docker @compose @('config', '--format', 'json') 2>$null | Out-String
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($rendered)) { return $false }
    $image = (ConvertFrom-Json $rendered).services.'spark-master'.image
    if ([string]::IsNullOrWhiteSpace($image)) { return $false }
    & docker image inspect $image 2>$null | Out-Null
    return ($LASTEXITCODE -eq 0)
}

if ($ReuseDev) {
    Write-Host 'Reusing the already running dev cluster.'
} elseif ($StartDev) {
    # Mirror e2e_canonical.sh: the image is rebuilt only with -Build; a missing
    # image fails fast with the build hint instead of an implicit compose build.
    if ($Build) {
        Invoke-Compose @('build')
    } elseif (-not (Test-DevImagePresent)) {
        throw "dev image is missing - run 'make build' or pass -Build."
    }
    Invoke-Compose @('up', '-d', '--wait', '--wait-timeout', '600')
}

if (-not $SkipGenerate) {
    $generateLog = Join-Path $outDir 'e2e-canonical-generate-data.log'
    & docker @compose exec -T spark-master /bin/sh /opt/apex/scripts/with-s3-credentials.sh `
        /opt/spark/bin/spark-submit --master spark://spark-master:7077 `
        --conf spark.plugins=apex.ApexPlugin `
        --conf spark.apex.otlp.endpoint=http://apex-otel-collector:4318 `
        --conf "spark.driver.host=$DriverHost" `
        --conf spark.driver.bindAddress=0.0.0.0 `
        /opt/apex/jobs/generate_data.py 2>&1 | Tee-Object -FilePath $generateLog
    if ($LASTEXITCODE -ne 0 -or -not (Select-String -Quiet -Path $generateLog -Pattern 'hot_keys_~50pct=PASS')) {
        throw "Deterministic hot-key generation failed (see $generateLog)."
    }
}

foreach ($name in $Scenario) {
    if ($name -eq 'driver_oom') {
        $result = Invoke-SparkJob -Name $name -Job 'driver_oom.py' -Aqe 'off' -DriverMemory '512m'
        if ($result.ExitCode -eq 0) {
            throw "driver_oom unexpectedly completed (see $($result.Log))."
        }
    } else {
        $jobs = @{
            skew_join = 'skew_join.py'
            tail_outlier = 'tail_outlier.py'
            spill = 'spill.py'
            bad_shuffle = 'bad_shuffle.py'
        }
        $result = Invoke-SparkJob -Name $name -Job $jobs[$name] -Aqe 'off'
        if ($result.ExitCode -ne 0) {
            throw "$name Spark job failed (see $($result.Log))."
        }
    }
    Assert-Canonical -Name $name -JobId (Get-JobId -Log $result.Log)
}

Write-Host 'OK E2E CANONICAL PASSED - requested pathologies reached ClickHouse' -ForegroundColor Green
