[CmdletBinding()]
param(
    [ValidateSet('skew_join', 'spill', 'bad_shuffle', 'driver_oom')]
    [string[]]$Scenario = @('skew_join', 'spill', 'bad_shuffle', 'driver_oom'),
    [switch]$StartDev,
    [switch]$SkipGenerate
)

# Native Windows entry point for the canonical Spark -> OTLP -> ClickHouse gate.
# Credentials remain operator/CI environment variables; this script never reads,
# writes, or prints them.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Test-Path '.env')) {
    throw 'Missing dev/.env. Run: make env-spark41'
}
if ([string]::IsNullOrWhiteSpace($env:APEX_CANONICAL_CH_PASSWORD)) {
    throw 'APEX_CANONICAL_CH_PASSWORD is required for canonical ClickHouse assertions.'
}

$compose = @('compose', '-f', 'docker-compose.yml', '-f', 'docker-compose.c3-otlp.yml', '--env-file', '.env')
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
        'spark-master', '/opt/spark/bin/spark-submit', '--master', 'spark://spark-master:7077',
        '--conf', 'spark.plugins=apex.ApexPlugin',
        '--conf', 'spark.apex.otlp.endpoint=http://apex-otel-collector:4318',
        '--conf', 'spark.driver.host=spark-master', '--conf', 'spark.driver.bindAddress=0.0.0.0'
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

    python scripts/canonical_e2e_assert.py --job-id $JobId --scenario $Name
    if ($LASTEXITCODE -ne 0) {
        throw "Canonical ClickHouse assertion failed for $Name ($JobId)."
    }
}

if ((docker network inspect apex-collect-net 2>$null).Count -eq 0) {
    throw 'apex-collect-net is missing. Start COLLECT and INFRA first.'
}
if ((docker inspect -f '{{.State.Running}}' apex-otel-collector 2>$null) -ne 'true') {
    throw 'apex-otel-collector is not running. Start COLLECT and INFRA first.'
}

if ($StartDev) {
    Invoke-Compose @('up', '-d', '--build', '--wait', '--wait-timeout', '600')
}

if (-not $SkipGenerate) {
    $generateLog = Join-Path $outDir 'e2e-canonical-generate-data.log'
    & docker @compose exec -T spark-master /opt/spark/bin/spark-submit --master spark://spark-master:7077 `
        --conf spark.plugins=apex.ApexPlugin `
        --conf spark.apex.otlp.endpoint=http://apex-otel-collector:4318 `
        --conf spark.driver.host=spark-master `
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
        $jobs = @{ skew_join = 'skew_join.py'; spill = 'spill.py'; bad_shuffle = 'bad_shuffle.py' }
        $result = Invoke-SparkJob -Name $name -Job $jobs[$name] -Aqe 'off'
        if ($result.ExitCode -ne 0) {
            throw "$name Spark job failed (see $($result.Log))."
        }
    }
    Assert-Canonical -Name $name -JobId (Get-JobId -Log $result.Log)
}

Write-Host 'OK E2E CANONICAL PASSED - requested pathologies reached ClickHouse' -ForegroundColor Green
