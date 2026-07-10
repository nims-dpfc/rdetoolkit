"""Tests for rdetoolkit.workflows.run() v2 dispatch (Session D2, TC-DISPATCH-001..006).

Written before implementation (TDD Red phase).
Target: make all tests pass in codex-worker Green phase.

Design authority: local/develop/v2/Design.md v2.1 §11 (v1 compat dispatch).
Session authority: local/develop/v2/tasks/session_d2.md D2.8, Known Trap 1
(the CURRENT signature is already fully keyword-only:
``def run(*, custom_dataset_function=None, config=None)`` -- D2 only inserts
``flow: FlowFn | type[ProcessingTemplate] | None = None`` into that existing
keyword-only parameter list; ``custom_dataset_function``'s parameter kind
must not change), decisions_pre_A1.md Ruling 4 (flow= keyword-only, E1001).

Pinned dispatch contract:
    run(flow=<flow_fn>)                              -> v2 Runner, returns RunReport
    run(custom_dataset_function=<fn>)                 -> v1 code path, returns str (byte-identical, no DeprecationWarning)
    run(flow=..., custom_dataset_function=...)         -> RdeConfigError(code=1001)
    run()  (neither specified)                         -> v1-compatible behavior maintained
        (Design §11: "Python API でどちらも未指定 -> v1 互換のため既存
        workflows.run() 挙動を維持"; this is a CLI-layer contract (§9.3), NOT
        a Python API usage error -- run() must NOT raise RdeConfigError(1001)
        for this case.)

This file is entirely separate from ``tests/test_workflow.py`` (v1, never
modified) -- it only exercises the new v2-side dispatch branch.
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import pytest

from rdetoolkit.models.config import Config, MultiDataTileSettings, SystemSettings
from rdetoolkit.workflows import run as v1_run


def _no_op_dataset_function(srcpaths: object, resource_paths: object) -> None:
    """v1 custom_dataset_function that performs no writes."""
    return


# v1's built-in invoice_basic_and_sample.schema_.json requires top-level
# "datasetId"/"basic", and "basic" requires "dateSubmitted"/"dataOwnerId"/
# "dataName" (dataOwnerId must match ^([0-9a-zA-Z]{56})$). This is separate
# from -- and always enforced in addition to -- the caller-supplied
# invoice.schema.json.
_SEED_INVOICE_JSON: dict = {
    "datasetId": "seed-dataset",
    "basic": {
        "dateSubmitted": "2026-07-10",
        "dataOwnerId": "0" * 56,
        "dataName": "seed",
    },
}


def _build_v1_invoice_fixture(root: Path) -> None:
    """Minimal v1-runnable cwd-relative data/ tree.

    Mirrors ``tests/v2/golden/test_dir_tree_parity.py``'s
    ``_build_invoice_fixture`` shape (replicated inline, not imported --
    this session's "never import tests/ root helpers" rule).
    """
    (root / "data" / "inputdata").mkdir(parents=True)
    (root / "data" / "inputdata" / "test_single.txt").write_text("dummy", encoding="utf-8")
    (root / "data" / "invoice").mkdir(parents=True)
    (root / "data" / "invoice" / "invoice.json").write_text(
        json.dumps(_SEED_INVOICE_JSON),
        encoding="utf-8",
    )
    (root / "data" / "tasksupport").mkdir(parents=True)
    (root / "data" / "tasksupport" / "invoice.schema.json").write_text(
        json.dumps({"properties": {}}),
        encoding="utf-8",
    )
    (root / "data" / "tasksupport" / "metadata-def.json").write_text(
        json.dumps({"constant": {}, "variable": []}),
        encoding="utf-8",
    )


def _v1_config() -> Config:
    return Config(
        system=SystemSettings(extended_mode=None, save_raw=True, save_thumbnail_image=True, magic_variable=False),
        multidata_tile=MultiDataTileSettings(ignore_errors=False),
    )


class TestFlowDispatch:
    """TC-DISPATCH-001: run(flow=...) routes to the v2 Runner and returns a RunReport."""

    def test_run_with_flow_kwarg_returns_run_report__tc_dispatch_001(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from rdetoolkit.core.flow import flow
        from rdetoolkit.core.node import node
        from rdetoolkit.report.run_report import RunReport
        from rdetoolkit.types import IterationInfo
        from rdetoolkit.workflows import run

        root = tmp_path / "run_root"
        (root / "inputdata").mkdir(parents=True)
        (root / "inputdata" / "a.txt").write_text("a", encoding="utf-8")
        (root / "unpacked").mkdir()
        (root / "invoice").mkdir()
        (root / "invoice" / "invoice.json").write_text(json.dumps({"basic": {}}), encoding="utf-8")
        (root / "tasksupport").mkdir()
        monkeypatch.chdir(root)

        @node
        def _noop(iteration: IterationInfo) -> None:
            return None

        @flow
        def _pipeline(iteration: IterationInfo) -> None:
            _noop(iteration)

        result = run(flow=_pipeline)

        assert isinstance(result, RunReport)
        assert result.status in {"success", "partial", "failed"}


class TestCustomDatasetFunctionDispatch:
    """TC-DISPATCH-002: run(custom_dataset_function=...) keeps the v1 code
    path byte-identical (still returns the v1 JSON-string contract).
    """

    def test_run_with_custom_dataset_function_returns_v1_json_str__tc_dispatch_002(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.chdir(tmp_path)
        _build_v1_invoice_fixture(tmp_path)

        result = v1_run(custom_dataset_function=_no_op_dataset_function, config=_v1_config())

        assert isinstance(result, str)
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert isinstance(parsed.get("statuses"), list)


class TestMutualExclusionUsageError:
    """TC-DISPATCH-003: both flow and custom_dataset_function -> RdeConfigError(1001)."""

    def test_run_with_both_specified_raises_e1001__tc_dispatch_003(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from rdetoolkit.core.flow import flow
        from rdetoolkit.errors import RdeConfigError
        from rdetoolkit.types import IterationInfo
        from rdetoolkit.workflows import run

        @flow
        def _pipeline(iteration: IterationInfo) -> None:
            return None

        monkeypatch.chdir(tmp_path)

        with pytest.raises(RdeConfigError) as exc_info:
            run(flow=_pipeline, custom_dataset_function=_no_op_dataset_function)

        assert exc_info.value.code == 1001


class TestNeitherSpecifiedStaysV1Compatible:
    """TC-DISPATCH-004: run() with neither argument must NOT raise a usage
    error at the Python API layer (Design §11 -- that is a CLI-only contract).
    """

    def test_run_with_neither_specified_does_not_raise_usage_error__tc_dispatch_004(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from rdetoolkit.errors import RdeConfigError
        from rdetoolkit.workflows import run

        monkeypatch.chdir(tmp_path)
        _build_v1_invoice_fixture(tmp_path)

        try:
            result = run(config=_v1_config())
        except RdeConfigError as exc:
            assert exc.code != 1001, (
                "run() with BOTH flow and custom_dataset_function unspecified must "
                "NOT raise the 1xxx mutual-exclusion usage error at the Python API "
                "layer (Design §11) -- 'neither specified' usage-error behavior is "
                "a CLI-layer contract (§9.3) only"
            )
        else:
            assert isinstance(result, str)


class TestNoDeprecationWarningOnV1Path:
    """TC-DISPATCH-005: the v1 code path must never emit a DeprecationWarning
    ABOUT the run()/custom_dataset_function dispatch itself (Design §11 --
    v2.0 must not add one as part of introducing the flow= dispatch).

    Note: v1 has PRE-EXISTING, unrelated internal DeprecationWarnings (e.g.
    ``StorageDir.get_datadir is deprecated``) that this test intentionally
    does NOT flag -- flagging those would be scope creep unrelated to this
    session's dispatch change. Only a warning that mentions
    custom_dataset_function/run() dispatch is a regression this session must
    guard against.
    """

    def test_custom_dataset_function_path_emits_no_dispatch_deprecation_warning__tc_dispatch_005(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.chdir(tmp_path)
        _build_v1_invoice_fixture(tmp_path)

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            v1_run(custom_dataset_function=_no_op_dataset_function, config=_v1_config())

        dispatch_deprecation_warnings = [
            w
            for w in caught
            if issubclass(w.category, DeprecationWarning) and "custom_dataset_function" in str(w.message).lower()
        ]
        assert dispatch_deprecation_warnings == [], (
            "run(custom_dataset_function=...) must never emit a DeprecationWarning "
            "about the dispatch itself (Design §11)"
        )


class TestFlowIsKeywordOnly:
    """TC-DISPATCH-006: flow (like custom_dataset_function) must be keyword-only."""

    def test_positional_flow_argument_raises_type_error__tc_dispatch_006(self) -> None:
        """run()'s current signature is already fully keyword-only
        (session_d2.md Known Trap 1); this anchors that D2 must not change
        custom_dataset_function's parameter kind, and that flow joins it as
        keyword-only, not positional-or-keyword.
        """
        from rdetoolkit.workflows import run

        def _dummy_flow() -> None:
            return None

        with pytest.raises(TypeError):
            run(_dummy_flow)  # type: ignore[misc]
