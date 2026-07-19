import json

from tools.mcp_ide_subprocess_smoke import main


def test_mcp_ide_subprocess_smoke_writes_evidence(tmp_path):
    work_dir = tmp_path / "workspace"
    evidence = tmp_path / "evidence" / "mcp-smoke.jsonl"

    main(["--work-dir", str(work_dir), "--evidence", str(evidence)])

    records = [json.loads(line) for line in evidence.read_text(encoding="utf-8").splitlines()]
    assert records[-1] == {"event": "harness_result", "status": "passed"}
    assert any(record["event"] == "initialize" for record in records)
    assert any(record["event"] == "tools_list" for record in records)
    assert any(record["event"] == "crew_judge_diagnose" for record in records)
    assert any(record["event"] == "apply_fix" for record in records)
    assert (work_dir / "job.py").read_text(encoding="utf-8").startswith("# REVIEW")
