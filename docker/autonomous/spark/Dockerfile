ARG SPARK_BASE_IMAGE=apache/spark:4.1.2-scala2.13-java17-python3-ubuntu
FROM ${SPARK_BASE_IMAGE}

ARG HADOOP_AWS_VERSION=3.4.1
ARG AWS_SDK_BUNDLE_VERSION=2.29.52

USER root

RUN mkdir -p /opt/apex/listener

RUN set -eux; \
    curl --retry 3 --connect-timeout 20 --max-time 180 -fsSL "https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/${HADOOP_AWS_VERSION}/hadoop-aws-${HADOOP_AWS_VERSION}.jar" \
      -o "/opt/spark/jars/hadoop-aws-${HADOOP_AWS_VERSION}.jar"; \
    curl --retry 3 --connect-timeout 20 --max-time 180 -fsSL "https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/${AWS_SDK_BUNDLE_VERSION}/bundle-${AWS_SDK_BUNDLE_VERSION}.jar" \
      -o "/opt/spark/jars/aws-sdk-bundle-${AWS_SDK_BUNDLE_VERSION}.jar"; \
    chmod 0644 /opt/spark/jars/hadoop-aws-${HADOOP_AWS_VERSION}.jar /opt/spark/jars/aws-sdk-bundle-${AWS_SDK_BUNDLE_VERSION}.jar

COPY docker/autonomous/spark/spark-defaults.conf /opt/spark/conf/spark-defaults.conf

USER spark
