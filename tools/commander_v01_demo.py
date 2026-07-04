"""Run the local Commander V0.1 flow over a Spark event log."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apex import apexlib
from apex.commander.clickstack_mvp import append_envelope
from apex.commander.diagnostic_mvp import diagnose_job
from apex.commander.telemetry import build_telemetry


def main(argv=None):
    parser = argparse.ArgumentParser(description="Commander V0.1 local demo")
    parser.add_argument("event_log", help="Spark event log as NDJSON, zstd, or rolling-log directory")
    parser.add_argument("store", help="Local ClickStack MVP NDJSON store")
    parser.add_argument("--job-id", required=True, help="Job id used to query the diagnosis")
    args = parser.parse_args(argv)

    events = apexlib.read_events(args.event_log)
    envelope = build_telemetry(events, job_id=args.job_id)
    append_envelope(args.store, envelope)
    print(json.dumps(diagnose_job(args.store, args.job_id), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
