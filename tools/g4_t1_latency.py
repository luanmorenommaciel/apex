"""Measure deterministic T1 diagnosis latency over a Spark event log."""

import argparse
import json
import tempfile
import time
from pathlib import Path

from apex import apexlib
from apex.commander.clickstack_mvp import append_envelope
from apex.commander.diagnostic_mvp import diagnose_findings
from apex.commander.evidence_validator import validate_finding
from apex.commander.telemetry import build_telemetry


def measure(event_log, job_id):
    with tempfile.TemporaryDirectory() as tempdir:
        store = Path(tempdir) / "clickstack.ndjson"
        t0 = time.perf_counter()
        events = apexlib.read_events(event_log)
        envelope = build_telemetry(events, job_id=job_id)
        append_envelope(store, envelope)
        findings = diagnose_findings(store, job_id)
        validations = [validate_finding(finding) for finding in findings]
        elapsed_ms = (time.perf_counter() - t0) * 1000

    return {
        "event_log": str(event_log),
        "job_id": job_id,
        "elapsed_ms": round(elapsed_ms, 3),
        "finding_count": len(findings),
        "findings": findings,
        "validations": validations,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("event_log")
    parser.add_argument("--job-id", required=True)
    args = parser.parse_args()

    result = measure(args.event_log, args.job_id)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
