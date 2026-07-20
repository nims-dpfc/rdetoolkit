"""Common tile execution for planned v2 Runner work."""

from __future__ import annotations

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
        try:
            invoice = tile.prepare_invoice() if tile.prepare_invoice is not None else tile.invoice
            context = RunContext(
                paths=tile.paths,
                out=tile.out,
                config=plan.config,
                invoice=invoice,
                iteration=tile.iteration,
            )
            return self._flow_invoker.invoke(
                plan.target,
                context,
                event_sink=self._event_sink,
                run_id=plan.run_id,
                config=plan.config,
            )
        except Exception as exc:  # noqa: BLE001
            if _is_run_interrupted(exc):
                raise
            if isinstance(exc, TileExecutionError):
                return exc.result
            return ExecutionResult(
                iteration_index=tile.iteration.index,
                status="failed",
                call_records=(),
                outputs=(),
                error=_execution_error(exc),
                datatile_id=_datatile_id(tile.paths.rawfiles, tile.iteration.index),
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
