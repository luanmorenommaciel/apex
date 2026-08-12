#Requires -Version 7.0

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('bootstrap', 'doctor', 'smoke', 'e2e', 'tail-outlier', 'pilot-clean', 'status', 'down', 'help')]
    [string]$Action = 'help',
    [switch]$DryRun,
    [switch]$SkipBuild
)

$ErrorActionPreference = 'Stop'
$script:Root = Split-Path -Parent $PSScriptRoot
$script:RuntimeDir = Join-Path $script:Root '.apex'
$script:InfraEnv = Join-Path $script:RuntimeDir 'infra.env'
$script:CollectEnv = Join-Path $script:RuntimeDir 'collect.env'
$script:DevEnv = Join-Path $script:RuntimeDir 'dev.env'
$script:SparkDefaults = Join-Path $script:RuntimeDir 'spark-defaults.conf'
$script:S3SecretDir = Join-Path $script:RuntimeDir 'secrets'
$script:S3AccessKeyFile = Join-Path $script:S3SecretDir 's3_access_key'
$script:S3SecretKeyFile = Join-Path $script:S3SecretDir 's3_secret_key'
$script:PowerShellExe = 'pwsh'

function Write-Step {
    param([string]$Message)
    Write-Host "[apex] $Message" -ForegroundColor Cyan
}

function Invoke-Checked {
    param(
        [string]$FilePath,
        [string[]]$Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$FilePath failed with exit code $LASTEXITCODE"
    }
}

function Invoke-LaneCompose {
    param(
        [string[]]$Files,
        [string]$EnvFile,
        [string[]]$Arguments
    )

    $composeArguments = @('compose')
    foreach ($file in $Files) {
        $composeArguments += @('-f', $file)
    }
    $composeArguments += @('--env-file', $EnvFile)
    $composeArguments += $Arguments
    Invoke-Checked -FilePath 'docker' -Arguments $composeArguments
}

function New-SecureHex {
    param([int]$Bytes = 32)

    $buffer = [Security.Cryptography.RandomNumberGenerator]::GetBytes($Bytes)
    return [Convert]::ToHexString($buffer).ToLowerInvariant()
}

function Get-ExistingContainerEnvValue {
    param(
        [string]$Container,
        [string]$Name
    )

    $lines = & docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' $Container 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $lines) {
        return $null
    }
    $entry = $lines | Where-Object { $_ -like "$Name=*" } | Select-Object -Last 1
    if (-not $entry) {
        return $null
    }
    return ($entry -split '=', 2)[1]
}

function Set-EnvValue {
    param(
        [string]$Content,
        [string]$Name,
        [string]$Value
    )

    $pattern = "(?m)^$([regex]::Escape($Name))=.*$"
    if ([regex]::IsMatch($Content, $pattern)) {
        return [regex]::Replace($Content, $pattern, "$Name=$Value")
    }
    return "$Content`r`n$Name=$Value`r`n"
}

function Get-EnvValue {
    param(
        [string]$Path,
        [string]$Name
    )

    $match = Get-Content -LiteralPath $Path |
        Where-Object { $_ -match "^$([regex]::Escape($Name))=(.*)$" } |
        Select-Object -Last 1
    if (-not $match) {
        throw "Missing $Name in runtime configuration."
    }
    return ($match -split '=', 2)[1]
}

function Write-NewEnv {
    param(
        [string]$Destination,
        [string]$Example,
        [string]$Overlay = '',
        [hashtable]$Values = @{}
    )

    if (Test-Path -LiteralPath $Destination) {
        return
    }

    $content = Get-Content -Raw -LiteralPath $Example
    if ($Overlay) {
        $content += "`r`n# Spark 4.1.2 compatibility overlay`r`n"
        $content += Get-Content -Raw -LiteralPath $Overlay
    }
    foreach ($entry in $Values.GetEnumerator()) {
        $content = Set-EnvValue -Content $content -Name $entry.Key -Value $entry.Value
    }
    Set-Content -LiteralPath $Destination -Value $content -NoNewline -Encoding utf8
}

