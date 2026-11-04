# Railway wrapper: one-shot e2e runner = spark wrapper image (driver side) + uv + engine/serve/scripts.
# Generated from spark/Dockerfile; keep the two in step.
ARG SBT_IMAGE=sbtscala/scala-sbt:eclipse-temurin-jammy-17.0.10_7_1.10.4_3.5.2
ARG SPARK_IMAGE=apache/spark:4.0.1-scala2.13-java17-python3-ubuntu
ARG APEX_JAR_TARGET=apex_40
FROM ${SBT_IMAGE} AS apex-plugin-build
WORKDIR /workspace
ENV COURSIER_REPOSITORIES=https://repo.maven.apache.org/maven2
COPY jar/build.sbt ./
COPY jar/project ./project
COPY jar/src ./src
ARG APEX_JAR_TARGET
RUN set -eux; sbt -batch "${APEX_JAR_TARGET}/assembly"; \
    artifact="$(find target -type f -name 'apex_*-*-assembly.jar' | head -n 1)"; test -n "$artifact"; \
    install -D "$artifact" /out/apex-plugin.jar

FROM ${SPARK_IMAGE}
ARG HADOOP_AWS_VERSION=3.4.1
ARG AWS_SDK_BUNDLE_VERSION=2.24.6
ARG DELTA_VERSION=4.0.0
ARG DELTA_ARTIFACT=delta-spark_2.13
ENV SPARK_HOME=/opt/spark
USER root
RUN set -eux; apt-get update; apt-get install -y --no-install-recommends curl ca-certificates; rm -rf /var/lib/apt/lists/*
RUN set -eux; cd "${SPARK_HOME}/jars"; M="https://repo.maven.apache.org/maven2"; \
    curl -fSL -o "hadoop-aws-${HADOOP_AWS_VERSION}.jar" "${M}/org/apache/hadoop/hadoop-aws/${HADOOP_AWS_VERSION}/hadoop-aws-${HADOOP_AWS_VERSION}.jar"; \
    curl -fSL -o "aws-sdk-bundle-${AWS_SDK_BUNDLE_VERSION}.jar" "${M}/software/amazon/awssdk/bundle/${AWS_SDK_BUNDLE_VERSION}/bundle-${AWS_SDK_BUNDLE_VERSION}.jar"; \
    curl -fSL -o "${DELTA_ARTIFACT}-${DELTA_VERSION}.jar" "${M}/io/delta/${DELTA_ARTIFACT}/${DELTA_VERSION}/${DELTA_ARTIFACT}-${DELTA_VERSION}.jar"; \
    curl -fSL -o "delta-storage-${DELTA_VERSION}.jar" "${M}/io/delta/delta-storage/${DELTA_VERSION}/delta-storage-${DELTA_VERSION}.jar"
RUN python3 -m pip install --no-cache-dir requests==2.32.3
COPY --from=apex-plugin-build /out/apex-plugin.jar /opt/apex/lib/apex-plugin.jar
COPY dev/jvm/PlanFingerprint.java /tmp/apexdev/apexdev/PlanFingerprint.java
RUN set -eux; mkdir -p /opt/apex/lib; javac -cp "${SPARK_HOME}/jars/*" -d /tmp/apexdev/out /tmp/apexdev/apexdev/PlanFingerprint.java; \
    (cd /tmp/apexdev/out && jar cf /opt/apex/lib/apex-devfp.jar apexdev); rm -rf /tmp/apexdev
# Was bind-mounted by dev/docker-compose.yml.
COPY dev/jobs /opt/apex/jobs
COPY dev/common /opt/apex/common
COPY dev/scripts /opt/apex/scripts
COPY deploy/railway/spark/start.sh /opt/apex/railway/start.sh
RUN chmod +x /opt/apex/railway/start.sh && mkdir -p /opt/spark/conf && chown -R spark /opt/spark/conf
ENV PYTHONPATH=/opt/apex
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /usr/local/bin/uv
COPY engine /opt/apex/src/engine
COPY serve /opt/apex/src/serve
COPY scripts /opt/apex/src/scripts
COPY deploy/railway/e2e/e2e.sh /opt/apex/railway/e2e.sh
ENV UV_PYTHON=3.12 UV_CACHE_DIR=/tmp/uv-cache UV_PYTHON_INSTALL_DIR=/opt/uv-python
# Pre-resolve the engine env (spark image ships Python 3.10; engine needs >=3.11).
RUN cd /opt/apex/src/engine && uv sync --frozen --extra dev --extra clickhouse && uv pip install --python .venv "mcp>=1,<2" \
    && chmod +x /opt/apex/railway/e2e.sh && chown -R spark /opt/apex /tmp/uv-cache /opt/uv-python
USER spark
CMD ["/opt/apex/railway/e2e.sh"]
