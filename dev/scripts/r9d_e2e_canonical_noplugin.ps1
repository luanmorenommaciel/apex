[CmdletBinding()]
param(
    [ValidateSet('skew_join', 'tail_outlier', 'spill', 'bad_shuffle', 'driver_oom')]
    [string[]]$Scenario = @('skew_join', 'spill', 'bad_shuffle', 'driver_oom'),
    [switch]$StartDev,
    [switch]$SkipGenerate,
    [string]$EnvFile = '.env',
    [string[]]$AdditionalComposeFile = @()
)

# R9D control arm: identical workload to e2e_canonical.ps1 with the APEX JAR
# plugin NOT attached. The mounted dev/conf/spark-defaults.conf declares
# spark.plugins=apex.ApexPlugin, so this arm must explicitly override it with
# an empty spark.plugins= at submit time; the OTLP endpoint is never set here.
# Telemetry-dependent ClickHouse assertions are skipped by design: with the
# plugin off no telemetry can exist. APEX_SESSION is printed by the job harness
# itself (dev/common/session.py), independent of the plugin, so the functional
# gate of this arm is: scenario-specific expected exit codes plus the
# APEX_SESSION marker, both checked OUTSIDE the submit-to-exit clocked window.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Test-Path $EnvFile)) {
    throw "Missing dev environment file: $EnvFile. Run: make env-spark41"
}

$compose = @('compose', '-f', 'docker-compose.yml', '-f', 'docker-compose.c3-otlp.yml')
foreach ($composeFile in $AdditionalComposeFile) {
    $compose += @('-f', $composeFile)
}
$compose += @('--env-file', $EnvFile)
$outDir = Join-Path $root 'out'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$datasetId = if ($env:APEX_DATASET_ID) {
    $env:APEX_DATASET_ID
} else {
    "$(Get-Date -AsUTC -Format 'yyyyMMddTHHmmssZ')-$PID"
}
if ($datasetId -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$') {
    throw 'APEX_DATASET_ID must contain 1-128 letters, digits, dots, underscores or dashes.'
}
$factPath = "s3a://warehouse/apex-runs/$datasetId/fact"
$dimPath = "s3a://warehouse/apex-runs/$datasetId/dim"

function Invoke-SparkJobNoPlugin {
    param(
        [string]$Name,
        [string]$Job,
        [string]$Aqe,
        [string]$DriverMemory = ''
    )

    $log = Join-Path $outDir "r9d-e2e-noplugin-$Name.log"
    $submit = @(
        'exec', '-T', '-e', "APEX_AQE=$Aqe", '-e', 'APEX_FIX=off', '-e', 'APEX_SAFE=off',
        '-e', "APEX_FACT_PATH=$factPath", '-e', "APEX_DIM_PATH=$dimPath",
        'spark-master', '/bin/sh', '/opt/apex/scripts/with-s3-credentials.sh',
        '/opt/spark/bin/spark-submit', '--master', 'spark://spark-master:7077',
        '--conf', 'spark.plugins=',
        '--conf', 'spark.driver.host=spark-master', '--conf', 'spark.driver.bindAddress=0.0.0.0'
    )
    if ($DriverMemory) {
        $submit += @('--driver-memory', $DriverMemory)
    }
    $submit += "/opt/apex/jobs/$Job"

    # Keep this boundary identical to e2e_canonical.ps1. Any validation after
    # the process returns is intentionally outside submit-to-exit timing.
    $watch = [System.Diagnostics.Stopwatch]::StartNew()
    & docker @compose @submit 2>&1 | Tee-Object -FilePath $log
    $exitCode = $LASTEXITCODE
    $watch.Stop()
    $submitToExitMs = [int][Math]::Round($watch.Elapsed.TotalMilliseconds)
    Write-Host "APEX_SUBMIT_RESULT name=$Name exit=$exitCode submit_to_exit_ms=$submitToExitMs"
    return @{ ExitCode = $exitCode; Log = $log; SubmitToExitMs = $submitToExitMs }
}

function Assert-SessionMarker {
    param([string]$Name, [string]$Log)

    # Functional gate of the OFF arm; runs OUTSIDE the submit-to-exit window.
    $match = Select-String -Path $Log -Pattern 'APEX_SESSION job_id=([^ ]+)' | Select-Object -Last 1
    if (-not $match) {
        throw "The Spark job did not emit APEX_SESSION job_id (see $Log)."
    }
    Write-Host "APEX_SESSION_GATE name=$Name result=present"
}

