# dev/secrets/

Local-only Docker Compose file-based secrets, read by `with-s3-credentials.sh`
and mounted into containers at `/run/secrets/apex_s3_access_key` /
`apex_s3_secret_key`.

Contents here are gitignored (see `dev/.gitignore`) and match the existing
MinIO dev credentials already baked into `dev/conf/spark-defaults.conf`
(`minioadmin`/`minioadmin`) — this is local-dev parity, not a new secret
value, just delivered through the mechanism `with-s3-credentials.sh` already
expects instead of only via the mounted conf file.

To regenerate:
```
printf 'minioadmin' > dev/secrets/apex_s3_access_key
printf 'minioadmin' > dev/secrets/apex_s3_secret_key
```
