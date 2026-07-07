"""Diagnostics CLI used by `make diagnose` and callable directly.

Usage:
    uv run python -m apex_diagnostics.cli analyze APP_ID
    uv run python -m apex_diagnostics.cli analyze --latest
"""

import argparse

from spark_platform.utils.logger import logger

from apex_diagnostics.clickhouse import ClickHouseConnectClient
from apex_diagnostics.config import load_thresholds
from apex_diagnostics.crew.pipeline import analyze
from apex_diagnostics.reports.store import save_report, unanalyzed_runs


def analyze_app(client: ClickHouseConnectClient, app_id: str) -> None:
    thresholds = load_thresholds()
    report = analyze(app_id, client, thresholds)
    report_uid = save_report(client, report)
    logger.info(
        f"Stored report {report_uid} for {app_id}: status={report.status} "
        f"max_severity={report.max_severity()} findings={len(report.findings)} "
        f"recommendations={len(report.recommendations)}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="apex-diagnostics")
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze_parser = subparsers.add_parser("analyze", help="Run detectors + Crew A and store a report")
    analyze_parser.add_argument("app_id", nargs="?", help="Spark application id to analyze")
    analyze_parser.add_argument("--latest", action="store_true", help="Analyze recent runs without a stored report")
    args = parser.parse_args(argv)

    if not args.app_id and not args.latest:
        parser.error("provide APP_ID or --latest")

    client = ClickHouseConnectClient()
    if args.latest:
        app_ids = unanalyzed_runs(client)
        if not app_ids:
            logger.info("No unanalyzed runs found in spark_tasks")
            return 0
    else:
        app_ids = [args.app_id]

    for app_id in app_ids:
        analyze_app(client, app_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
