# Apex dev-env Spark image (T2 + C3 packaging)
# One image reused for master / worker / history — guarantees identical JARs everywhere.
# S3A + AWS SDK + Delta jars are BAKED IN (not --packages) so the History Server works
# offline and startup is deterministic (DEV.md key decision).

# Build the self-contained Spark 4.0/Scala 2.13 plugin first. The Docker build
# context is the repository root (see docker-compose.yml), so this remains a
# fresh-clone operation without relying on a host-local Ivy or Maven cache.
# The launcher image carries the SAME sbt version jar/project/build.properties
# declares (1.10.7), so the build does not download a second launcher.
ARG SBT_IMAGE=sbtscala/scala-sbt:eclipse-temurin-17.0.14_7_1.10.7_3.6.3
ARG SPARK_IMAGE=apache/spark:4.0.1-scala2.13-java17-python3-ubuntu
ARG APEX_JAR_TARGET=apex_40
# The cell's test suite runs before assembly (decision D-2): an untested plugin is
# never baked into the lab image. APEX_JAR_SKIP_TESTS=1 skips it for inner-loop
# rebuilds only.
ARG APEX_JAR_SKIP_TESTS=0
FROM ${SBT_IMAGE} AS apex-plugin-build
WORKDIR /workspace
ENV COURSIER_REPOSITORIES=https://repo.maven.apache.org/maven2
COPY jar/build.sbt ./
COPY jar/project ./project
COPY jar/src ./src
ARG APEX_JAR_TARGET
ARG APEX_JAR_SKIP_TESTS
RUN set -eux; \
    if [ "${APEX_JAR_SKIP_TESTS}" = "1" ]; then \
      sbt -batch "${APEX_JAR_TARGET}/assembly"; \
    else \
      sbt -batch "${APEX_JAR_TARGET}/test" "${APEX_JAR_TARGET}/assembly"; \
    fi; \
    artifact="$(find target -type f -name 'apex_*-*-assembly.jar' | head -n 1)"; \
    test -n "$artifact"; \
    install -D "$artifact" /out/apex-plugin.jar; \
    jar tf /out/apex-plugin.jar | grep -q '^apex/ApexPlugin.class$'; \
    jar tf /out/apex-plugin.jar | grep -q '^io/opentelemetry/api/trace/Tracer.class$'

FROM ${SPARK_IMAGE}

# Versions passed from .env via compose build args. Defaults = PRIMARY quartet.
ARG HADOOP_AWS_VERSION=3.4.1
ARG AWS_SDK_BUNDLE_VERSION=2.24.6
ARG DELTA_VERSION=4.0.0
ARG DELTA_ARTIFACT=delta-spark_2.13
ARG SCALA_BIN=2.13

ENV SPARK_HOME=/opt/spark
USER root

# curl for jar fetch (may be absent on the slim base) — installed defensively.
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends curl ca-certificates; \
    rm -rf /var/lib/apt/lists/*

# S3A connector + AWS SDK bundle + Delta jars → $SPARK_HOME/jars
# hadoop-aws MUST equal the bundled Hadoop version (see .env pitfall note).
RUN set -eux; \
    cd "${SPARK_HOME}/jars"; \
    MAVEN="https://repo.maven.apache.org/maven2"; \
    curl -fSL -o "hadoop-aws-${HADOOP_AWS_VERSION}.jar" \
      "${MAVEN}/org/apache/hadoop/hadoop-aws/${HADOOP_AWS_VERSION}/hadoop-aws-${HADOOP_AWS_VERSION}.jar"; \
    curl -fSL -o "aws-sdk-bundle-${AWS_SDK_BUNDLE_VERSION}.jar" \
      "${MAVEN}/software/amazon/awssdk/bundle/${AWS_SDK_BUNDLE_VERSION}/bundle-${AWS_SDK_BUNDLE_VERSION}.jar"; \
    curl -fSL -o "${DELTA_ARTIFACT}-${DELTA_VERSION}.jar" \
      "${MAVEN}/io/delta/${DELTA_ARTIFACT}/${DELTA_VERSION}/${DELTA_ARTIFACT}-${DELTA_VERSION}.jar"; \
    curl -fSL -o "delta-storage-${DELTA_VERSION}.jar" \
      "${MAVEN}/io/delta/delta-storage/${DELTA_VERSION}/delta-storage-${DELTA_VERSION}.jar"; \
    ls -1 hadoop-aws-*.jar aws-sdk-bundle-*.jar delta-spark_*.jar delta-storage-*.jar

# No extra Python packages: the jobs and common/ use only pyspark (shipped by
# the base image) and the standard library. Telemetry is emitted by the Scala
# plugin, not by a Python HTTP client.

# Make the canonical plugin available to every Spark process.
COPY --from=apex-plugin-build /out/apex-plugin.jar /opt/apex/lib/apex-plugin.jar

# The dev-only fingerprint helper remains a test utility. Telemetry is emitted
# only by apex.ApexPlugin; no JSONL listener is compiled into this image.
COPY dev/jvm/PlanFingerprint.java /tmp/apexdev/apexdev/PlanFingerprint.java
RUN set -eux; \
    mkdir -p /opt/apex/lib; \
    javac -cp "${SPARK_HOME}/jars/*" \
      -d /tmp/apexdev/out /tmp/apexdev/apexdev/PlanFingerprint.java; \
    (cd /tmp/apexdev/out && jar cf /opt/apex/lib/apex-devfp.jar apexdev); \
    jar tf /opt/apex/lib/apex-devfp.jar | grep -q '^apexdev/PlanFingerprint.class$'; \
    ! jar tf /opt/apex/lib/apex-devfp.jar | grep -q 'StageListener'; \
    rm -rf /tmp/apexdev; \
    ls -l /opt/apex/lib/apex-devfp.jar
# The official APEX plugin is the only telemetry implementation in the image.
RUN jar tf /opt/apex/lib/apex-plugin.jar | grep -E 'apex/ApexPlugin|io/opentelemetry/api/trace/Tracer' \
    && ls -lh /opt/apex/lib/apex-plugin.jar

# Apex job code lands here at runtime (mounted by compose); keep it importable.
ENV PYTHONPATH=/opt/apex:${PYTHONPATH}

USER spark
