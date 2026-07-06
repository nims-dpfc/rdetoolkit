"""Phase B testing helpers for v2 workflows."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from rdetoolkit.report.run_report import RunReport
from rdetoolkit.runner.finalize import finalize as finalize_run
from rdetoolkit.runner.lifecycle import Runner
from rdetoolkit.types import OutputContext, RdeConfig


def run_flow(flow_fn_or_template: Callable[..., Any], fixture_dir: Path) -> RunReport:
    """Run a flow-like callable through the Phase B Runner skeleton.

    Args:
        flow_fn_or_template: Callable placeholder for later flow dispatch phases.
        fixture_dir: Directory used as the source fixture root.

    Returns:
        Run report produced by the Runner.
    """
    fixture_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as run_dir:
        root = Path(run_dir)
        _build_minimal_rde_tree(root, fixture_dir)
        with _chdir(root):
            runner = _TestingRunner(root=root, inputdata_path=root / "inputdata", unpacked_dir_path=root / "unpacked")
            return runner.run(flow_fn_or_template)


def assert_output_tree(out: OutputContext, golden_dir: Path) -> None:
    """Assert that an output context's directory tree matches ``golden_dir``.

    Args:
        out: Output context to compare.
        golden_dir: Root directory containing the expected tree.

    Raises:
        AssertionError: If the relative directory sets differ.
    """
    actual = _collect_output_dirs(out)
    expected = _collect_dirs(golden_dir, golden_dir)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        msg = "output tree mismatch"
        if missing:
            msg += f"\nmissing: {missing}"
        if extra:
            msg += f"\nextra: {extra}"
        raise AssertionError(msg)


class _TestingRunner(Runner):
    def finalize(self, report: RunReport, config: RdeConfig) -> None:
        finalize_run(report, config)


def _build_minimal_rde_tree(root: Path, fixture_dir: Path) -> None:
    for name in ("inputdata", "invoice", "tasksupport", "unpacked"):
        (root / name).mkdir(parents=True, exist_ok=True)
    for path in fixture_dir.iterdir():
        if path.is_file():
            (root / "inputdata" / path.name).write_bytes(path.read_bytes())


@contextmanager
def _chdir(path: Path) -> Iterator[None]:
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def _collect_output_dirs(out: OutputContext) -> set[str]:
    roots = (
        out.struct,
        out.meta,
        out.main_image,
        out.other_image,
        out.thumbnail,
        out.attachment,
        out.nonshared_raw,
        out.raw,
        out.invoice,
        out.logs,
    )
    common_root = Path(os.path.commonpath([str(path.parent) for path in roots]))
    collected: set[str] = set()
    for root in roots:
        collected.add(str(root.relative_to(common_root)))
        collected.update(_collect_dirs(root, common_root))
    return collected


def _collect_dirs(root: Path, relative_to: Path) -> set[str]:
    if not root.exists():
        return set()
    return {str(path.relative_to(relative_to)) for path in root.rglob("*") if path.is_dir()}
