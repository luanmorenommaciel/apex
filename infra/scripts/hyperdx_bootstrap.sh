#!/usr/bin/env bash
# Apex infra · hyperdx-bootstrap — register HyperDX's first user through its API.
#
# DEFAULT_CONNECTIONS / DEFAULT_SOURCES are applied by HyperDX only when the first team is
# created, i.e. at first user registration. Until then the stack has no Source and every
# search returns nothing. This replaces the "open :8090 and sign up" step with an
# idempotent call to the same endpoint the sign-up form uses:
#   GET  /installation           -> {"isTeamExisting": false|true}
#   POST /register/password      {email, password, confirmPassword}  (409 teamAlreadyExists)
# (hyperdxio/hyperdx packages/api/src/routers/api/root.ts, verified 2026-11-03)
#
# Usage:  make bootstrap   (or ./scripts/hyperdx_bootstrap.sh)
#   HYPERDX_ADMIN_EMAIL / HYPERDX_ADMIN_PASSWORD  from infra/.env (required; no default).
#   HyperDX's policy (2.43): 12+ characters with lower AND upper case and at least one of
#   !@#$%^&*(),.?":{}|<>;-+=  — a hex string is refused with HTTP 400.
#   HYPERDX_API_URL                               default http://127.0.0.1:${HYPERDX_API_HOST_PORT:-8000}
set -euo pipefail
cd "$(dirname "$0")/.."
ENV_FILE="${INFRA_ENV_FILE:-.env}"
set -a; [ -f "$ENV_FILE" ] && . "$ENV_FILE"; set +a

fail() { echo "❌ hyperdx-bootstrap: $1"; exit 1; }

EMAIL="${HYPERDX_ADMIN_EMAIL:-}"
PASSWORD="${HYPERDX_ADMIN_PASSWORD:-}"
[ -n "$EMAIL" ]    || fail "HYPERDX_ADMIN_EMAIL is required (set it in infra/.env)"
[ -n "$PASSWORD" ] || fail "HYPERDX_ADMIN_PASSWORD is required (set it in infra/.env; 12+ chars, upper+lower case, a special character)"
API="${HYPERDX_API_URL:-http://127.0.0.1:${HYPERDX_API_HOST_PORT:-8000}}"

installation=$(curl -sf -m 10 "$API/installation") || fail "HyperDX API at $API is not answering"
team=$(printf '%s' "$installation" | python3 -c 'import json,sys; print(str(json.load(sys.stdin).get("isTeamExisting")).lower())' 2>/dev/null || echo unparsable)
case "$team" in
  true)  echo "✅ hyperdx-bootstrap: a team already exists at $API — nothing to register"; exit 0 ;;
  false) ;;
  *)     fail "unexpected /installation response: $installation" ;;
esac

body=$(python3 -c 'import json,sys; print(json.dumps({"email": sys.argv[1], "password": sys.argv[2], "confirmPassword": sys.argv[2]}))' "$EMAIL" "$PASSWORD")
status=$(curl -s -m 30 -o /tmp/hyperdx_bootstrap.$$ -w '%{http_code}' -X POST -H 'Content-Type: application/json' \
  --data "$body" "$API/register/password") || fail "POST $API/register/password failed"
response=$(cat /tmp/hyperdx_bootstrap.$$); rm -f /tmp/hyperdx_bootstrap.$$
case "$status" in
  200|201) echo "✅ hyperdx-bootstrap: registered $EMAIL as the first user (connection + Spark Events source seeded)" ;;
  409)     echo "✅ hyperdx-bootstrap: team already exists (409) — nothing to register" ;;
  *)       fail "registration returned HTTP $status: $response" ;;
esac
