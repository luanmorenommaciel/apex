#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
JARS_DIR="$ROOT_DIR/build/config/spark/jars"
MANIFEST="$JARS_DIR/.bootstrap-manifest"
REQ_FILE="$ROOT_DIR/build/images/spark/requirements.txt"
WHEELS_DIR="$ROOT_DIR/build/cache/python-wheels"
WHEELS_MANIFEST="$WHEELS_DIR/.requirements.sha256"

if [[ ! -f "$ROOT_DIR/.env" ]]; then
  echo "Missing .env. Run: make bootstrap" >&2
  exit 1
fi

set -a
source "$ROOT_DIR/.env.example"
source "$ROOT_DIR/.env"
set +a

for image in "$SPARK_BASE_IMAGE" "$GO_BASE_IMAGE" "$MINIO_BASE_IMAGE" "$MINIO_MC_BASE_IMAGE" "$CLICKHOUSE_BASE_IMAGE"; do
  if ! docker image inspect "$image" >/dev/null 2>&1; then
    echo "Missing bootstrapped base image: $image" >&2
    echo "Run: make bootstrap" >&2
    exit 1
  fi
done

if [[ ! -f "$MANIFEST" ]]; then
  echo "Missing jar bootstrap manifest. Run: make bootstrap" >&2
  exit 1
fi

while IFS= read -r jar_name; do
  [[ -z "$jar_name" ]] && continue
  if [[ ! -f "$JARS_DIR/$jar_name" ]]; then
    echo "Missing bootstrapped jar: $jar_name" >&2
    exit 1
  fi
done < "$MANIFEST"

requirements_hash="$(sha256sum "$REQ_FILE" | awk '{print $1}')"
if [[ ! -f "$WHEELS_MANIFEST" || "$(cat "$WHEELS_MANIFEST")" != "$requirements_hash" ]]; then
  echo "Missing or stale Python wheel cache. Run: make bootstrap" >&2
  exit 1
fi

if ! find "$WHEELS_DIR" -maxdepth 1 -type f \( -name '*.whl' -o -name '*.tar.gz' \) | grep -q .; then
  echo "Python wheel cache is empty. Run: make bootstrap" >&2
  exit 1
fi

if [[ ! -d "$ROOT_DIR/build/images/eventlog-loader/vendor" || ! -f "$ROOT_DIR/build/images/eventlog-loader/go.sum" ]]; then
  echo "Missing vendored Go dependencies. Run: make bootstrap" >&2
  exit 1
fi
