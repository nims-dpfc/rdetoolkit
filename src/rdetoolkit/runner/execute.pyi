from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal

from rdetoolkit.core.calllog import NodeCallRecord, TypeSummary
from rdetoolkit.core.context import RunContext
from rdetoolkit.report.events import EventSink
from rdetoolkit.types import RdeConfig

@dataclass(frozen=True, slots=True)
class ExecutionResult:
    iteration_index: int
    status: Literal["completed", "failed"]
    call_records: tuple[NodeCallRecord, ...]
    outputs: tuple[TypeSummary, ...]
    error: dict[str, Any] | None = ...

def run_tile(
    flow_fn: Callable[..., Any],
    run_context: RunContext,
    *,
    event_sink: EventSink,
    run_id: str,
    config: RdeConfig,
) -> ExecutionResult: ...
