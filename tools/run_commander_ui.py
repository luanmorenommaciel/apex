"""Run the local read-only Apex Commander UI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from apex.commander.ui_server import create_ui_server


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    args = parser.parse_args()

    server = create_ui_server(args.root, args.host, args.port)
    address, port = server.server_address[:2]
    print(f"Apex Commander UI: http://{address}:{port}/")
    print("Mode: read_only (GET /, /api/health, /api/snapshot)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nApex Commander UI stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
