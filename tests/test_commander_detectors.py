from apex.commander.findings import build_finding


def test_build_finding_keeps_legacy_title_and_new_kind():
    finding = build_finding(
        kind="shuffle_spill_candidate",
        job_id="job-42",
        severity="warning",
        confidence="medium",
        evidence={"stage_id": 3},
        recommendations=["Reduce shuffle spill."],
    )

    assert finding["status"] == "finding"
    assert finding["kind"] == "shuffle_spill_candidate"
    assert finding["title"] == "shuffle_spill_candidate"
    assert finding["job_id"] == "job-42"
    assert finding["evidence"]["stage_id"] == 3