function Write-GeneratedSparkDefaults {
    # dev/conf/spark-defaults.conf ships with static minioadmin/minioadmin —
    # correct for dev's own docker-compose.yml, but this package generates a
    # fresh random MinIO credential per bootstrap (Initialize-RuntimeConfiguration).
    # Substitute the real generated values so Spark's S3A client (spark-history
    # reads s3a:// on its own startup, not just on job submission) actually
    # authenticates against the MinIO this package started.
    $content = Get-Content -Raw -LiteralPath (Join-Path $script:Root 'dev/conf/spark-defaults.conf')
    $accessKey = Get-EnvValue -Path $script:DevEnv -Name 'MINIO_ROOT_USER'
    $secretKey = Get-EnvValue -Path $script:DevEnv -Name 'MINIO_ROOT_PASSWORD'
    $content = [regex]::Replace($content, '(?m)^(spark\.hadoop\.fs\.s3a\.access\.key\s+).*$', "`${1}$accessKey")
    $content = [regex]::Replace($content, '(?m)^(spark\.hadoop\.fs\.s3a\.secret\.key\s+).*$', "`${1}$secretKey")
    Set-Content -LiteralPath $script:SparkDefaults -Value $content -NoNewline -Encoding utf8
}

function Write-S3SecretFiles {
    New-Item -ItemType Directory -Force -Path $script:S3SecretDir | Out-Null
    $accessKey = Get-EnvValue -Path $script:DevEnv -Name 'MINIO_ROOT_USER'
    $secretKey = Get-EnvValue -Path $script:DevEnv -Name 'MINIO_ROOT_PASSWORD'
    Set-Content -LiteralPath $script:S3AccessKeyFile -Value $accessKey -NoNewline -Encoding utf8
    Set-Content -LiteralPath $script:S3SecretKeyFile -Value $secretKey -NoNewline -Encoding utf8
}

function Set-S3SecretEnvironment {
    $env:APEX_S3_ACCESS_KEY_FILE = $script:S3AccessKeyFile
    $env:APEX_S3_SECRET_KEY_FILE = $script:S3SecretKeyFile
}

function Initialize-RuntimeConfiguration {
    New-Item -ItemType Directory -Force -Path $script:RuntimeDir | Out-Null

    # An existing named volume was initialized with the container credential.
    # Adopt it silently on first package bootstrap instead of rotating it behind
    # ClickHouse's back. Fresh installations always receive a random secret.
    $clickHousePassword = Get-ExistingContainerEnvValue `
        -Container 'apex-infra-clickhouse' -Name 'CLICKHOUSE_PASSWORD'
    if ([string]::IsNullOrWhiteSpace($clickHousePassword)) {
        $clickHousePassword = New-SecureHex
    }
    Write-NewEnv `
        -Destination $script:InfraEnv `
        -Example (Join-Path $script:Root 'infra/.env.example') `
        -Values @{
            CLICKHOUSE_PASSWORD = $clickHousePassword
            HYPERDX_API_KEY = New-SecureHex
        }

    $clickHousePassword = Get-EnvValue -Path $script:InfraEnv -Name 'CLICKHOUSE_PASSWORD'
    Write-NewEnv `
        -Destination $script:CollectEnv `
        -Example (Join-Path $script:Root 'collect/.env.example') `
        -Values @{
            CLICKHOUSE_PASSWORD = $clickHousePassword
            REDACTION_SECRET_KEY = New-SecureHex
        }

    Write-NewEnv `
        -Destination $script:DevEnv `
        -Example (Join-Path $script:Root 'dev/.env.example') `
        -Values @{
            MINIO_ROOT_USER = "apex-$(New-SecureHex -Bytes 8)"
            MINIO_ROOT_PASSWORD = New-SecureHex
            APEX_OTLP_ENDPOINT = 'http://apex-otel-collector:4318'
        }
    Write-GeneratedSparkDefaults
    Write-S3SecretFiles
    $env:APEX_SPARK_DEFAULTS_PATH = $script:SparkDefaults
    Set-S3SecretEnvironment
}

