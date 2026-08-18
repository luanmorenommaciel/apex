[CmdletBinding()]
param(
    [string]$EnvFile = '.env',
    [string]$LogFile = 'out/e2e-canonical-generate-data-background.log'
)

# Starts the deterministic data generator outside the interactive terminal.
# Configuration is read by Docker Compose; this launcher never prints it.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Test-Path $EnvFile)) {
    throw "Missing dev environment file: $EnvFile"
}

$logPath = Join-Path $root $LogFile
$errorPath = "$logPath.stderr"
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $logPath) | Out-Null
Remove-Item $errorPath -ErrorAction SilentlyContinue

$composeArgs = @(
    'compose', '-f', 'docker-compose.yml', '-f', 'docker-compose.c3-otlp.yml', '--env-file', $EnvFile,
    'exec', '-T', '-e', 'APEX_AQE=off', '-e', 'APEX_FIX=off', '-e', 'APEX_SAFE=off',
    'spark-master', '/bin/sh', '/opt/apex/scripts/with-s3-credentials.sh',
    '/opt/spark/bin/spark-submit', '--master', 'spark://spark-master:7077',
    '--conf', 'spark.plugins=apex.ApexPlugin',
    '--conf', 'spark.apex.otlp.endpoint=http://apex-otel-collector:4318',
    '--conf', 'spark.driver.host=spark-master', '--conf', 'spark.driver.bindAddress=0.0.0.0',
    '/opt/apex/jobs/generate_data.py'
)

$process = Start-Process -FilePath 'docker' -ArgumentList $composeArgs -PassThru -WindowStyle Hidden `
    -RedirectStandardOutput $logPath -RedirectStandardError $errorPath

@{
    pid = $process.Id
    log = $logPath
    stderr = $errorPath
    status = 'started'
} | ConvertTo-Json -Compress

# The caller can poll Get-Process -Id <pid>; completion is proved by the
# generator's PASS marker in the log, not guessed from a running process.
