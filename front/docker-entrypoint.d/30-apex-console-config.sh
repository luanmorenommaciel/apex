#!/bin/sh
# Apex Console — deployment configuration, written at CONTAINER START.
#
# Run by the nginx image's own entrypoint (/docker-entrypoint.d/*.sh) before
# nginx starts. Two jobs:
#
#   1. Fail loudly when CLICKHOUSE_UPSTREAM is missing. nginx substitutes it into
#      proxy_pass and would otherwise die with "invalid URL prefix in
#      /etc/nginx/conf.d/default.conf", which names neither the variable nor the
#      deployment step that forgot it.
#   2. Render /config.js from this container's environment, so the bundle is not
#      pinned to the database, user, credential and mode it was BUILT with.
#      Vite inlines every VITE_* reference, so this is the only way one image can
#      serve more than one deployment. See src/data/runtimeConfig.ts.
#
# A variable that is UNSET emits no key, leaving the bundle's own default in
# place. A variable set to "" emits an empty string, which is a real value:
# apex_ro is created IDENTIFIED WITH no_password.
set -eu

: "${CLICKHOUSE_UPSTREAM:=}"
if [ -z "$CLICKHOUSE_UPSTREAM" ]; then
  echo "apex-console: CLICKHOUSE_UPSTREAM is not set." >&2
  echo "  nginx.conf substitutes it into proxy_pass; without it the server" >&2
  echo "  refuses to start. Pass the store's endpoint, for example:" >&2
  echo "    docker run -e CLICKHOUSE_UPSTREAM=http://clickhouse.internal:8123 ..." >&2
  echo "  It is an endpoint only, never a credential." >&2
  exit 1
fi

out=/usr/share/nginx/html/config.js
tmp="$out.tmp"

# JSON string escaping: the backslash first, then the double quote, so an
# already-escaped backslash is not doubled twice.
esc() { printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'; }

{
  echo "// Generated at container start by 30-apex-console-config.sh — do not edit."
  echo "window.__APEX_CONFIG__ = {"
  if [ "${CLICKHOUSE_DB+set}" = set ]; then
    printf '  database: "%s",\n' "$(esc "$CLICKHOUSE_DB")"
  fi
  if [ "${CLICKHOUSE_USER+set}" = set ]; then
    printf '  user: "%s",\n' "$(esc "$CLICKHOUSE_USER")"
  fi
  if [ "${CLICKHOUSE_PASSWORD+set}" = set ]; then
    printf '  password: "%s",\n' "$(esc "$CLICKHOUSE_PASSWORD")"
  fi
  if [ "${DATA_SOURCE+set}" = set ]; then
    printf '  dataSource: "%s",\n' "$(esc "$DATA_SOURCE")"
  fi
  echo "};"
} > "$tmp"
mv "$tmp" "$out"