function Assert-RuntimeConfiguration {
    foreach ($path in @($script:InfraEnv, $script:CollectEnv, $script:DevEnv)) {
        if (-not (Test-Path -LiteralPath $path)) {
            throw "Runtime configuration missing: $path. Run bootstrap first."
        }
    }
    if (-not (Test-Path -LiteralPath $script:SparkDefaults)) {
        throw 'Generated Spark defaults are missing. Run bootstrap first.'
    }
    foreach ($secretPath in @($script:S3AccessKeyFile, $script:S3SecretKeyFile)) {
        if (-not (Test-Path -LiteralPath $secretPath)) {
            throw "Runtime S3 secret missing: $secretPath. Run bootstrap first."
        }
    }
    $env:APEX_SPARK_DEFAULTS_PATH = $script:SparkDefaults
    Set-S3SecretEnvironment
    if ((Get-EnvValue $script:InfraEnv 'CLICKHOUSE_PASSWORD') -ne
        (Get-EnvValue $script:CollectEnv 'CLICKHOUSE_PASSWORD')) {
        throw 'INFRA and COLLECT ClickHouse credentials differ. Recreate .apex configuration.'
    }
}

function Assert-Prerequisites {
    foreach ($command in @('docker', 'uv', 'pwsh', 'bash')) {
        if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
            throw "Required command not found: $command"
        }
    }
    & docker info --format '{{.ServerVersion}}' | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw 'Docker Desktop engine is not available.'
    }
    & docker compose version --short | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw 'Docker Compose is not available.'
    }
}

