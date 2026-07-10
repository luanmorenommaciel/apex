from apex.commander.fix_preview import build_fix_preview


def test_build_fix_preview_returns_diff_without_modifying_file(tmp_path):
    source = tmp_path / "job.py"
    source.write_text("df.join(dim, 'id').count()\n", encoding="utf-8")

    preview = build_fix_preview(
        source,
        "Add salting before the skewed join.",
        replacement="# REVIEW: Add salting before this join\ndf.join(dim, 'id').count()\n",
    )

    assert source.read_text(encoding="utf-8") == "df.join(dim, 'id').count()\n"
    assert preview["mode"] == "preview"
    assert preview["target"] == str(source)
    assert "Add salting before the skewed join." in preview["recommendation"]
    assert "+# REVIEW: Add salting before this join" in preview["diff"]
    assert " df.join(dim, 'id').count()" in preview["diff"]
