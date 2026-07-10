#!/usr/bin/env python3
"""
fetch_real_log.py — baixa o event log real mais recente do MinIO para o oraculo.

Usado pelo oracle-weekly.yml (P2-12). Escolhe o objeto mais recente sob o
prefixo (spark-logs/events/<app-id>) e salva no caminho de saida. A decompressao
zstd fica a cargo do apexlib (auto-detecta magic bytes) — aqui so baixamos bytes.

Env vars esperadas: MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY
Uso:
    python3 scripts/fetch_real_log.py --bucket spark-logs --prefix events/ --output real_log.ndjson
"""
import argparse
import os
import sys


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bucket", required=True)
    p.add_argument("--prefix", default="events/")
    p.add_argument("--output", required=True)
    p.add_argument("--app-id", default=None, help="app especifico; default = mais recente")
    args = p.parse_args()

    try:
        from minio import Minio
    except ImportError:
        sys.exit("erro: pacote 'minio' nao instalado (pip install minio)")

    endpoint = os.environ.get("MINIO_ENDPOINT")
    access_key = os.environ.get("MINIO_ACCESS_KEY")
    secret_key = os.environ.get("MINIO_SECRET_KEY")
    if not all([endpoint, access_key, secret_key]):
        sys.exit("erro: MINIO_ENDPOINT / MINIO_ACCESS_KEY / MINIO_SECRET_KEY nao definidos")

    secure = endpoint.startswith("https://")
    endpoint = endpoint.split("://", 1)[-1]
    client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)

    prefix = args.prefix + args.app_id if args.app_id else args.prefix
    def _is_event_log(o):
        name = o.object_name.rsplit("/", 1)[-1]
        if o.is_dir or o.size == 0:
            return False
        if name.endswith(".inprogress") or name.startswith("appstatus"):
            return False  # marcadores do rolling event log, nao sao o log
        return True

    objects = [o for o in client.list_objects(args.bucket, prefix=prefix, recursive=True)
               if _is_event_log(o)]
    if not objects:
        sys.exit(f"erro: nenhum event log em {args.bucket}/{prefix}")

    latest = max(objects, key=lambda o: o.last_modified)
    client.fget_object(args.bucket, latest.object_name, args.output)
    size = os.path.getsize(args.output)
    print(f"baixado: {args.bucket}/{latest.object_name} -> {args.output} ({size} bytes)")


if __name__ == "__main__":
    main()