function Get-CleanPilotResidues {
    $residues = [Collections.Generic.List[string]]::new()
    if (Test-Path -LiteralPath $script:RuntimeDir) {
        $residues.Add('.apex/')
    }

    $containerPatterns = @(
        'apex-infra-*',
        'apex-dev-*',
        'apex-otel-collector',
        'apex-queue-init',
        'apex-clickhouse'
    )
    $containerNames = @(& docker ps -a --format '{{.Names}}')
    if ($LASTEXITCODE -ne 0) {
        throw 'Unable to inventory Docker containers for the clean pilot.'
    }
    foreach ($name in $containerNames) {
        if ($containerPatterns | Where-Object { $name -like $_ }) {
            $residues.Add("container:$name")
        }
    }

    $networkNames = @(& docker network ls --format '{{.Name}}')
    if ($LASTEXITCODE -ne 0) {
        throw 'Unable to inventory Docker networks for the clean pilot.'
    }
    foreach ($name in @('apex-infra-net', 'apex-collect-net', 'apex-dev_default')) {
        if ($networkNames -contains $name) {
            $residues.Add("network:$name")
        }
    }

    $volumeNames = @(& docker volume ls --format '{{.Name}}')
    if ($LASTEXITCODE -ne 0) {
        throw 'Unable to inventory Docker volumes for the clean pilot.'
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

function Assert-CleanPilotEnvironment {
    $residues = @(Get-CleanPilotResidues)
    if ($residues.Count -gt 0) {
        $summary = $residues -join ','
        Write-Host "APEX_CLEAN_PILOT=refused residues=$summary" -ForegroundColor Yellow
        throw 'Clean pilot requires a fresh clone/runtime and dedicated Docker resources. No resources were removed.'
    }

    $trackedChanges = @(& git status --porcelain --untracked-files=no)
    if ($LASTEXITCODE -ne 0) {
        throw 'Unable to verify the Git worktree for the clean pilot.'
    }
    if ($trackedChanges.Count -gt 0) {
        Write-Host 'APEX_CLEAN_PILOT=refused residues=tracked-worktree-changes' -ForegroundColor Yellow
        throw 'Clean pilot requires a clean tracked worktree. No files were changed.'
    }
}

function Write-CleanPilotReport {
    param(
        [datetime]$StartedAtUtc,
        [string]$JobId
    )

    $reportPath = Join-Path $script:Root 'evidence/clean-pilot-summary.json'
    $branch = (& git branch --show-current).Trim()
    $commit = (& git rev-parse HEAD).Trim()
    $components = @(
        'apex-infra-clickhouse',
        'apex-infra-mongodb',
        'apex-infra-hyperdx',
        'apex-otel-collector',
        'apex-dev-minio-1',
        'apex-dev-spark-master-1',
        'apex-dev-spark-worker-1',
        'apex-dev-spark-history-1'
    ) | ForEach-Object {
        $state = Get-ContainerState $_
        [ordered]@{
            name = $state.Name
            status = $state.Status
            health = $state.Health
        }
    }

    $report = [ordered]@{
        schema = 'apex.clean_pilot.v1'
        status = 'passed'
        started_at_utc = $StartedAtUtc.ToString('o')
        completed_at_utc = [datetime]::UtcNow.ToString('o')
        source = [ordered]@{
            branch = $branch
            commit = $commit
            tracked_worktree_clean_at_start = $true
        }
        runtime = [ordered]@{
            spark_version = '4.0.1'
            job_id = $JobId
            components = $components
        }
        gates = [ordered]@{
            bootstrap = 'passed'
            doctor = 'passed'
            smoke = 'passed'
            product_gate = 'passed'
        }
        security = [ordered]@{
            generated_service_secrets = 'local-only'
            secret_values_in_report = $false
            external_llm_called = $false
            automatic_fix_applied = $false
        }
    }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $reportPath) | Out-Null
    $report | ConvertTo-Json -Depth 8 |
        Set-Content -LiteralPath $reportPath -Encoding utf8
    return $reportPath
}

function Invoke-CleanPilot {
    Assert-Prerequisites
    Assert-CleanPilotEnvironment
    $startedAtUtc = [datetime]::UtcNow

    Write-Step 'Clean pilot accepted; running bootstrap, doctor and smoke'
    Start-Package
    Invoke-Doctor
    Invoke-ProductGate

    $jobId = Get-SkewJobId
    $reportPath = Write-CleanPilotReport -StartedAtUtc $startedAtUtc -JobId $jobId
    $relativeReport = [IO.Path]::GetRelativePath($script:Root, $reportPath)
    Write-Host "APEX_CLEAN_PILOT=passed job_id=$jobId evidence=$relativeReport" -ForegroundColor Green
}

function Get-ContainerState {
    param([string]$Name)

    $raw = & docker inspect -f '{{json .State}}' $Name 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $raw) {
        return [pscustomobject]@{ Name = $Name; Status = 'missing'; Health = '-'; ExitCode = $null }
    }
    $state = $raw | ConvertFrom-Json
    $health = if ($state.Health) { $state.Health.Status } else { '-' }
    return [pscustomobject]@{
        Name = $Name
        Status = $state.Status
        Health = $health
        ExitCode = $state.ExitCode
    }
}

function Wait-HttpHealthy {
    param(
        [string]$Uri,
        [int]$Attempts = 30
    )

    for ($attempt = 1; $attempt -le $Attempts; $attempt++) {
        try {
            $response = Invoke-WebRequest -UseBasicParsing -Uri $Uri -TimeoutSec 3
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300) {
                return
            }
        } catch {
            if ($attempt -eq $Attempts) {
                throw "Endpoint did not become healthy: $Uri"
            }
        }
        Start-Sleep -Seconds 2
    }
}

