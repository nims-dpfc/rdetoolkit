"""Common tile execution for planned v2 Runner work."""

from __future__ import annotations

import contextlib
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING, Any

from rdetoolkit.core.context import RunContext
from rdetoolkit.domain.artifacts import ImageArtifactService, RawArtifactService
from rdetoolkit.errors import ERROR_CATALOG, RdeExecutionError
from rdetoolkit.report.events import EventSink
from rdetoolkit.runner.execute import ExecutionResult, TileExecutionError
from rdetoolkit.runner.finalize import structured_error_record
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
        raw_artifact_service: RawArtifactService | None = None,
        image_artifact_service: ImageArtifactService | None = None,
    ) -> None:
        """Create a tile executor.

        Args:
            event_sink: Sink receiving node events from the eager execution core.
            flow_invoker: Optional flow adapter used by tests or alternate hosts.
            raw_artifact_service: Optional completed-tile raw publisher.
            image_artifact_service: Optional completed-tile image publisher.
        """
        self._event_sink = event_sink
        self._flow_invoker = flow_invoker or FlowInvoker()
        self._raw_artifact_service = raw_artifact_service
        self._image_artifact_service = image_artifact_service

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
            result = _with_legacy_metadata(
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
            if result.status == "completed":
                self._publish_artifacts(plan, tile)
            return result
        except Exception as exc:  # noqa: BLE001
            if _is_run_interrupted(exc):
                raise
            if isinstance(exc, TileExecutionError):
                return _with_legacy_metadata(
                    _with_user_error(exc.result, exc.__cause__),
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

    def _publish_artifacts(self, plan: ExecutionPlan, tile: TilePlan) -> None:
        """Invoke injected artifact services after successful tile execution."""
        if self._raw_artifact_service is not None:
            self._raw_artifact_service.copy(
                tile.paths.rawfiles,
                raw_dir=tile.out.raw,
                nonshared_raw_dir=tile.out.nonshared_raw,
                config=plan.config,
                smarttable=plan.mode.value == "smarttable",
            )
        if self._image_artifact_service is not None:
            self._image_artifact_service.generate(
                main_image_dir=tile.out.main_image,
                thumbnail_dir=tile.out.thumbnail,
                config=plan.config,
            )


def _is_run_interrupted(exc: Exception) -> bool:
    return isinstance(exc, RdeExecutionError) and exc.code == _RUN_INTERRUPTED_CODE


#: Fields the passthrough record owns. ``remediation`` is included because it
#: is derived from the catalog code being replaced, so keeping the wrapper's
#: 3001 remediation would describe an error the run no longer reports.
_PASSTHROUGH_OWNED_KEYS = frozenset({"code", "name", "message", "remediation"})


def _with_user_error(result: ExecutionResult, cause: BaseException | None) -> ExecutionResult:
    """Restore a ``StructuredError``'s ``ecode``/``emsg`` on a wrapped result.

    ``run_tile`` catalogues every flow failure as 3001 before raising, so the
    raised code would otherwise be lost at the tile boundary. Only the
    catalogued fields are replaced: recorder context such as ``call_id`` stays
    on the record so the failing call remains identifiable.
    """
    passthrough = structured_error_record(cause)
    if passthrough is None:
        return result
    preserved = {key: value for key, value in (result.error or {}).items() if key not in _PASSTHROUGH_OWNED_KEYS}
    return replace(result, error={**preserved, **passthrough})


def _execution_error(exc: Exception) -> dict[str, Any]:
    # A StructuredError carries ecode/emsg, not code/message (Design §6.3).
    passthrough = structured_error_record(exc)
    if passthrough is not None:
        return passthrough
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
