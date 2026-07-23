from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "canonical_e2e_assert.py"
SPEC = importlib.util.spec_from_file_location("canonical_e2e_assert", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def row(**overrides):
    base = {
        "stage_id": 2,
        "stage_attempt": 0,
        "shuffle_read_bytes": 0,
        "spill_disk_bytes": 0,
        "task_count": 8,
        "task_duration_p50_ms": 10,
        "task_duration_p99_ms": 10,
    }
    base.update(overrides)
    return base


class CanonicalE2EAssertionTests(unittest.TestCase):
    def test_skew_requires_ratio_above_ten(self):
        result = MODULE.evaluate("skew_join", [row(task_duration_p99_ms=101)])
        self.assertEqual(10.1, result["max_p99_p50_ratio"])

    def test_spill_requires_disk_spill(self):
        result = MODULE.evaluate("spill", [row(spill_disk_bytes=42)])
        self.assertEqual(42, result["spill_disk_bytes"])

    def test_bad_shuffle_requires_two_large_reduce_tasks(self):
        result = MODULE.evaluate("bad_shuffle", [row(stage_id=9, task_count=2, shuffle_read_bytes=1_000_001)])
        self.assertEqual([9], result["matched_stage_ids"])

    def test_driver_oom_requires_pre_failure_stage(self):
        self.assertEqual(1, MODULE.evaluate("driver_oom", [row()])["pre_oom_stage_count"])

    def test_missing_stage_telemetry_fails(self):
        with self.assertRaisesRegex(MODULE.AssertionFailure, "canonical_stage_telemetry_missing"):
            MODULE.evaluate("spill", [])

    def test_bad_shuffle_does_not_accept_wrong_shape(self):
        with self.assertRaisesRegex(MODULE.AssertionFailure, "two_task_large_shuffle_stage_missing"):
            MODULE.evaluate("bad_shuffle", [row(task_count=3, shuffle_read_bytes=2_000_000)])

    def test_waits_until_late_pathology_evidence_arrives(self):
        batches = iter([
            [row(stage_id=0, task_count=2, shuffle_read_bytes=0)],
            [row(stage_id=15, task_count=2, shuffle_read_bytes=65_765_168)],
        ])
        rows, result = MODULE.wait_for_evidence(
            lambda: next(batches), scenario="bad_shuffle", wait_seconds=1, poll_seconds=0
        )
        self.assertEqual([15], result["matched_stage_ids"])
        self.assertEqual(15, rows[0]["stage_id"])


if __name__ == "__main__":
    unittest.main()