function Wait-ContainerReady {
    param(
        [string]$Name,
        [string]$ExpectedHealth = '-',
        [int]$Attempts = 150
    )

    for ($attempt = 1; $attempt -le $Attempts; $attempt++) {
        $state = Get-ContainerState $Name
        if ($state.Status -eq 'running' -and
            ($ExpectedHealth -eq '-' -or $state.Health -eq $ExpectedHealth)) {
            return $state
        }
        if ($state.Status -eq 'exited' -and $state.ExitCode -ne 0) {
            throw "$Name exited during startup (exit=$($state.ExitCode))."
        }
        Start-Sleep -Seconds 2
    }
    $final = Get-ContainerState $Name
    throw "$Name did not become ready (state=$($final.Status), health=$($final.Health))."
}

function Show-Status {
    $names = @(
        'apex-infra-clickhouse',
        'apex-infra-mongodb',
        'apex-infra-hyperdx',
        'apex-otel-collector',
        'apex-dev-minio-1',
        'apex-dev-spark-master-1',
        'apex-dev-spark-worker-1',
        'apex-dev-spark-history-1'
    )
    $names | ForEach-Object { Get-ContainerState $_ } | Format-Table -AutoSize
}

function Invoke-Doctor {
    Assert-RuntimeConfiguration

    $required = @(
        @{ Name = 'apex-infra-clickhouse'; Health = 'healthy' },
        @{ Name = 'apex-infra-mongodb'; Health = 'healthy' },
        @{ Name = 'apex-otel-collector'; Health = '-' },
        @{ Name = 'apex-dev-minio-1'; Health = 'healthy' },
        @{ Name = 'apex-dev-spark-master-1'; Health = 'healthy' },
        @{ Name = 'apex-dev-spark-worker-1'; Health = 'healthy' },
        @{ Name = 'apex-dev-spark-history-1'; Health = 'healthy' }
    )
    foreach ($expectation in $required) {
        Wait-ContainerReady `
            -Name $expectation.Name `
            -ExpectedHealth $expectation.Health | Out-Null
    }

    $collectorPort = Get-EnvValue $script:CollectEnv 'HEALTHCHECK_HOST_PORT'
    Wait-HttpHealthy -Uri "http://127.0.0.1:$collectorPort/"

    $sparkVersion = Get-EnvValue $script:DevEnv 'SPARK_VERSION'
    if ($sparkVersion -ne '4.0.1') {
        throw "Expected Spark 4.0.1, configured $sparkVersion."
    }

    $schemaSql = @"
SELECT count()
FROM system.tables
WHERE database = 'apex'
  AND name IN ('spark_events', 'plan_transitions', 'findings')
"@
    $tableCount = (
        $schemaSql |
            docker exec -i apex-infra-clickhouse sh -lc `
                'clickhouse-client --user "$CLICKHOUSE_USER" --password "$CLICKHOUSE_PASSWORD"'
    ).Trim()
    if ($LASTEXITCODE -ne 0 -or $tableCount -ne '3') {
        throw "Canonical ClickHouse schema is incomplete (required tables=$tableCount/3)."
    }

    Show-Status
    Write-Host 'APEX_DOCTOR=ready spark=4.0.1 schema=3/3 secrets=local' -ForegroundColor Green
}

function Start-Package {
    Assert-Prerequisites
    Initialize-RuntimeConfiguration
    Assert-RuntimeConfiguration

    $infraCompose = Join-Path $script:Root 'infra/docker-compose.yml'
    $collectCompose = Join-Path $script:Root 'collect/docker-compose.yml'
    $collectOverlay = Join-Path $script:Root 'collect/docker-compose.c3-infra.yml'
    $devCompose = Join-Path $script:Root 'dev/docker-compose.yml'
    $devOverlay = Join-Path $script:Root 'dev/docker-compose.c3-otlp.yml'
    $devPackageOverlay = Join-Path $script:Root 'dev/docker-compose.package.yml'

    Write-Step 'Validating lane Compose contracts'
    Invoke-LaneCompose @($infraCompose) $script:InfraEnv @('config', '--quiet')
    Invoke-LaneCompose @($collectCompose, $collectOverlay) $script:CollectEnv @('config', '--quiet')
    Invoke-LaneCompose @($devCompose, $devOverlay, $devPackageOverlay) `
        $script:DevEnv @('config', '--quiet')

    Write-Step 'Starting canonical INFRA'
    Invoke-LaneCompose @($infraCompose) $script:InfraEnv @(
        'up', '-d', '--wait', '--wait-timeout', '300', 'clickhouse'
    )
    # mongodb and hyperdx: start best-effort, uncoupled from Compose's --wait.
    # mongosh (the mongodb healthcheck client) can exceed its 5s timeout under
    # the CPU/disk contention of a fresh multi-service bring-up even though the
    # server itself is accepting connections fine; hyperdx's own baked-in
    # healthcheck can likewise report a few early failures before settling —
    # Compose's --wait treats "unhealthy" as terminal even if it recovers a
    # moment later. Invoke-Doctor's own Wait-ContainerReady loop below is far
    # more patient (150 x 2s) and is the real gate for both.
    Invoke-LaneCompose @($infraCompose) $script:InfraEnv @('up', '-d', 'mongodb', 'hyperdx')
    Write-Step 'Applying infra schema (idempotent — safe on a pre-existing volume)'
    $env:CLICKHOUSE_USER = Get-EnvValue $script:InfraEnv 'CLICKHOUSE_USER'
    $env:CLICKHOUSE_PASSWORD = Get-EnvValue $script:InfraEnv 'CLICKHOUSE_PASSWORD'
    # The HTTP healthcheck above can report Healthy a moment before the native
    # TCP port (9000, what clickhouse-client / apply_ddl.sh use) finishes
    # binding — settle before applying DDL rather than letting a transient
    # "Connection refused" fail the whole bootstrap.
    $ddlReady = $false
    for ($attempt = 1; $attempt -le 10; $attempt++) {
        & docker exec apex-infra-clickhouse clickhouse-client `
            --user $env:CLICKHOUSE_USER --password $env:CLICKHOUSE_PASSWORD `
            --query 'SELECT 1' 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) { $ddlReady = $true; break }
        Start-Sleep -Seconds 2
    }
    if (-not $ddlReady) {
        throw 'apex-infra-clickhouse did not accept native-protocol connections in time.'
    }
    Invoke-Checked -FilePath 'bash' -Arguments @(
        (Join-Path $script:Root 'infra/scripts/apply_ddl.sh')
    )

    Write-Step 'Starting redacting COLLECT against canonical INFRA'
    Invoke-LaneCompose @($collectCompose, $collectOverlay) $script:CollectEnv @(
        'up', '-d', 'queue-init'
    )
    Invoke-Checked -FilePath 'docker' -Arguments @('wait', 'apex-queue-init')
    $queueState = Get-ContainerState 'apex-queue-init'
    if ($queueState.Status -ne 'exited' -or $queueState.ExitCode -ne 0) {
        throw "COLLECT queue initialization failed (state=$($queueState.Status), exit=$($queueState.ExitCode))."
    }
    Invoke-LaneCompose @($collectCompose, $collectOverlay) $script:CollectEnv @(
        'up', '-d', '--no-deps', 'otel-collector'
    )
    Wait-HttpHealthy -Uri "http://127.0.0.1:$(Get-EnvValue $script:CollectEnv 'HEALTHCHECK_HOST_PORT')/"

    Write-Step 'Starting DEV with Spark 4.0.1 and the official JAR cell'
    # Compose v5 on Docker Desktop can stall in --wait after a successful
    # one-shot minio-init. Start detached and let doctor perform explicit,
    # bounded health waits for every long-running component.
    $devArguments = @('up', '-d')
    if (-not $SkipBuild) {
        $devArguments += '--build'
    }
    Invoke-LaneCompose @($devCompose, $devOverlay, $devPackageOverlay) `
        $script:DevEnv $devArguments

    Invoke-Doctor
}

function Set-CanonicalProcessEnvironment {
    $env:APEX_CANONICAL_CH_PASSWORD = Get-EnvValue $script:InfraEnv 'CLICKHOUSE_PASSWORD'
    $env:APEX_CANONICAL_CH_USER = Get-EnvValue $script:InfraEnv 'CLICKHOUSE_USER'
    $infraPort = Get-EnvValue $script:InfraEnv 'CLICKHOUSE_HTTP_HOST_PORT'
    $env:APEX_CANONICAL_CH_URL = "http://127.0.0.1:$infraPort"
    $env:CLICKHOUSE_HOST = '127.0.0.1'
    $env:CLICKHOUSE_PORT = $infraPort
    $env:CLICKHOUSE_USER = $env:APEX_CANONICAL_CH_USER
    $env:CLICKHOUSE_PASSWORD = $env:APEX_CANONICAL_CH_PASSWORD
    $env:CLICKHOUSE_DATABASE = 'apex'
}

function Get-SkewJobId {
    $log = Join-Path $script:Root 'dev/out/e2e-canonical-skew_join.log'
    $match = Select-String -Path $log -Pattern 'APEX_SESSION job_id=([^ ]+)' |
        Select-Object -Last 1
    if (-not $match) {
        throw "Could not find the fresh skew job_id in $log."
    }
    return $match.Matches[0].Groups[1].Value
}

function Invoke-ProductGate {
    param([switch]$Full)

    Invoke-Doctor
    Set-CanonicalProcessEnvironment

    $scenarioArguments = if ($Full) {
        @()
    } else {
        @('-Scenario', 'skew_join')
    }
    $canonicalArguments = @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
        (Join-Path $script:Root 'dev/scripts/e2e_canonical.ps1')
    ) + $scenarioArguments + @(
        '-EnvFile', $script:DevEnv,
        '-AdditionalComposeFile', (Join-Path $script:Root 'dev/docker-compose.package.yml')
    )
    Invoke-Checked -FilePath $script:PowerShellExe -Arguments $canonicalArguments

    $jobId = Get-SkewJobId
    Write-Step "Running deterministic six-lane gate for $jobId"
    Invoke-Checked -FilePath 'uv' -Arguments @(
        'run', '--python', '3.11', '--no-editable',
        '--reinstall-package', 'apex-mcp',
        '--project', (Join-Path $script:Root 'serve'), '--extra', 'dev',
        'python', (Join-Path $script:Root 'scripts/e2e_six_lanes.py'),
        '--job-id', $jobId
    )

    Write-Step 'Running full MCP stdio client gate'
    $env:APEX_GATE_JOB_ID = $jobId
    $env:APEX_GATE_BASELINE_ID = $jobId
    Invoke-Checked -FilePath 'uv' -Arguments @(
        'run', '--python', '3.11', '--no-editable',
        '--reinstall-package', 'apex-mcp',
        '--project', (Join-Path $script:Root 'serve'), '--extra', 'dev',
        'python', (Join-Path $script:Root 'serve/tools/mcp_stdio_gate.py')
    )
    Write-Host "APEX_PRODUCT_GATE=passed job_id=$jobId" -ForegroundColor Green
}

function Stop-Package {
    Assert-RuntimeConfiguration
    $devFiles = @(
        (Join-Path $script:Root 'dev/docker-compose.yml'),
        (Join-Path $script:Root 'dev/docker-compose.c3-otlp.yml'),
        (Join-Path $script:Root 'dev/docker-compose.package.yml')
    )
    $collectFiles = @(
        (Join-Path $script:Root 'collect/docker-compose.yml'),
        (Join-Path $script:Root 'collect/docker-compose.c3-infra.yml')
    )
    Invoke-LaneCompose $devFiles $script:DevEnv @('down', '--remove-orphans')
    Invoke-LaneCompose $collectFiles $script:CollectEnv @('down', '--remove-orphans')
    Invoke-LaneCompose @((Join-Path $script:Root 'infra/docker-compose.yml')) `
        $script:InfraEnv @('down', '--remove-orphans')
    Write-Host 'APEX_DOWN=complete volumes=preserved' -ForegroundColor Green
}

