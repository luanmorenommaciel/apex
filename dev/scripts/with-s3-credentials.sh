#!/usr/bin/env sh
set -eu

access_file="${APEX_S3_ACCESS_KEY_FILE:-/run/secrets/apex_s3_access_key}"
secret_file="${APEX_S3_SECRET_KEY_FILE:-/run/secrets/apex_s3_secret_key}"

if [ ! -r "$access_file" ] || [ ! -r "$secret_file" ]; then
  echo "APEX S3 credential files are missing or unreadable." >&2
  exit 78
fi

AWS_ACCESS_KEY_ID="$(cat "$access_file")"
AWS_SECRET_ACCESS_KEY="$(cat "$secret_file")"

if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
  echo "APEX S3 credential files must not be empty." >&2
  exit 78
fi

export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY

exec "$@"

