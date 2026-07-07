#!/usr/bin/env bash
set -euo pipefail

exec /opt/spark/bin/spark-class org.apache.spark.deploy.history.HistoryServer
