"""Finalize v2 Runner outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rdetoolkit.errors import ERROR_CATALOG, write_job_errorlog_file
from rdetoolkit.report.run_report import RunReport
from rdetoolkit.types import RdeConfig


_DEFAULT_FAILURE_CODE = 3001


def finalize(report: RunReport, config: RdeConfig) -> None:
    """Persist the run report and write ``job.failed`` for failed runs.

    The ``job.failed`` file is delegated to v1 ``write_job_errorlog_file`` so
    the RDE platform format stays owned by the existing public API.

    Args:
        report: Run report produced by the Runner.
        config: Effective v2 Runner configuration.
    """
    _ = config
    _write_run_report(report)
    if report.status == "failed":
        code, message = _failure_error(report)
        write_job_errorlog_file(code, message)


def _write_run_report(report: RunReport) -> None:
    logs_dir = Path("data") / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    report_path = logs_dir / f"run_report_{report.run_id}.json"
    report_path.write_text(report.to_json(), encoding="utf-8")


def _failure_error(report: RunReport) -> tuple[int, str]:
    error = report.error or {}
    raw_code = error.get("code", _DEFAULT_FAILURE_CODE)
    code = raw_code if isinstance(raw_code, int) else _DEFAULT_FAILURE_CODE
    if code not in ERROR_CATALOG:
        code = _DEFAULT_FAILURE_CODE

    raw_message: Any = error.get("message")
    message = raw_message if isinstance(raw_message, str) and raw_message else ERROR_CATALOG[code].message_template
    return code, message
