#!/usr/bin/env bash
# Railway Spark entrypoint: render spark-defaults.conf from env, then start one role.
# Usage: start.sh master|worker|history|conf   ("conf" only renders, used by e2e-runner before spark-submit)
# No endpoints or credentials are hardcoded; every value comes from Railway variables.
set -euo pipefail
role=${1:?usage: start.sh master|worker|history|conf}
: "${S3_ENDPOINT:?}" "${S3_ACCESS_KEY:?}" "${S3_SECRET_KEY:?}" "${APEX_OTLP_ENDPOINT:?}"
WAREHOUSE_BUCKET=${WAREHOUSE_BUCKET:-warehouse}; LOGS_BUCKET=${LOGS_BUCKET:-spark-logs}
S3_REGION=${S3_REGION:-us-east-1}
SPARK_HOME=${SPARK_HOME:-/opt/spark}
# Railway private networking is IPv6-first: advertise our private DNS name, bind on all v6 (and v4) addrs.
HOST=${RAILWAY_PRIVATE_DOMAIN:-$(hostname)}
export SPARK_LOCAL_HOSTNAME=$HOST SPARK_PUBLIC_DNS=$HOST
export SPARK_LOCAL_IP=${SPARK_LOCAL_IP:-::}
V6='-Djava.net.preferIPv6Addresses=true'
export SPARK_DAEMON_JAVA_OPTS="${SPARK_DAEMON_JAVA_OPTS:-} $V6"
export SPARK_HISTORY_OPTS="${SPARK_HISTORY_OPTS:-} $V6"
DRIVER_PORT=${SPARK_DRIVER_PORT:-7078}; BM_PORT=${SPARK_BLOCKMANAGER_PORT:-7079}

# Driver JVM: no preferIPv6Addresses. With it, the local PySpark data server binds ::1 while PySpark
# connects to 127.0.0.1 (CANNOT_OPEN_SOCKET on collect()). Master/worker/executors keep it.
conf=${SPARK_CONF_DIR:-$SPARK_HOME/conf}/spark-defaults.conf
mkdir -p "$(dirname "$conf")"; umask 077
cat > "$conf" <<CONF
spark.sql.extensions                        io.delta.sql.DeltaSparkSessionExtension
spark.sql.catalog.spark_catalog             org.apache.spark.sql.delta.catalog.DeltaCatalog
spark.hadoop.fs.s3a.impl                    org.apache.hadoop.fs.s3a.S3AFileSystem
spark.hadoop.fs.s3a.endpoint                ${S3_ENDPOINT}
spark.hadoop.fs.s3a.endpoint.region         ${S3_REGION}
spark.hadoop.fs.s3a.access.key              ${S3_ACCESS_KEY}
spark.hadoop.fs.s3a.secret.key              ${S3_SECRET_KEY}
spark.hadoop.fs.s3a.path.style.access       true
spark.hadoop.fs.s3a.connection.ssl.enabled  false
spark.hadoop.fs.s3a.aws.credentials.provider org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider
spark.eventLog.enabled                      true
spark.eventLog.dir                          s3a://${LOGS_BUCKET}/events/
spark.history.fs.logDirectory               s3a://${LOGS_BUCKET}/events/
spark.sql.warehouse.dir                     s3a://${WAREHOUSE_BUCKET}/
spark.driver.extraClassPath                 /opt/apex/lib/apex-devfp.jar:/opt/apex/lib/apex-plugin.jar
spark.executor.extraClassPath               /opt/apex/lib/apex-plugin.jar
spark.plugins                               apex.ApexPlugin
spark.apex.otlp.endpoint                    ${APEX_OTLP_ENDPOINT}
spark.apex.aqe.enabled                      true
spark.driver.host                           ${HOST}
spark.driver.bindAddress                    ::
spark.driver.port                           ${DRIVER_PORT}
spark.blockManager.port                     ${BM_PORT}
spark.driver.blockManager.port              ${BM_PORT}
spark.driver.extraJavaOptions               -Djava.net.preferIPv6Addresses=false
spark.executor.extraJavaOptions             ${V6}
CONF

cls() { exec "$SPARK_HOME/bin/spark-class" "$@"; }
case $role in
  master)  cls org.apache.spark.deploy.master.Master --host "$HOST" --port "${SPARK_MASTER_PORT:-7077}" --webui-port "${SPARK_MASTER_WEBUI_PORT:-8080}" ;;
  worker)  : "${SPARK_MASTER_URL:?}"
           cls org.apache.spark.deploy.worker.Worker "$SPARK_MASTER_URL" --host "$HOST" \
             --port "${SPARK_WORKER_PORT:-7080}" --webui-port "${SPARK_WORKER_WEBUI_PORT:-8081}" \
             --cores "${SPARK_WORKER_CORES:-2}" --memory "${SPARK_WORKER_MEMORY:-2g}" ;;
  history) cls org.apache.spark.deploy.history.HistoryServer ;;
  conf)    echo "rendered $conf" ;;
  *) echo "unknown role: $role" >&2; exit 2 ;;
esac
