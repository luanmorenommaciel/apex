#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example"
else
  added_header=false
  while IFS= read -r line; do
    [[ -z "$line" || "$line" =~ ^# ]] && continue
    key="${line%%=*}"
    if ! grep -Eq "^${key}=" .env; then
      if [[ "$added_header" == "false" ]]; then
        printf '\n# Added by make bootstrap after .env.example changed.\n' >> .env
        added_header=true
      fi
      printf '%s\n' "$line" >> .env
      echo "Added missing .env key: $key"
    fi
  done < .env.example
fi

set -a
source .env.example
source .env
set +a

JARS_DIR="$ROOT_DIR/build/config/spark/jars"
MANIFEST="$JARS_DIR/.bootstrap-manifest"
REQ_FILE="$ROOT_DIR/build/images/spark/requirements.txt"
WHEELS_DIR="$ROOT_DIR/build/cache/python-wheels"
WHEELS_MANIFEST="$WHEELS_DIR/.requirements.sha256"
mkdir -p "$JARS_DIR" "$WHEELS_DIR" build/var/minio-data build/var/clickhouse-data build/var/clickhouse-logs build/var/metrics build/cache

required_tools=(docker sha256sum)
for tool in "${required_tools[@]}"; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Missing required tool: $tool" >&2
    exit 1
  fi
done

ensure_uv() {
  if command -v uv >/dev/null 2>&1; then
    echo "uv found: $(command -v uv)"
    return 0
  fi

  if ! command -v curl >/dev/null 2>&1; then
    echo "Missing required tool: curl is needed to install uv" >&2
    exit 1
  fi

  echo "uv was not found. Installing uv with the official Astral installer..."
  export UV_INSTALL_DIR="${UV_INSTALL_DIR:-$HOME/.local/bin}"
  mkdir -p "$UV_INSTALL_DIR"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$UV_INSTALL_DIR:$PATH"

  if ! command -v uv >/dev/null 2>&1; then
    echo "uv installation finished, but uv is still not available on PATH" >&2
    echo "Expected install directory: $UV_INSTALL_DIR" >&2
    exit 1
  fi

  echo "uv installed: $(command -v uv)"
}

ensure_uv

echo "Syncing project Python dependencies with uv..."
uv sync

echo "Pulling required base images..."
docker pull "$SPARK_BASE_IMAGE"
docker pull "$GO_BASE_IMAGE"
docker pull "$MINIO_BASE_IMAGE"
docker pull "$MINIO_MC_BASE_IMAGE"
docker pull "$CLICKHOUSE_BASE_IMAGE"

manifest_complete=false
if [[ -f "$MANIFEST" ]]; then
  manifest_complete=true
  while IFS= read -r jar_name; do
    [[ -z "$jar_name" ]] && continue
    if [[ ! -f "$JARS_DIR/$jar_name" ]]; then
      manifest_complete=false
      break
    fi
  done < "$MANIFEST"
fi

if [[ "$manifest_complete" == "true" ]]; then
  echo "Spark jars are already bootstrapped in build/config/spark/jars"
else
  echo "Resolving Spark, Delta, and S3A jars into build/config/spark/jars..."
  docker run --rm \
    -u root \
    -e HOST_UID="$(id -u)" \
    -e HOST_GID="$(id -g)" \
    -v "$JARS_DIR:/resolved-jars" \
    "$SPARK_BASE_IMAGE" \
    bash -lc '
      set -euo pipefail
      rm -rf /root/.ivy2.5.2
      cat > /tmp/resolve_packages.py <<PYSPARK
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[1]").appName("resolve-packages").getOrCreate()
spark.stop()
PYSPARK
      /opt/spark/bin/spark-submit \
        --master local[1] \
        --conf spark.ui.enabled=false \
        --packages "io.delta:delta-spark_4.1_2.13:4.2.0,org.apache.hadoop:hadoop-aws:3.4.2" \
        /tmp/resolve_packages.py
      cp /root/.ivy2.5.2/jars/*.jar /resolved-jars/
      find /resolved-jars -maxdepth 1 -type f -name "*.jar" -printf "%f\n" | sort > /resolved-jars/.bootstrap-manifest
      chown -R "$HOST_UID:$HOST_GID" /resolved-jars
    '
fi

for required_jar in \
  io.delta_delta-spark_4.1_2.13-4.2.0.jar \
  io.delta_delta-storage-4.2.0.jar \
  org.apache.hadoop_hadoop-aws-3.4.2.jar \
  software.amazon.awssdk_bundle-2.29.52.jar; do
  if [[ ! -f "$JARS_DIR/$required_jar" ]]; then
    echo "Missing expected jar after bootstrap: $required_jar" >&2
    exit 1
  fi
done

requirements_hash="$(sha256sum "$REQ_FILE" | awk '{print $1}')"
if [[ -f "$WHEELS_MANIFEST" && "$(cat "$WHEELS_MANIFEST")" == "$requirements_hash" ]] && find "$WHEELS_DIR" -maxdepth 1 -type f \( -name '*.whl' -o -name '*.tar.gz' \) | grep -q .; then
  echo "Python wheels are already bootstrapped in build/cache/python-wheels"
else
  echo "Downloading Python wheels for the Spark image..."
  rm -rf "$WHEELS_DIR"
  mkdir -p "$WHEELS_DIR"
  docker run --rm \
    -u root \
    -e HOST_UID="$(id -u)" \
    -e HOST_GID="$(id -g)" \
    -v "$REQ_FILE:/requirements.txt:ro" \
    -v "$WHEELS_DIR:/python-wheels" \
    "$SPARK_BASE_IMAGE" \
    bash -lc 'set -euo pipefail; python3 -m pip download --dest /python-wheels -r /requirements.txt; chown -R "$HOST_UID:$HOST_GID" /python-wheels'
  printf '%s\n' "$requirements_hash" > "$WHEELS_MANIFEST"
fi

if [[ -d build/images/eventlog-loader/vendor && -f build/images/eventlog-loader/go.sum ]]; then
  echo "Go dependencies are already vendored for the event log loader"
else
  echo "Vendoring Go dependencies for the event log loader..."
  docker run --rm \
    -u root \
    -e HOST_UID="$(id -u)" \
    -e HOST_GID="$(id -g)" \
    -v "$ROOT_DIR/build/images/eventlog-loader:/src" \
    -w /src \
    "$GO_BASE_IMAGE" \
    bash -lc 'set -euo pipefail; /usr/local/go/bin/go mod tidy; /usr/local/go/bin/go mod vendor; chown -R "$HOST_UID:$HOST_GID" /src'
fi

echo "Bootstrap completed"
