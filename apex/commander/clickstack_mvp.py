"""File-backed ClickStack MVP used by the local Commander harness."""

import json
from pathlib import Path


def append_envelope(path, envelope):
    """Append one telemetry envelope to an NDJSON store."""
    store_path = Path(path)
    store_path.parent.mkdir(parents=True, exist_ok=True)
    with store_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(envelope, sort_keys=True) + "\n")


def query_by_job_id(path, job_id):
    """Return telemetry envelopes for a job id from the NDJSON store."""
    store_path = Path(path)
    if not store_path.exists():
        return []

    matches = []
    with store_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            envelope = json.loads(line)
            if envelope.get("job_id") == job_id:
                matches.append(envelope)
    return matches
