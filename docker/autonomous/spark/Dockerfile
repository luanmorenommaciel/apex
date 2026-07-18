ARG SPARK_BASE_IMAGE=spark-plat-v0-spark:4.1.2
FROM ${SPARK_BASE_IMAGE}

USER root

RUN mkdir -p /opt/apex/listener

COPY docker/autonomous/spark/spark-defaults.conf /opt/spark/conf/spark-defaults.conf

USER spark
