#!/bin/sh
# Apex Console — deployment configuration, written at CONTAINER START.
#
# Run by the nginx image's own entrypoint (/docker-entrypoint.d/*.sh) before
# nginx starts. Two jobs:
#
#   1. Fail loudly when the deployment has NO store to serve from, and only
#      then. nginx substitutes CLICKHOUSE_UPSTREAM into proxy_pass and would
#      otherwise die with "invalid URL prefix in /etc/nginx/conf.d/default.conf",
#      which names neither the variable nor the deployment step that forgot it.
#      What counts as "forgot" depends on the data source:
#
#        clickhouse  ClickHouse is the only path        -> CLICKHOUSE_UPSTREAM required
#        http        the API is the only path           -> ClickHouse never used;
#                                                          no CLICKHOUSE_UPSTREAM needed
#        fixtures    the recording is the only path     -> neither needed
#        auto        probes the API first, then         -> at least ONE of an API
#        (default)   ClickHouse, then fixtures             or CLICKHOUSE_UPSTREAM
#
#      In `auto` ClickHouse is a FALLBACK, so a deployment that configures the
#      API alone must boot — otherwise the documented same-origin setup could
#      not start without an upstream it will never call. `auto` with neither
#      configured has nothing to probe and is refused rather than silently
#      serving the recording.
#   2. Render /config.js from this container's environment, so the bundle is not
#      pinned to the database, user, credential and mode it was BUILT with.
#      Vite inlines every VITE_* reference, so this is the only way one image can
#      serve more than one deployment. See src/data/runtimeConfig.ts.
#
# A variable that is UNSET emits no key, leaving the bundle's own default in
# place. A variable set to "" emits an empty string, which is a real value:
# apex_ro is created IDENTIFIED WITH no_password.
set -eu

# The Dockerfile defaults CLICKHOUSE_UPSTREAM and APEX_API_UPSTREAM to this
# address, because nginx renders its template BEFORE this script runs and
# needs SOME value to boot. It refuses connections immediately, so a path
# nobody configured fails fast instead of hanging. Both variables therefore
# read "not configured" when empty OR equal to it. Keep in step with Dockerfile.
UNROUTABLE="http://127.0.0.1:1"

configured() { [ -n "$1" ] && [ "$1" != "$UNROUTABLE" ]; }

# An unrecognised DATA_SOURCE behaves as `auto` in the bundle
# (runtimeConfig.ts asDataSource), so it is judged as `auto` here too.
mode="${DATA_SOURCE:-auto}"
case "$mode" in
  auto|clickhouse|fixtures|http) ;;
  *) mode=auto ;;
esac

have_clickhouse=0
if configured "${CLICKHOUSE_UPSTREAM:-}"; then have_clickhouse=1; fi
# The API is configured by either handle: an explicit upstream for nginx to
# forward /v1 to (same-origin, the supported arrangement), or an absolute URL
# the browser calls directly.
have_api=0
if configured "${APEX_API_UPSTREAM:-}" || [ -n "${APEX_API_URL:-}" ]; then have_api=1; fi

missing_clickhouse() {
  echo "apex-console: CLICKHOUSE_UPSTREAM is not set." >&2
  echo "  $1" >&2
  echo "  Pass the store's endpoint, for example:" >&2
  echo "    docker run -e CLICKHOUSE_UPSTREAM=http://clickhouse.internal:8123 ..." >&2
  echo "  It is an endpoint only, never a credential." >&2
  exit 1
}

case "$mode" in
  clickhouse)
    [ "$have_clickhouse" = 1 ] || missing_clickhouse \
      "DATA_SOURCE=clickhouse queries the store through nginx's /clickhouse proxy, which has no target."
    ;;
  auto)
    if [ "$have_clickhouse" = 0 ] && [ "$have_api" = 0 ]; then
      missing_clickhouse \
        "DATA_SOURCE=auto needs a store to probe: set CLICKHOUSE_UPSTREAM, or configure the API (APEX_API_UPSTREAM for same-origin, or APEX_API_URL). Use DATA_SOURCE=fixtures to serve the recording deliberately."
    fi
    if [ "$have_clickhouse" = 0 ]; then
      echo "apex-console: DATA_SOURCE=auto with no CLICKHOUSE_UPSTREAM — the API is the only store." >&2
      echo "  If it does not answer, the console shows the recorded run, not the database." >&2
    fi
    ;;
  http)
    if [ "$have_api" = 0 ]; then
      echo "apex-console: DATA_SOURCE=http but neither APEX_API_UPSTREAM nor APEX_API_URL is set." >&2
      echo "  Every /v1 request will fail until one is." >&2
    fi
    ;;
esac

# APEX_CONFIG_OUT exists so the script can be exercised without an nginx image.
out="${APEX_CONFIG_OUT:-/usr/share/nginx/html/config.js}"
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
  # Only for DATA_SOURCE=http. Leave APEX_API_URL unset to call /v1 relative,
  # which nginx forwards to APEX_API_UPSTREAM and keeps the browser on one
  # origin — the same arrangement /clickhouse already uses.
  if [ "${APEX_API_URL+set}" = set ]; then
    printf '  apiUrl: "%s",\n' "$(esc "$APEX_API_URL")"
  fi
  if [ "${APEX_API_TOKEN+set}" = set ]; then
    printf '  apiToken: "%s",\n' "$(esc "$APEX_API_TOKEN")"
  fi
  echo "};"
} > "$tmp"
mv "$tmp" "$out"
