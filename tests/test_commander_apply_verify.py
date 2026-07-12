from apex.commander.apply_verify import (
    apply_recommendation,
    verify_recommendation_apply,
)
from apex.commander.findings import build_finding
from apex.commander.recommendations import preview_recommendation


class FakeFindingStore:
    def __init__(self, records):
        self.records = records

    def query_by_job_id(self, job_id):
        return self.records.get(job_id, [])


def accepted_skew_record():
    finding = build_finding(
        "shuffle_skew_candidate",
        "job-42",
        "warning",
        "medium",
        {
            "app_id": "app-apply",
            "stage_id": 2,
            "ratio": 29.5,
            "hot_records": 165297,
            "median_cold_records": 5596,
            "task_count": 8,
        },
        ["Validar skew antes de aplicar mudanca."],
    )
    return {"finding": finding, "validation": {"status": "valid", "accepted": True}}


def test_preview_recommendation_returns_approval_token(tmp_path):
    source = tmp_path / "job.py"
    source.write_text("df.join(dim, 'id').count()\n", encoding="utf-8")
    store = FakeFindingStore({"job-42": [accepted_skew_record()]})

    preview = preview_recommendation(
        store,
        "job-42",
        "job-42:shuffle_skew_candidate:stage-2:0",
        source,
        "# REVIEW: validate skew before this join\ndf.join(dim, 'id').count()\n",
    )

    assert preview["status"] == "preview_ready"
    assert preview["approval"]["required"] is True
    assert len(preview["approval"]["token"]) == 64
    assert preview["before_sha256"] != preview["after_sha256"]


def test_apply_recommendation_requires_configured_apply_root(tmp_path):
    source = tmp_path / "job.py"
    source.write_text("df.join(dim, 'id').count()\n", encoding="utf-8")
    store = FakeFindingStore({"job-42": [accepted_skew_record()]})

    result = apply_recommendation(
        store,
        "job-42",
        "job-42:shuffle_skew_candidate:stage-2:0",
        source,
        "# REVIEW: validate skew before this join\ndf.join(dim, 'id').count()\n",
        "token",
    )

    assert result["status"] == "apply_root_not_configured"
    assert source.read_text(encoding="utf-8") == "df.join(dim, 'id').count()\n"


def test_apply_recommendation_rejects_invalid_approval_token(tmp_path):
    source = tmp_path / "job.py"
    source.write_text("df.join(dim, 'id').count()\n", encoding="utf-8")
    store = FakeFindingStore({"job-42": [accepted_skew_record()]})

    result = apply_recommendation(
        store,
        "job-42",
        "job-42:shuffle_skew_candidate:stage-2:0",
        source,
        "# REVIEW: validate skew before this join\ndf.join(dim, 'id').count()\n",
        "wrong-token",
        apply_root=tmp_path,
    )

    assert result["status"] == "invalid_approval_token"
    assert result["verification"]["status"] == "not_run"
    assert source.read_text(encoding="utf-8") == "df.join(dim, 'id').count()\n"


def test_apply_recommendation_rejects_path_outside_apply_root(tmp_path):
    root = tmp_path / "allowed"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    source = outside / "job.py"
    source.write_text("df.join(dim, 'id').count()\n", encoding="utf-8")
    store = FakeFindingStore({"job-42": [accepted_skew_record()]})

    result = apply_recommendation(
        store,
        "job-42",
        "job-42:shuffle_skew_candidate:stage-2:0",
        source,
        "# REVIEW: validate skew before this join\ndf.join(dim, 'id').count()\n",
        "token",
        apply_root=root,
    )

    assert result["status"] == "outside_apply_root"
    assert source.read_text(encoding="utf-8") == "df.join(dim, 'id').count()\n"


def test_apply_recommendation_writes_and_verifies_with_matching_token(tmp_path):
    source = tmp_path / "job.py"
    original = "df.join(dim, 'id').count()\n"
    replacement = "# REVIEW: validate skew before this join\ndf.join(dim, 'id').count()\n"
    source.write_text(original, encoding="utf-8")
    store = FakeFindingStore({"job-42": [accepted_skew_record()]})
    preview = preview_recommendation(
        store,
        "job-42",
        "job-42:shuffle_skew_candidate:stage-2:0",
        source,
        replacement,
    )

    result = apply_recommendation(
        store,
        "job-42",
        "job-42:shuffle_skew_candidate:stage-2:0",
        source,
        replacement,
        preview["approval"]["token"],
        apply_root=tmp_path,
    )

    assert result["status"] == "applied"
    assert result["verification"]["status"] == "verified"
    assert source.read_text(encoding="utf-8") == replacement


def test_apply_recommendation_preserves_preview_token_for_relative_target(tmp_path, monkeypatch):
    source = tmp_path / "job.py"
    original = "df.join(dim, 'id').count()\n"
    replacement = "# REVIEW: validate skew before this join\ndf.join(dim, 'id').count()\n"
    source.write_text(original, encoding="utf-8")
    store = FakeFindingStore({"job-42": [accepted_skew_record()]})
    monkeypatch.chdir(tmp_path)

    preview = preview_recommendation(
        store,
        "job-42",
        "job-42:shuffle_skew_candidate:stage-2:0",
        "job.py",
        replacement,
    )
    result = apply_recommendation(
        store,
        "job-42",
        "job-42:shuffle_skew_candidate:stage-2:0",
        "job.py",
        replacement,
        preview["approval"]["token"],
        apply_root=tmp_path,
    )

    assert result["status"] == "applied"
    assert result["verification"]["status"] == "verified"
    assert source.read_text(encoding="utf-8") == replacement


def test_verify_recommendation_apply_detects_mismatch(tmp_path):
    source = tmp_path / "job.py"
    source.write_text("df.join(dim, 'id').count()\n", encoding="utf-8")

    result = verify_recommendation_apply(
        source,
        "0" * 64,
        apply_root=tmp_path,
    )

    assert result["status"] == "mismatch"
