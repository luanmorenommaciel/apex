# TODO(hardening): digest-pin SPARK_BASE_IMAGE (FROM apache/spark@sha256:...)
# once a Docker daemon/registry is available to resolve the current digest.
ARG SPARK_BASE_IMAGE=apache/spark:4.1.2-scala2.13-java17-python3-ubuntu
FROM ${SPARK_BASE_IMAGE}

USER root
RUN mkdir -p /opt/spark/apps /opt/spark/metrics \
    && chown -R spark:spark /opt/spark/apps /opt/spark/metrics \
    && chmod -R 775 /opt/spark/apps /opt/spark/metrics
COPY context/jars/*.jar /opt/spark/jars/
COPY context/python-wheels /tmp/python-wheels
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-index --find-links=/tmp/python-wheels -r /tmp/requirements.txt \
    && rm -rf /tmp/python-wheels /tmp/requirements.txt
COPY context/conf/spark-defaults.conf /opt/spark/conf/spark-defaults.conf
COPY context/conf/log4j2.properties /opt/spark/conf/log4j2.properties
USER spark
