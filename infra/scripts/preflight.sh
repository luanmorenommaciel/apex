#!/usr/bin/env bash
# Apex infra · preflight — refuse to start the stack with missing or default credentials.
#
# A copied .env.example carries EMPTY credentials on purpose; this is the step that turns
# "forgot to set the password" into a one-line error instead of a world-readable store.
# `make up` runs it before `docker compose up`.
#
# Usage:  ./scripts/preflight.sh            (reads infra/.env)
#         INFRA_ENV_FILE=/path/to/env ./scripts/preflight.sh
set -euo pipefail
cd "$(dirname "$0")/.."
ENV_FILE="${INFRA_ENV_FILE:-.env}"

fail() { echo "❌ preflight: $1"; exit 1; }

[ -f "$ENV_FILE" ] || fail "$ENV_FILE is missing — cp .env.example .env, then set CLICKHOUSE_PASSWORD and HYPERDX_API_KEY"
set -a; . "$ENV_FILE"; set +a

pw="${CLICKHOUSE_PASSWORD:-}"
[ -n "$pw" ] || fail "CLICKHOUSE_PASSWORD is empty — generate one: openssl rand -hex 24"
case "$pw" in
  apex_local_dev|change-me*|changeme*|password|secret)
    fail "CLICKHOUSE_PASSWORD is a default value — generate one: openssl rand -hex 24" ;;
esac
[ "${#pw}" -ge 16 ] || fail "CLICKHOUSE_PASSWORD is shorter than 16 characters — generate one: openssl rand -hex 24"

key="${HYPERDX_API_KEY:-}"
[[ "$key" =~ ^[0-9a-f]{64}$ ]] || fail "HYPERDX_API_KEY must be 64 hex characters (openssl rand -hex 32); got ${#key} characters"

echo "✅ preflight ok — CLICKHOUSE_PASSWORD and HYPERDX_API_KEY are set and not defaults"
