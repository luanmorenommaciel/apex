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
        "task_duration_max_ms": 10,
        "task_duration_sample_count": 8,
        "successful_task_duration_p50_ms": 0,
        "successful_task_duration_p99_ms": 0,
        "successful_task_duration_max_ms": 0,
        "successful_task_sample_count": 0,
    }
    base.update(overrides)
    return base


class CanonicalE2EAssertionTests(unittest.TestCase):
    def test_skew_requires_ratio_above_ten(self):
        result = MODULE.evaluate("skew_join", [row(task_duration_p99_ms=101)])
        self.assertEqual(10.1, result["max_p99_p50_ratio"])

    def test_tail_outlier_requires_sparse_effective_duration_tail(self):
        result = MODULE.evaluate(
            "tail_outlier",
            [
                row(
                    task_count=200,
                    task_duration_sample_count=200,
                    task_duration_p99_ms=12,
                    task_duration_max_ms=101,
                )
            ],
        )
        self.assertEqual("legacy_all_attempts", result["duration_sample_source"])
        self.assertEqual(10.1, result["max_tail_ratio"])
        self.assertEqual(1.2, result["p99_p50_ratio"])

    def test_tail_outlier_uses_successful_task_population_when_available(self):
        result = MODULE.evaluate(
            "tail_outlier",
            [
                row(
                    task_count=200,
                    task_duration_sample_count=200,
                    task_duration_max_ms=1_000,
                    successful_task_sample_count=200,
                    successful_task_duration_p50_ms=10,
                    successful_task_duration_p99_ms=11,
                    successful_task_duration_max_ms=101,
                )
            ],
        )
        self.assertEqual("successful_tasks", result["duration_sample_source"])
        self.assertEqual(10.1, result["max_tail_ratio"])

    def test_tail_outlier_does_not_accept_p99_without_max_tail_evidence(self):
        with self.assertRaisesRegex(MODULE.AssertionFailure, "tail_outlier_not_observed"):
            MODULE.evaluate(
                "tail_outlier",
                [
                    row(
                        task_count=200,
                        task_duration_sample_count=200,
                        task_duration_p99_ms=1_000,
                        task_duration_max_ms=100,
                    )
                ],
            )

    def test_tail_outlier_requires_at_least_one_hundred_effective_samples(self):
        with self.assertRaisesRegex(MODULE.AssertionFailure, "tail_outlier_not_observed"):
            MODULE.evaluate(
                "tail_outlier",
                [
                    row(
                        task_count=99,
                        task_duration_sample_count=99,
                        task_duration_max_ms=1_000,
                    )
                ],
            )

    def test_tail_outlier_accepts_exactly_one_hundred_tasks_and_samples(self):
        result = MODULE.evaluate(
            "tail_outlier",
            [
                row(
                    task_count=100,
                    task_duration_sample_count=100,
                    task_duration_max_ms=101,
                )
            ],
        )
        self.assertEqual(100, result["task_count"])
        self.assertEqual(100, result["duration_sample_count"])

    def test_tail_outlier_rejects_less_than_one_hundred_tasks(self):
        with self.assertRaisesRegex(MODULE.AssertionFailure, "tail_outlier_not_observed"):
            MODULE.evaluate(
                "tail_outlier",
                [
                    row(
                        task_count=99,
                        task_duration_sample_count=200,
                        task_duration_max_ms=1_000,
                        successful_task_sample_count=200,
                        successful_task_duration_p50_ms=10,
                        successful_task_duration_p99_ms=11,
                        successful_task_duration_max_ms=101,
                    )
                ],
            )

    def test_tail_outlier_rejects_short_successful_population_even_with_qualifying_raw_rows(self):
        with self.assertRaisesRegex(MODULE.AssertionFailure, "tail_outlier_not_observed"):
            MODULE.evaluate(
                "tail_outlier",
                [
                    row(
                        task_count=200,
                        task_duration_sample_count=200,
                        task_duration_max_ms=1_000,
                        successful_task_sample_count=99,
                        successful_task_duration_p50_ms=10,
                        successful_task_duration_p99_ms=11,
                        successful_task_duration_max_ms=101,
                    )
                ],
            )

    def test_tail_outlier_uses_task_count_when_legacy_sample_count_is_absent(self):
        result = MODULE.evaluate(
            "tail_outlier",
            [
                row(
                    task_count=200,
                    task_duration_sample_count=0,
                    task_duration_max_ms=101,
                )
            ],
        )
        self.assertEqual(200, result["duration_sample_count"])

    def test_tail_outlier_rejects_zero_effective_p50(self):
        with self.assertRaisesRegex(MODULE.AssertionFailure, "tail_outlier_not_observed"):
            MODULE.evaluate(
                "tail_outlier",
                [
                    row(
                        task_count=200,
                        task_duration_sample_count=200,
                        task_duration_p50_ms=0,
                        task_duration_max_ms=1_000,
                    )
                ],
            )

    def test_tail_outlier_reports_the_strongest_qualifying_stage(self):
        result = MODULE.evaluate(
            "tail_outlier",
            [
                row(
                    stage_id=2,
                    task_count=200,
                    task_duration_sample_count=200,
                    task_duration_max_ms=101,
                ),
                row(
                    stage_id=7,
                    task_count=200,
                    task_duration_sample_count=200,
                    task_duration_max_ms=201,
                ),
            ],
        )
        self.assertEqual(7, result["stage_id"])
        self.assertEqual(20.1, result["max_tail_ratio"])

    def test_tail_outlier_waits_for_late_tail_telemetry(self):
        batches = iter([
            [row(stage_id=0, task_count=200, task_duration_sample_count=200)],
            [
                row(
                    stage_id=15,
                    task_count=200,
                    task_duration_sample_count=200,
                    task_duration_max_ms=101,
                )
            ],
        ])
        rows, result = MODULE.wait_for_evidence(
            lambda: next(batches), scenario="tail_outlier", wait_seconds=1, poll_seconds=0
        )
        self.assertEqual(15, result["stage_id"])
        self.assertEqual(15, rows[0]["stage_id"])

    def test_tail_outlier_is_an_accepted_cli_scenario(self):
        self.assertIn("tail_outlier", MODULE.SCENARIOS)

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
