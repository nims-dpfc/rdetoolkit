"""Tests for rdetoolkit v2 Runner lifecycle (TC-RUN-001..007).

Written before implementation (TDD Red phase).
Target: make all tests pass in codex-worker Green phase.

Design authority: local/develop/v2/Design.md §6.1
  6-step lifecycle: (1) load_config → (2) resolve_mode → (3) pre_validate
                 → (4) iterate → (5) post_validate → (6) finalize
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

# Target import — fails until implementation exists (expected in Red phase):
# from rdetoolkit.runner.lifecycle import Runner
# from rdetoolkit.report.run_report import RunReport


class TestRunnerLifecycle:
    """Tests for Runner.run() 6-step lifecycle (Design §6.1)."""

    def test_run_steps_called_in_config_mode_prevalidate_iterate_postvalidate_finalize_order(self) -> None:
        """TC-RUN-001: Steps 1->2->3->4->5->6 are called in Design §6.1 order."""
        from rdetoolkit.report.run_report import RunReport
        from rdetoolkit.runner.lifecycle import Runner

        runner = Runner()
        call_log: list[str] = []
        mock_report = MagicMock(spec=RunReport)

        with (
            patch.object(
                runner,
                "load_config",
                side_effect=lambda *a, **kw: call_log.append("load_config") or MagicMock(),
            ),
            patch.object(
                runner,
                "resolve_mode",
                side_effect=lambda *a, **kw: call_log.append("resolve_mode") or MagicMock(),
            ),
            patch.object(
                runner,
                "pre_validate",
                side_effect=lambda *a, **kw: call_log.append("pre_validate"),
            ),
            patch.object(
                runner,
                "iterate",
                side_effect=lambda *a, **kw: call_log.append("iterate") or mock_report,
            ),
            patch.object(
                runner,
                "post_validate",
                side_effect=lambda *a, **kw: call_log.append("post_validate"),
            ),
            patch.object(
                runner,
                "finalize",
                side_effect=lambda *a, **kw: call_log.append("finalize"),
            ),
        ):
            runner.run(lambda: None)

        assert call_log == [
            "load_config",
            "resolve_mode",
            "pre_validate",
            "iterate",
            "post_validate",
            "finalize",
        ], f"Step order wrong: {call_log}"

    def test_run_calls_iterate_and_iterate_can_be_replaced_with_stub(self) -> None:
        """TC-RUN-002: iterate step is injectable — a replaced stub is called during run()."""
        from rdetoolkit.report.run_report import RunReport
        from rdetoolkit.runner.lifecycle import Runner

        runner = Runner()
        stub_called: list[bool] = []
        mock_report = MagicMock(spec=RunReport)

        def iterate_stub(*args: object, **kwargs: object) -> MagicMock:
            stub_called.append(True)
            return mock_report

        with (
            patch.object(runner, "load_config", return_value=MagicMock()),
            patch.object(runner, "resolve_mode", return_value=MagicMock()),
            patch.object(runner, "pre_validate"),
            patch.object(runner, "iterate", side_effect=iterate_stub),
            patch.object(runner, "post_validate"),
            patch.object(runner, "finalize"),
        ):
            runner.run(lambda: None)

        assert stub_called, "iterate stub must be called exactly once during Runner.run()"

    def test_run_returns_runreport_instance(self) -> None:
        """TC-RUN-003: Runner.run() returns a RunReport instance."""
        from rdetoolkit.report.run_report import RunReport
        from rdetoolkit.runner.lifecycle import Runner

        runner = Runner()
        real_report = RunReport(
            run_id="test-run-id",
            status="success",
            flow_id="test.flow",
            mode="invoice",
            started_at="2026-01-01T00:00:00",
            duration_ms=0.0,
            config_digest="sha256:test",
            iterations=[],
            warnings=[],
        )

        with (
            patch.object(runner, "load_config", return_value=MagicMock()),
            patch.object(runner, "resolve_mode", return_value=MagicMock()),
            patch.object(runner, "pre_validate"),
            patch.object(runner, "iterate", return_value=real_report),
            patch.object(runner, "post_validate"),
            patch.object(runner, "finalize"),
        ):
            result = runner.run(lambda: None)

        assert isinstance(result, RunReport), (
            f"Runner.run() must return a RunReport instance, got {type(result)}"
        )

    def test_run_load_config_is_called_before_resolve_mode(self) -> None:
        """TC-RUN-004: load_config (step 1) is called before resolve_mode (step 2)."""
        from rdetoolkit.report.run_report import RunReport
        from rdetoolkit.runner.lifecycle import Runner

        runner = Runner()
        call_log: list[str] = []
        mock_report = MagicMock(spec=RunReport)

        with (
            patch.object(
                runner,
                "load_config",
                side_effect=lambda *a, **kw: call_log.append("load_config") or MagicMock(),
            ),
            patch.object(
                runner,
                "resolve_mode",
                side_effect=lambda *a, **kw: call_log.append("resolve_mode") or MagicMock(),
            ),
            patch.object(
                runner,
                "pre_validate",
                side_effect=lambda *a, **kw: call_log.append("pre_validate"),
            ),
            patch.object(
                runner,
                "iterate",
                side_effect=lambda *a, **kw: call_log.append("iterate") or mock_report,
            ),
            patch.object(
                runner,
                "post_validate",
                side_effect=lambda *a, **kw: call_log.append("post_validate"),
            ),
            patch.object(
                runner,
                "finalize",
                side_effect=lambda *a, **kw: call_log.append("finalize"),
            ),
        ):
            runner.run(lambda: None)

        config_pos = call_log.index("load_config")
        mode_pos = call_log.index("resolve_mode")
        assert config_pos < mode_pos, (
            f"load_config must precede resolve_mode; positions: "
            f"load_config={config_pos}, resolve_mode={mode_pos}"
        )

    def test_run_finalize_is_the_last_step_called(self) -> None:
        """TC-RUN-005: finalize (step 6) is always the last step in the lifecycle."""
        from rdetoolkit.report.run_report import RunReport
        from rdetoolkit.runner.lifecycle import Runner

        runner = Runner()
        call_log: list[str] = []
        mock_report = MagicMock(spec=RunReport)

        with (
            patch.object(
                runner,
                "load_config",
                side_effect=lambda *a, **kw: call_log.append("load_config") or MagicMock(),
            ),
            patch.object(
                runner,
                "resolve_mode",
                side_effect=lambda *a, **kw: call_log.append("resolve_mode") or MagicMock(),
            ),
            patch.object(
                runner,
                "pre_validate",
                side_effect=lambda *a, **kw: call_log.append("pre_validate"),
            ),
            patch.object(
                runner,
                "iterate",
                side_effect=lambda *a, **kw: call_log.append("iterate") or mock_report,
            ),
            patch.object(
                runner,
                "post_validate",
                side_effect=lambda *a, **kw: call_log.append("post_validate"),
            ),
            patch.object(
                runner,
                "finalize",
                side_effect=lambda *a, **kw: call_log.append("finalize"),
            ),
        ):
            runner.run(lambda: None)

        assert call_log[-1] == "finalize", (
            f"finalize must be the last step, but step order was: {call_log}"
        )

    def test_run_pre_validate_is_called_after_resolve_mode_and_before_iterate(self) -> None:
        """TC-RUN-006: pre_validate (step 3) is after resolve_mode and before iterate."""
        from rdetoolkit.report.run_report import RunReport
        from rdetoolkit.runner.lifecycle import Runner

        runner = Runner()
        call_log: list[str] = []
        mock_report = MagicMock(spec=RunReport)

        with (
            patch.object(
                runner,
                "load_config",
                side_effect=lambda *a, **kw: call_log.append("load_config") or MagicMock(),
            ),
            patch.object(
                runner,
                "resolve_mode",
                side_effect=lambda *a, **kw: call_log.append("resolve_mode") or MagicMock(),
            ),
            patch.object(
                runner,
                "pre_validate",
                side_effect=lambda *a, **kw: call_log.append("pre_validate"),
            ),
            patch.object(
                runner,
                "iterate",
                side_effect=lambda *a, **kw: call_log.append("iterate") or mock_report,
            ),
            patch.object(
                runner,
                "post_validate",
                side_effect=lambda *a, **kw: call_log.append("post_validate"),
            ),
            patch.object(
                runner,
                "finalize",
                side_effect=lambda *a, **kw: call_log.append("finalize"),
            ),
        ):
            runner.run(lambda: None)

        mode_pos = call_log.index("resolve_mode")
        prevalidate_pos = call_log.index("pre_validate")
        iterate_pos = call_log.index("iterate")
        assert mode_pos < prevalidate_pos < iterate_pos, (
            f"pre_validate must follow resolve_mode and precede iterate; "
            f"positions: resolve_mode={mode_pos}, pre_validate={prevalidate_pos}, "
            f"iterate={iterate_pos}"
        )

    def test_run_post_validate_is_called_after_iterate_and_before_finalize(self) -> None:
        """TC-RUN-007: post_validate (step 5) is after iterate and before finalize."""
        from rdetoolkit.report.run_report import RunReport
        from rdetoolkit.runner.lifecycle import Runner

        runner = Runner()
        call_log: list[str] = []
        mock_report = MagicMock(spec=RunReport)

        with (
            patch.object(
                runner,
                "load_config",
                side_effect=lambda *a, **kw: call_log.append("load_config") or MagicMock(),
            ),
            patch.object(
                runner,
                "resolve_mode",
                side_effect=lambda *a, **kw: call_log.append("resolve_mode") or MagicMock(),
            ),
            patch.object(
                runner,
                "pre_validate",
                side_effect=lambda *a, **kw: call_log.append("pre_validate"),
            ),
            patch.object(
                runner,
                "iterate",
                side_effect=lambda *a, **kw: call_log.append("iterate") or mock_report,
            ),
            patch.object(
                runner,
                "post_validate",
                side_effect=lambda *a, **kw: call_log.append("post_validate"),
            ),
            patch.object(
                runner,
                "finalize",
                side_effect=lambda *a, **kw: call_log.append("finalize"),
            ),
        ):
            runner.run(lambda: None)

        iterate_pos = call_log.index("iterate")
        postvalidate_pos = call_log.index("post_validate")
        finalize_pos = call_log.index("finalize")
        assert iterate_pos < postvalidate_pos < finalize_pos, (
            f"post_validate must follow iterate and precede finalize; "
            f"positions: iterate={iterate_pos}, post_validate={postvalidate_pos}, "
            f"finalize={finalize_pos}"
        )
