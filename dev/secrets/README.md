# dev/secrets/

Local-only Docker Compose file-based secrets, read by `with-s3-credentials.sh`
and mounted into every Spark container (master, worker, history) at
`/run/secrets/apex_s3_access_key` / `apex_s3_secret_key`.

They are the ONLY source of S3 credentials in the standalone lane:
`conf/spark-defaults.conf` carries no key literals and selects the S3A
`EnvironmentVariableCredentialsProvider`; the wrapper exports the two files as
`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` for each daemon and each
`spark-submit`, and executors inherit the worker's environment. Without these
files the Spark services refuse to start (wrapper exit 78) instead of silently
running with a default password.

The values must match the MinIO root user the compose file starts
(`MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` in `.env`, `minioadmin` by default).
Contents here are gitignored (see `dev/.gitignore`); only this README is tracked.

To (re)generate for the default local MinIO:
```
printf 'minioadmin' > dev/secrets/apex_s3_access_key
printf 'minioadmin' > dev/secrets/apex_s3_secret_key
```