function Assert-ExpectedDriverOom {
    param([string]$Log)

    # The control arm must prove the expected pathology, not merely accept an
    # arbitrary non-zero spark-submit result. These are deliberately specific
    # JVM/Spark OOM signatures; this check runs after the clock has stopped.
    $text = Get-Content -Raw -Path $Log
    $oomPattern = '(?is)(?:java\.lang\.)?OutOfMemoryError|Java heap space|SparkException.*?(?:Caused by:\s*)?(?:java\.lang\.)?OutOfMemoryError'
    if (-not [regex]::IsMatch($text, $oomPattern)) {
        throw "driver_oom failed without an expected OOM signature (see $Log)."
    }
    Write-Host 'APEX_EXPECTED_FAILURE name=driver_oom result=oom_signature_present'
}

if ((docker network inspect apex-collect-net 2>$null).Count -eq 0) {
    throw 'apex-collect-net is missing. Start COLLECT and INFRA first.'
}
if ((docker inspect -f '{{.State.Running}}' apex-otel-collector 2>$null) -ne 'true') {
    throw 'apex-otel-collector is not running. Start COLLECT and INFRA first.'
}

if ($StartDev) {
    & docker @compose @('up', '-d', '--build', '--wait', '--wait-timeout', '600')
    if ($LASTEXITCODE -ne 0) { throw "docker compose up failed with exit code $LASTEXITCODE" }
}

if (-not $SkipGenerate) {
    $generateLog = Join-Path $outDir 'r9d-e2e-noplugin-generate-data.log'
    $generateSubmit = @(
        'exec', '-T', '-e', 'APEX_AQE=off', '-e', 'APEX_FIX=off', '-e', 'APEX_SAFE=off',
        '-e', "APEX_FACT_PATH=$factPath", '-e', "APEX_DIM_PATH=$dimPath",
        'spark-master', '/bin/sh', '/opt/apex/scripts/with-s3-credentials.sh',
        '/opt/spark/bin/spark-submit', '--master', 'spark://spark-master:7077',
        '--conf', 'spark.plugins=',
        '--conf', 'spark.driver.host=spark-master', '--conf', 'spark.driver.bindAddress=0.0.0.0'
    )
    $generateSubmit += '/opt/apex/jobs/generate_data.py'
    $generateWatch = [System.Diagnostics.Stopwatch]::StartNew()
    & docker @compose @generateSubmit 2>&1 | Tee-Object -FilePath $generateLog
    $generateExitCode = $LASTEXITCODE
    $generateWatch.Stop()
    $generateSubmitToExitMs = [int][Math]::Round($generateWatch.Elapsed.TotalMilliseconds)
    Write-Host "APEX_SUBMIT_RESULT name=generate_data exit=$generateExitCode submit_to_exit_ms=$generateSubmitToExitMs"
    if ($generateExitCode -ne 0 -or -not (Select-String -Quiet -Path $generateLog -Pattern 'hot_key_~50pct=PASS')) {
        throw "Deterministic hot-key generation failed (see $generateLog)."
    }
}

foreach ($name in $Scenario) {
    if ($name -eq 'driver_oom') {
        $result = Invoke-SparkJobNoPlugin -Name $name -Job 'driver_oom.py' -Aqe 'off' -DriverMemory '512m'
        if ($result.ExitCode -eq 0) {
            throw "driver_oom unexpectedly completed (see $($result.Log))."
        }
        Assert-SessionMarker -Name $name -Log $result.Log
        Assert-ExpectedDriverOom -Log $result.Log
    } else {
        $jobs = @{
            skew_join = 'skew_join.py'
            tail_outlier = 'tail_outlier.py'
            spill = 'spill.py'
            bad_shuffle = 'bad_shuffle.py'
        }
        $result = Invoke-SparkJobNoPlugin -Name $name -Job $jobs[$name] -Aqe 'off'
        if ($result.ExitCode -ne 0) {
            throw "$name Spark job failed (see $($result.Log))."
        }
        Assert-SessionMarker -Name $name -Log $result.Log
    }
}

Write-Host 'OK R9D NO-PLUGIN ARM PASSED - workload completed without the APEX JAR' -ForegroundColor Green
