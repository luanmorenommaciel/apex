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

$migration = Join-Path $root 'sql/021_findings_v02_additive.sql'
if (-not (Test-Path $migration)) {
    throw "Migration file not found: $migration"
}

if ((docker inspect -f '{{.State.Running}}' $ClickHouseContainer 2>$null) -ne 'true') {
    throw "ClickHouse container is not running: $ClickHouseContainer"
}

Get-Content -Raw $migration | docker exec -i $ClickHouseContainer sh -lc `
    'clickhouse-client --user "$CLICKHOUSE_USER" --password "$CLICKHOUSE_PASSWORD" --multiquery'
if ($LASTEXITCODE -ne 0) {
    throw "ClickHouse schema migration failed with exit code $LASTEXITCODE"
}

'DESCRIBE TABLE apex.findings' | docker exec -i $ClickHouseContainer sh -lc `
    'clickhouse-client --user "$CLICKHOUSE_USER" --password "$CLICKHOUSE_PASSWORD"'
if ($LASTEXITCODE -ne 0) {
    throw "Could not verify apex.findings after migration"
}