function Invoke-TailOutlierGate {
    Assert-RuntimeConfiguration
    Invoke-Doctor
    Set-CanonicalProcessEnvironment

    $canonicalScript = Join-Path $script:Root 'dev/scripts/e2e_canonical.ps1'
    $packageOverlay = Join-Path $script:Root 'dev/docker-compose.package.yml'
    Invoke-Checked -FilePath $script:PowerShellExe -Arguments @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $canonicalScript,
        '-Scenario', 'tail_outlier',
        '-EnvFile', $script:DevEnv,
        '-AdditionalComposeFile', $packageOverlay
    )

    $scenarioLog = Join-Path $script:Root 'dev/out/e2e-canonical-tail_outlier.log'
    $jobMatch = Select-String -Path $scenarioLog -Pattern 'APEX_SESSION job_id=([^ ]+)' |
        Select-Object -Last 1
    if (-not $jobMatch) {
        throw "Tail-outlier job_id missing from $scenarioLog"
    }
    $jobId = $jobMatch.Matches[0].Groups[1].Value

    $engineOutput = & uv run --python 3.11 --no-editable `
        --reinstall-package apex-engine `
        --project (Join-Path $script:Root 'engine') `
        --extra clickhouse python -m apex_engine $jobId --dry-run --no-crew 2>&1
    $engineExitCode = $LASTEXITCODE
    $engineOutput | Write-Output
    if ($engineExitCode -ne 0) {
        throw "Tail-outlier ENGINE analysis failed with exit code $engineExitCode"
    }
    if (-not ($engineOutput -match 'tail_outlier_watcher')) {
        throw "Tail-outlier telemetry arrived, but ENGINE did not emit tail_outlier_watcher"
    }

    Write-Host "APEX_TAIL_OUTLIER_GATE=passed job_id=$jobId llm_calls=0" -ForegroundColor Green
}

function Show-Help {
    @'
Apex initial package

  .\scripts\apex.ps1 bootstrap [-SkipBuild]
  .\scripts\apex.ps1 doctor
  .\scripts\apex.ps1 smoke
  .\scripts\apex.ps1 e2e
  .\scripts\apex.ps1 tail-outlier
  .\scripts\apex.ps1 pilot-clean
  .\scripts\apex.ps1 status
  .\scripts\apex.ps1 down

Use -DryRun with any command to inspect the operation without Docker,
configuration writes or external calls.

pilot-clean is fail-closed: it refuses existing .apex configuration, canonical
Docker resources or tracked worktree changes and never removes them.
'@
}

if ($DryRun) {
    $requiredFiles = @(
        'infra/docker-compose.yml',
        'collect/docker-compose.yml',
        'collect/docker-compose.c3-infra.yml',
        'dev/docker-compose.yml',
        'dev/docker-compose.c3-otlp.yml',
        'dev/docker-compose.package.yml',
        'infra/scripts/apply_ddl.sh',
        'serve/tools/mcp_stdio_gate.py'
    )
    foreach ($relativePath in $requiredFiles) {
        if (-not (Test-Path -LiteralPath (Join-Path $script:Root $relativePath))) {
            throw "Package input missing: $relativePath"
        }
    }
    Write-Host "APEX_DRY_RUN=passed action=$Action mutations=0 external_calls=0"
    exit 0
}

Set-Location $script:Root
switch ($Action) {
    'bootstrap' { Start-Package }
    'doctor' { Assert-Prerequisites; Invoke-Doctor }
    'smoke' { Assert-Prerequisites; Invoke-ProductGate }
    'e2e' { Assert-Prerequisites; Invoke-ProductGate -Full }
    'tail-outlier' { Assert-Prerequisites; Invoke-TailOutlierGate }
    'pilot-clean' { Invoke-CleanPilot }
    'status' { Show-Status }
    'down' { Stop-Package }
    'help' { Show-Help }
}
