# TODO(hardening): digest-pin GO_BASE_IMAGE (FROM golang@sha256:...) once a
# Docker daemon/registry is available to resolve the current digest for this tag.
ARG GO_BASE_IMAGE=golang:1.26-bookworm
FROM ${GO_BASE_IMAGE} AS build

WORKDIR /src
COPY go.mod go.sum ./
COPY vendor ./vendor
COPY main.go schema.sql ./
RUN CGO_ENABLED=0 GOOS=linux /usr/local/go/bin/go build -mod=vendor -trimpath -ldflags="-s -w" -o /out/spark-eventlog-loader .

FROM scratch
COPY --from=build --chown=65532:65532 /out/spark-eventlog-loader /spark-eventlog-loader
USER 65532:65532
ENTRYPOINT ["/spark-eventlog-loader"]
