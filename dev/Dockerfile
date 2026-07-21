# Apex dev-env Spark image (T2)
# One image reused for master / worker / history — guarantees identical JARs everywhere.
# S3A + AWS SDK + Delta jars are BAKED IN (not --packages) so the History Server works
# offline and startup is deterministic (DEV.md key decision).

ARG SPARK_IMAGE=apache/spark:4.0.1-scala2.13-java17-python3-ubuntu
FROM ${SPARK_IMAGE}

# Versions passed from .env via compose build args. Defaults = PRIMARY quartet.
ARG HADOOP_AWS_VERSION=3.4.1
ARG AWS_SDK_BUNDLE_VERSION=2.24.6
ARG DELTA_VERSION=4.0.0
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
    MAVEN="https://repo1.maven.org/maven2"; \
    curl -fSL -o "hadoop-aws-${HADOOP_AWS_VERSION}.jar" \
      "${MAVEN}/org/apache/hadoop/hadoop-aws/${HADOOP_AWS_VERSION}/hadoop-aws-${HADOOP_AWS_VERSION}.jar"; \
    curl -fSL -o "aws-sdk-bundle-${AWS_SDK_BUNDLE_VERSION}.jar" \
      "${MAVEN}/software/amazon/awssdk/bundle/${AWS_SDK_BUNDLE_VERSION}/bundle-${AWS_SDK_BUNDLE_VERSION}.jar"; \
    curl -fSL -o "delta-spark_${SCALA_BIN}-${DELTA_VERSION}.jar" \
      "${MAVEN}/io/delta/delta-spark_${SCALA_BIN}/${DELTA_VERSION}/delta-spark_${SCALA_BIN}-${DELTA_VERSION}.jar"; \
    curl -fSL -o "delta-storage-${DELTA_VERSION}.jar" \
      "${MAVEN}/io/delta/delta-storage/${DELTA_VERSION}/delta-storage-${DELTA_VERSION}.jar"; \
    ls -1 hadoop-aws-*.jar aws-sdk-bundle-*.jar delta-spark_*.jar delta-storage-*.jar

# Python deps for the jobs + listener (OTLP/HTTP POST is plain JSON → requests).
RUN python3 -m pip install --no-cache-dir requests==2.32.3

# Dev-lane JVM helpers (package apexdev), compiled against the image's Spark jars:
#   - PlanFingerprint — mirrors the jar's apex.ApexPlanFingerprint so the Python and
#     Scala plan_fingerprints match byte-for-byte.
#   - StageListener   — JVM SparkListener that emits one contract record per stage
#     (robust: no py4j JVM→Python callbacks).
# Baked into /opt/apex/lib/apex-devfp.jar (on the driver classpath via spark-defaults).
COPY jvm/ /tmp/apexdev/apexdev/
RUN set -eux; \
    mkdir -p /opt/apex/lib; \
    javac -cp "${SPARK_HOME}/jars/*" -d /tmp/apexdev/out /tmp/apexdev/apexdev/*.java; \
    (cd /tmp/apexdev/out && jar cf /opt/apex/lib/apex-devfp.jar apexdev); \
    jar tf /opt/apex/lib/apex-devfp.jar | grep -E 'PlanFingerprint|StageListener' || true; \
    rm -rf /tmp/apexdev; \
    ls -l /opt/apex/lib/apex-devfp.jar

# Apex job code lands here at runtime (mounted by compose); keep it importable.
ENV PYTHONPATH=/opt/apex:${PYTHONPATH}

USER spark
