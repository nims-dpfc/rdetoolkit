"""Single-tile eager flow execution for the v2 Runner."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal, cast

from rdetoolkit.core.calllog import CallLogRecorder, NodeCallRecord, TypeSummary
from rdetoolkit.core.context import RunContext, get_reserved_mapping
from rdetoolkit.core.injection import resolve_flow_kwargs
from rdetoolkit.report.events import Event, EventSink
from rdetoolkit.types import RdeConfig


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    """Result of one eager flow execution for a single tile."""

    iteration_index: int
    status: Literal["completed", "failed"]
    call_records: tuple[NodeCallRecord, ...]
    outputs: tuple[TypeSummary, ...]
    error: dict[str, Any] | None = None


def run_tile(
    flow_fn: Callable[..., Any],
    run_context: RunContext,
    *,
    event_sink: EventSink,
    run_id: str,
    config: RdeConfig,
) -> ExecutionResult:
    """Execute one tile by injecting reserved values and calling the flow eagerly.

    Args:
        flow_fn: Flow function to execute.
        run_context: Per-tile reserved values.
        event_sink: Sink receiving iteration lifecycle events.
        run_id: Current run identifier.
        config: Effective Runner configuration.

    Returns:
        Completed tile execution result.
    """
    if run_context.iteration is None:
        msg = "RunContext.iteration is required for tile execution."
        raise ValueError(msg)

    iteration_index = run_context.iteration.index
    kwargs = resolve_flow_kwargs(_flow_for_di(flow_fn), run_context)
    event_sink.emit(Event.iteration_started(run_id=run_id, index=iteration_index))
    recorder = CallLogRecorder(
        repr_head=config.provenance.repr_head,
        repr_head_len=config.provenance.repr_head_len,
        type_check=cast("Literal['off', 'warn', 'strict']", config.execution.type_check),
        iteration_index=iteration_index,
    )
    with recorder:
        result = flow_fn(**kwargs)
    outputs = _summarize_outputs(
        result,
        repr_head=config.provenance.repr_head,
        repr_head_len=config.provenance.repr_head_len,
    )
    event_sink.emit(Event.iteration_completed(run_id=run_id, index=iteration_index))
    return ExecutionResult(
        iteration_index=iteration_index,
        status="completed",
        call_records=recorder.records,
        outputs=outputs,
        error=None,
    )


def _summarize_outputs(value: Any, *, repr_head: str, repr_head_len: int) -> tuple[TypeSummary, ...]:
    if value is None:
        return ()
    if isinstance(value, tuple):
        return tuple(_summarize(item, repr_head=repr_head, repr_head_len=repr_head_len) for item in value)
    return (_summarize(value, repr_head=repr_head, repr_head_len=repr_head_len),)


def _summarize(value: Any, *, repr_head: str, repr_head_len: int) -> TypeSummary:
    return TypeSummary(
        type_name=_type_name(value),
        repr_head=_safe_repr_head(value, enabled=repr_head == "on", length=repr_head_len),
    )


def _type_name(value: Any) -> str:
    target = type(value)
    if target is type(None):
        return "None"
    if target.__module__ == "builtins":
        return target.__qualname__
    return f"{target.__module__}.{target.__qualname__}"


def _safe_repr_head(value: Any, *, enabled: bool, length: int) -> str | None:
    if not enabled:
        return None
    try:
        return repr(value)[:length]
    except Exception:  # noqa: BLE001
        return None


def _flow_for_di(flow_fn: Callable[..., Any]) -> Callable[..., Any]:
    signature = inspect.signature(flow_fn)
    reserved_by_name = {reserved_type.__name__: reserved_type for reserved_type in get_reserved_mapping().values()}
    parameters: list[inspect.Parameter] = []
    changed = False
    for parameter in signature.parameters.values():
        annotation = parameter.annotation
        if isinstance(annotation, str) and annotation in reserved_by_name:
            annotation = reserved_by_name[annotation]
            changed = True
        parameters.append(parameter.replace(annotation=annotation))

    if not changed:
        return flow_fn

    resolved_signature = signature.replace(parameters=parameters)
    flow_fn.__signature__ = resolved_signature  # type: ignore[attr-defined]
    flow_fn.__annotations__ = {
        parameter.name: parameter.annotation
        for parameter in parameters
        if parameter.annotation is not inspect.Signature.empty
    }
    if signature.return_annotation is not inspect.Signature.empty:
        flow_fn.__annotations__["return"] = signature.return_annotation
    return flow_fn
