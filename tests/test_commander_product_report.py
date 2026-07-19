import json

from apex.commander.product_report import (
    ProductReportInputs,
    build_product_snapshot,
    render_product_report,
)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_product_snapshot_extracts_remote_loop_and_known_gaps(tmp_path):
    compare = {
        "status": "improved",
        "before": {
            "app_id": "app-before",
            "metrics": {"finding_count": 1, "max_skew_ratio": 29.4},
        },
        "after": {
            "app_id": "app-after",
            "metrics": {"finding_count": 0, "max_skew_ratio": 0.0},
        },
        "comparisons": [
            {
                "metric": "finding_count",
                "before": 1,
                "after": 0,
                "status": "improved",
            }
        ],
        "summary": {"resolved_findings": ["shuffle_skew_candidate"]},
    }
    write(
        tmp_path / "evidence" / "f7.log",
        "\n".join(
            [
                "before_app_id=app-before",
                "after_app_id=app-after",
                f"compare={json.dumps(compare)}",
                "loop_status=success elapsed_ms=100",
            ]
        ),
    )
    write(
        tmp_path / "evidence" / "mcp.log",
        "\n".join(
            [
                "tools/list: success",
                "recommend_fix: success",
                "preview_fix: success",
                "apply_fix: success",
            ]
        ),
    )
    write(tmp_path / "evidence" / "g4.log", '{\n  "elapsed_ms": 226.991\n}')
    write(
        tmp_path / "ISSUES.md",
        "| CODEX-018 | F4/L5 | gap futuro | Crew.ai/Judge real ausente em self-hosted | x | aberta |",
    )

    snapshot = build_product_snapshot(
        ProductReportInputs(
            root=tmp_path,
            f7_log="evidence/f7.log",
            mcp_gui_log="evidence/mcp.log",
            latency_log="evidence/g4.log",
            issues_file="ISSUES.md",
        )
    )

    assert snapshot["status"] == "ready_for_judge_with_known_gaps"
    assert snapshot["score"] == 90
    assert snapshot["f7"]["before_app_id"] == "app-before"
    assert snapshot["f7"]["after_app_id"] == "app-after"
    assert snapshot["latency_ms"] == 226.991
    assert "crew_judge_real_missing" in snapshot["signals"]


def test_render_product_report_contains_key_sections():
    html = render_product_report(
        {
            "status": "ready_for_judge_with_known_gaps",
            "score": 90,
            "latency_ms": 226.991,
            "f7": {
                "before_app_id": "app-before",
                "after_app_id": "app-after",
                "comparisons": [
                    {
                        "metric": "max_skew_ratio",
                        "before": 29.4,
                        "after": 0.0,
                        "status": "improved",
                    }
                ],
            },
            "strengths": ["F7 remoto verde"],
            "gaps": ["Crew.ai/Judge real ainda nao implementado"],
            "next_actions": ["Decidir ciclo de vida do runner"],
        }
    )

    assert "Apex Codex Product Readiness" in html
    assert "app-before" in html
    assert "max_skew_ratio" in html
    assert "Crew.ai/Judge real" in html
