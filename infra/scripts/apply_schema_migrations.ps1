[CmdletBinding()]
param(
    [string]$ClickHouseContainer = 'apex-infra-clickhouse'
)

# Applies additive migrations to an existing local ClickHouse volume.
# The client runs inside the named ClickHouse container and reads its configured
# CLICKHOUSE_USER/PASSWORD there, so this script neither requests nor prints a secret.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$migrations = @(
    (Join-Path $root 'sql/021_findings_v02_additive.sql'),
    (Join-Path $root 'sql/022_stage_duration_max_additive.sql')
)
$missingMigrations = @($migrations | Where-Object { -not (Test-Path $_) })
if ($missingMigrations.Count -gt 0) {
    throw "Migration file not found: $($missingMigrations -join ', ')"
}

if ((docker inspect -f '{{.State.Running}}' $ClickHouseContainer 2>$null) -ne 'true') {
    throw "ClickHouse container is not running: $ClickHouseContainer"
}

foreach ($migration in $migrations) {
    Get-Content -Raw $migration | docker exec -i $ClickHouseContainer sh -lc `
        'clickhouse-client --user "$CLICKHOUSE_USER" --password "$CLICKHOUSE_PASSWORD" --multiquery'
    if ($LASTEXITCODE -ne 0) {
        throw "ClickHouse schema migration failed for $migration with exit code $LASTEXITCODE"
    }
}

$verificationSql = @"
SELECT
    (SELECT count()
     FROM system.columns
     WHERE database = 'apex'
       AND ((table = 'findings' AND name IN ('app_id', 'confidence_score'))
         OR (table = 'spark_events' AND name = 'task_duration_max_ms')))
  + (SELECT count()
     FROM system.tables
     WHERE database = 'apex'
       AND name = 'mv_spark_events'
       AND position(create_table_query, 'task_duration_max_ms') > 0)
"@
$verifiedArtifacts = (
    $verificationSql |
        docker exec -i $ClickHouseContainer sh -lc `
            'clickhouse-client --user "$CLICKHOUSE_USER" --password "$CLICKHOUSE_PASSWORD"'
).Trim()
if ($LASTEXITCODE -ne 0 -or $verifiedArtifacts -ne '4') {
    throw "Could not verify canonical migrations (artifacts=$verifiedArtifacts/4)"
}
