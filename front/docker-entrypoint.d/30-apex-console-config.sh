#!/bin/sh
# Apex Console — deployment configuration, written at CONTAINER START.
#
# Run by the nginx image's own entrypoint (/docker-entrypoint.d/*.sh) before
# nginx starts. Two jobs:
#
#   1. Judge the data source. The console reads through the Apex API alone
#      (D-api-only, 2026-10-19), so there are two modes and nothing else:
#
#        http        the API is the only path  -> APEX_API_UPSTREAM (same-origin,
#        (default)                                the supported arrangement) or
#                                                 APEX_API_URL; warned if neither
#        fixtures    the recording is the only path -> no upstream needed
#
#      Anything else is REFUSED by name. The bundle reads an unknown value as
#      http because it cannot refuse; a typo here would otherwise boot a
#      container whose operator believes it is in a mode that does not exist.
#   2. Render /config.js from this container's environment, so the bundle is not
#      pinned to the API, token and mode it was BUILT with. Vite inlines every
#      VITE_* reference, so this is the only way one image can serve more than
#      one deployment. See src/data/runtimeConfig.ts.
#
# A variable that is UNSET emits no key, leaving the bundle's own default in
# place. /config.js carries dataSource, apiUrl and apiToken and nothing else:
# no database, no user, no password - the browser never holds one.
set -eu

# The Dockerfile defaults APEX_API_UPSTREAM to this address, because nginx
# renders its template BEFORE this script runs and needs SOME value to boot.
# It refuses connections immediately, so a path nobody configured fails fast
# instead of hanging. The variable therefore reads "not configured" when empty
# OR equal to it. Keep in step with Dockerfile.
UNROUTABLE="http://127.0.0.1:1"

configured() { [ -n "$1" ] && [ "$1" != "$UNROUTABLE" ]; }

mode="${DATA_SOURCE:-http}"
case "$mode" in
  http|fixtures) ;;
  *)
    echo "apex-console: DATA_SOURCE='$mode' is not a data source." >&2
    echo "  The console reads through the Apex API alone. Set DATA_SOURCE=http (the default)," >&2
    echo "  or DATA_SOURCE=fixtures to serve the recorded run with no store." >&2
    exit 1
    ;;
esac

# The API is configured by either handle: an explicit upstream for nginx to
# forward /v1 to (same-origin, the supported arrangement), or an absolute URL
# the browser calls directly.
have_api=0
if configured "${APEX_API_UPSTREAM:-}" || [ -n "${APEX_API_URL:-}" ]; then have_api=1; fi

if [ "$mode" = http ] && [ "$have_api" = 0 ]; then
  echo "apex-console: DATA_SOURCE=http but neither APEX_API_UPSTREAM nor APEX_API_URL is set." >&2
  echo "  The console will render 'no store answered' until one is. For example:" >&2
  echo "    docker run -e APEX_API_UPSTREAM=http://apex-api.internal:8099 -e APEX_API_TOKEN=<token> ..." >&2
fi

# APEX_CONFIG_OUT exists so the script can be exercised without an nginx image.
out="${APEX_CONFIG_OUT:-/usr/share/nginx/html/config.js}"
tmp="$out.tmp"

# JSON string escaping: the backslash first, then the double quote, so an
# already-escaped backslash is not doubled twice.
esc() { printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'; }

{
  echo "// Generated at container start by 30-apex-console-config.sh — do not edit."
  echo "window.__APEX_CONFIG__ = {"
  if [ "${DATA_SOURCE+set}" = set ]; then
    printf '  dataSource: "%s",\n' "$(esc "$DATA_SOURCE")"
  fi
  # Leave APEX_API_URL unset to call /v1 relative, which nginx forwards to
  # APEX_API_UPSTREAM and keeps the browser on one origin.
  if [ "${APEX_API_URL+set}" = set ]; then
    printf '  apiUrl: "%s",\n' "$(esc "$APEX_API_URL")"
  fi
  if [ "${APEX_API_TOKEN+set}" = set ]; then
    printf '  apiToken: "%s",\n' "$(esc "$APEX_API_TOKEN")"
  fi
  echo "};"
} > "$tmp"
mv "$tmp" "$out"
