"""Tests for rdetoolkit v2 runner finalize (TC-FIN-001..007).

Written before implementation (TDD Red phase).
Target: make all tests pass in codex-worker Green phase.

Design authority: local/develop/v2/Design.md §6.3 (job.failed), §13.1, §13.3
Session authority: local/develop/v2/tasks/session_b2.md (B2.4/B2.5/B2.6)

Contract exercised here:
    finalize(report: RunReport, config: RdeConfig) -> None
      - status == "failed"  -> calls rdetoolkit.errors.write_job_errorlog_file
                                with an int ERROR_CATALOG code and a message;
                                v1 owns the "ErrorCode=/ErrorMessage=" format.
      - status in {"success", "partial"} -> job.failed is NOT written.
      - Regardless of status, RunReport is persisted as JSON to
        ``data/logs/run_report_{run_id}.json`` (cwd-relative, same "data" root
        convention as write_job_errorlog_file / StorageDir.get_datadir).

``write_job_errorlog_file`` itself is v1 public surface and MUST NOT be
reimplemented by finalize.py; finalize.py only calls it.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from rdetoolkit.errors import ERROR_CATALOG
from rdetoolkit.report.run_report import RunReport
from rdetoolkit.types import RdeConfig

# Target import — fails until implementation exists (expected in Red phase):
from rdetoolkit.runner.finalize import finalize

_NODE_EXECUTION_FAILED_CODE = 3001  # ERROR_CATALOG[3001].name == "NodeExecutionFailed"


def _make_report(status: str, *, error: dict[str, object] | None = None, run_id: str = "run-0001") -> RunReport:
    return RunReport(
        run_id=run_id,
        status=status,
        flow_id="tests.v2.runner.test_finalize.stub_flow",
        mode="invoice",
        started_at="2026-07-06T00:00:00",
        duration_ms=1.0,
        config_digest="sha256:deadbeef",
        iterations=[],
        warnings=[],
        error=error,
    )


@pytest.fixture()
def _cwd_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Chdir into a fresh tmp_path with a pre-created ``data/`` directory.

    ``write_job_errorlog_file`` resolves its target via
    ``StorageDir.get_datadir(False)``, which is always cwd-relative "data" and
    does not create the directory itself.
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()
    return tmp_path / "data"


class TestFinalizeWritesJobFailedOnFailure:
    """TC-FIN-001: status=failed writes job.failed."""

    def test_failed_status_writes_job_failed(self, _cwd_data_dir: Path) -> None:
        """job.failed must exist under data/ after finalize() on a failed report."""
        report = _make_report("failed", error={"code": _NODE_EXECUTION_FAILED_CODE, "message": "boom"})

        finalize(report, RdeConfig())

        assert (_cwd_data_dir / "job.failed").exists()


class TestFinalizeSkipsJobFailedOnSuccessOrPartial:
    """TC-FIN-002 / TC-FIN-003: success/partial must not write job.failed."""

    def test_success_status_does_not_write_job_failed(self, _cwd_data_dir: Path) -> None:
        """job.failed must be absent after finalize() on a successful report."""
        report = _make_report("success")

        finalize(report, RdeConfig())

        assert not (_cwd_data_dir / "job.failed").exists()

    def test_partial_status_does_not_write_job_failed(self, _cwd_data_dir: Path) -> None:
        """job.failed must be absent after finalize() on a partial report."""
        report = _make_report("partial")

        finalize(report, RdeConfig())

        assert not (_cwd_data_dir / "job.failed").exists()


class TestFinalizeJobFailedFormat:
    """TC-FIN-004 / TC-FIN-005: job.failed content matches the v1 format with an int code."""

    def test_job_failed_content_matches_v1_format_with_int_code(self, _cwd_data_dir: Path) -> None:
        """Content must be exactly 'ErrorCode=<int>\\nErrorMessage=<msg>\\n'."""
        report = _make_report(
            "failed",
            error={"code": _NODE_EXECUTION_FAILED_CODE, "message": "node execution failed for call c-1"},
        )

        finalize(report, RdeConfig())

        content = (_cwd_data_dir / "job.failed").read_text(encoding="utf_8")
        assert content == f"ErrorCode={_NODE_EXECUTION_FAILED_CODE}\nErrorMessage=node execution failed for call c-1\n"
        # The code line must carry an int literal, never a catalog string name.
        code_line = content.splitlines()[0]
        assert code_line == f"ErrorCode={_NODE_EXECUTION_FAILED_CODE}"
        assert ERROR_CATALOG[_NODE_EXECUTION_FAILED_CODE].name not in code_line


class TestFinalizeSingleResponsibility:
    """TC-FIN-006: finalize is the sole, exactly-once caller of write_job_errorlog_file."""

    def test_finalize_calls_write_job_errorlog_file_exactly_once(
        self, _cwd_data_dir: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """finalize must delegate to write_job_errorlog_file exactly once, with the int code."""
        mock_write = MagicMock()
        monkeypatch.setattr("rdetoolkit.runner.finalize.write_job_errorlog_file", mock_write)
        report = _make_report("failed", error={"code": _NODE_EXECUTION_FAILED_CODE, "message": "boom"})

        finalize(report, RdeConfig())

        mock_write.assert_called_once_with(_NODE_EXECUTION_FAILED_CODE, "boom")

    def test_finalize_does_not_call_write_job_errorlog_file_on_success(
        self, _cwd_data_dir: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """finalize must not invoke write_job_errorlog_file at all for a successful report."""
        mock_write = MagicMock()
        monkeypatch.setattr("rdetoolkit.runner.finalize.write_job_errorlog_file", mock_write)
        report = _make_report("success")

        finalize(report, RdeConfig())

        mock_write.assert_not_called()


class TestFinalizePersistsRunReport:
    """TC-FIN-007: RunReport JSON is saved to logs/run_report_{run_id}.json regardless of status."""

    def test_run_report_json_saved_on_failure(self, _cwd_data_dir: Path) -> None:
        """A logs/run_report_{run_id}.json file must exist after a failed run is finalized."""
        report = _make_report("failed", error={"code": _NODE_EXECUTION_FAILED_CODE, "message": "boom"}, run_id="run-fail-1")

        finalize(report, RdeConfig())

        report_path = _cwd_data_dir / "logs" / "run_report_run-fail-1.json"
        assert report_path.exists()
        saved = json.loads(report_path.read_text(encoding="utf-8"))
        assert saved["run_id"] == "run-fail-1"
        assert saved["status"] == "failed"

    def test_run_report_json_saved_on_success(self, _cwd_data_dir: Path) -> None:
        """A logs/run_report_{run_id}.json file must exist after a successful run is finalized too."""
        report = _make_report("success", run_id="run-ok-1")

        finalize(report, RdeConfig())

        report_path = _cwd_data_dir / "logs" / "run_report_run-ok-1.json"
        assert report_path.exists()
        saved = json.loads(report_path.read_text(encoding="utf-8"))
        assert saved["run_id"] == "run-ok-1"
        assert saved["status"] == "success"
