"""Phase B testing helpers for v2 workflows."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Mapping, Callable, Iterable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from rdetoolkit.report.run_report import RunReport
    from rdetoolkit.runner.lifecycle import Runner
    from rdetoolkit.types import InputPaths, InvoiceData, OutputContext


def make_input_paths(tmp_path: Path, files: Iterable[str] = ()) -> InputPaths:
    """Create a minimal on-disk input tree for tests."""
    from rdetoolkit.testing.builders import make_input_paths as _make_input_paths  # noqa: PLC0415

    return _make_input_paths(tmp_path, files=files)


def make_output_context(tmp_path: Path) -> OutputContext:
    """Create a test output context with all canonical directories present."""
    from rdetoolkit.testing.builders import make_output_context as _make_output_context  # noqa: PLC0415

    return _make_output_context(tmp_path)


def make_invoice(overrides: Mapping[str, Any] | None = None) -> InvoiceData:
    """Create minimal invoice data for tests."""
    from rdetoolkit.testing.builders import make_invoice as _make_invoice  # noqa: PLC0415

    return _make_invoice(overrides=overrides)


def run_flow(flow_fn_or_template: Callable[..., Any], fixture_dir: Path) -> RunReport:
    """Run a flow-like callable through the Phase B Runner skeleton.

    Args:
        flow_fn_or_template: Callable placeholder for later flow dispatch phases.
        fixture_dir: Directory used as the source fixture root.

    Returns:
        Run report produced by the Runner.
    """
    from rdetoolkit.runner.lifecycle import Runner  # noqa: PLC0415

    fixture_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as run_dir:
        root = Path(run_dir)
        _build_minimal_rde_tree(root, fixture_dir)
        with _chdir(root):
            runner_cls = _make_testing_runner()
            runner = runner_cls(root=root, inputdata_path=root / "inputdata", unpacked_dir_path=root / "unpacked")
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


def _make_testing_runner() -> type[Runner]:
    from rdetoolkit.runner.lifecycle import Runner  # noqa: PLC0415

    class _TestingRunner(Runner):
        """Alias kept for the Phase B seam; the base Runner now finalizes for real."""

    return _TestingRunner


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
        if not root.exists():
            # A missing directory must show up as a diff, not be assumed present.
            continue
        collected.add(str(root.relative_to(common_root)))
        collected.update(_collect_dirs(root, common_root))
    return collected


def _collect_dirs(root: Path, relative_to: Path) -> set[str]:
    if not root.exists():
        return set()
    return {str(path.relative_to(relative_to)) for path in root.rglob("*") if path.is_dir()}
