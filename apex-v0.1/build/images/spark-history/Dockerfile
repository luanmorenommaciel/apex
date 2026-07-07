# TODO(hardening): digest-pinning is inherited from the locally-built
# apex-v01-spark image (see build/images/spark/Dockerfile); no separate public
# registry reference to pin here.
ARG SPARK_RUNTIME_IMAGE=apex-v01-spark:4.1.2
FROM ${SPARK_RUNTIME_IMAGE}

USER root
COPY entrypoint.sh /opt/spark/bin/spv0-history-entrypoint.sh
RUN chmod 755 /opt/spark/bin/spv0-history-entrypoint.sh

USER spark

ENTRYPOINT ["/opt/spark/bin/spv0-history-entrypoint.sh"]
