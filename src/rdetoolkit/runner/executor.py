"""Common tile execution for planned v2 Runner work."""

from __future__ import annotations

import contextlib
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING, Any

from rdetoolkit.core.context import RunContext
from rdetoolkit.errors import ERROR_CATALOG, RdeExecutionError
from rdetoolkit.report.events import EventSink
from rdetoolkit.runner.execute import ExecutionResult, TileExecutionError
from rdetoolkit.runner.invoker import FlowInvoker, TargetInvoker


if TYPE_CHECKING:
    from rdetoolkit.runner.planner import ExecutionPlan, TilePlan


_RUN_INTERRUPTED_CODE = 3004


class TileExecutor:
    """Execute planned tiles through the invoker registered for their target."""

    def __init__(
        self,
        *,
        event_sink: EventSink,
        flow_invoker: TargetInvoker | None = None,
    ) -> None:
        """Create a tile executor.

        Args:
            event_sink: Sink receiving node events from the eager execution core.
            flow_invoker: Optional flow adapter used by tests or alternate hosts.
        """
        self._event_sink = event_sink
        self._flow_invoker = flow_invoker or FlowInvoker()

    def execute(self, plan: ExecutionPlan, tile: TilePlan) -> ExecutionResult:
        """Execute one tile and normalize ordinary failures into a result.

        Args:
            plan: Immutable run execution plan.
            tile: Per-tile paths, iteration data, and invoice preparation.

        Returns:
            Completed or failed primary execution result.
        """
        invoice = tile.invoice
        try:
            invoice = tile.prepare_invoice() if tile.prepare_invoice is not None else tile.invoice
            context = RunContext(
                paths=tile.paths,
                out=tile.out,
                config=plan.config,
                invoice=invoice,
                iteration=tile.iteration,
            )
            return _with_legacy_metadata(
                self._flow_invoker.invoke(
                    plan.target,
                    context,
                    event_sink=self._event_sink,
                    run_id=plan.run_id,
                    config=plan.config,
                ),
                invoice=invoice,
                rawfiles=tile.paths.rawfiles,
                root=plan.root,
            )
        except Exception as exc:  # noqa: BLE001
            if _is_run_interrupted(exc):
                raise
            if isinstance(exc, TileExecutionError):
                return _with_legacy_metadata(
                    exc.result,
                    invoice=invoice,
                    rawfiles=tile.paths.rawfiles,
                    root=plan.root,
                )
            result = ExecutionResult(
                iteration_index=tile.iteration.index,
                status="failed",
                call_records=(),
                outputs=(),
                error=_execution_error(exc),
                datatile_id=_datatile_id(tile.paths.rawfiles, tile.iteration.index),
            )
            return _with_legacy_metadata(
                result,
                invoice=invoice,
                rawfiles=tile.paths.rawfiles,
                root=plan.root,
            )


def _is_run_interrupted(exc: Exception) -> bool:
    return isinstance(exc, RdeExecutionError) and exc.code == _RUN_INTERRUPTED_CODE


def _execution_error(exc: Exception) -> dict[str, Any]:
    code = getattr(exc, "code", 3001)
    error_def = ERROR_CATALOG.get(code) if isinstance(code, int) else None
    return {
        "code": code,
        "name": getattr(exc, "name", error_def.name if error_def is not None else type(exc).__name__),
        "message": getattr(exc, "message", str(exc)),
        **({"remediation": error_def.remediation} if error_def is not None else {}),
    }


def _datatile_id(rawfiles: tuple[Path, ...], iteration_index: int) -> str:
    return rawfiles[0].stem if rawfiles else str(iteration_index)


def _with_legacy_metadata(
    result: ExecutionResult,
    *,
    invoice: Any,
    rawfiles: tuple[Path, ...],
    root: Path,
) -> ExecutionResult:
    """Attach compatibility inputs while they are available at the tile boundary."""
    title = result.datatile_id
    if invoice is not None:
        basic = invoice.raw.get("basic")
        if isinstance(basic, dict) and isinstance(basic.get("dataName"), str):
            title = basic["dataName"]
    target = _legacy_target(rawfiles, root=root)
    return replace(result, title=title, target=target)


def _legacy_target(rawfiles: tuple[Path, ...], *, root: Path) -> str | None:
    if not rawfiles:
        return None
    basedir = rawfiles[0].parent
    with contextlib.suppress(ValueError):
        basedir = basedir.relative_to(root)
    return basedir.as_posix()
