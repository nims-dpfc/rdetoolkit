from typing import Protocol

from rdetoolkit.api.request import ExecutionTarget
from rdetoolkit.core.context import RunContext
from rdetoolkit.report.events import EventSink
from rdetoolkit.runner.execute import ExecutionResult
from rdetoolkit.types import RdeConfig

class TargetInvoker(Protocol):
    def invoke(
        self,
        target: ExecutionTarget,
        context: RunContext,
        *,
        event_sink: EventSink,
        run_id: str,
        config: RdeConfig,
    ) -> ExecutionResult: ...

class FlowInvoker:
    def invoke(
        self,
        target: ExecutionTarget,
        context: RunContext,
        *,
        event_sink: EventSink,
        run_id: str,
        config: RdeConfig,
    ) -> ExecutionResult: ...

class InvokerRegistry:
    def __init__(
        self,
        *,
        flow_invoker: TargetInvoker | None = ...,
        legacy_invoker: TargetInvoker | None = ...,
    ) -> None: ...
    def for_target(self, target: ExecutionTarget) -> TargetInvoker: ...
    def invoke(
        self,
        target: ExecutionTarget,
        context: RunContext,
        *,
        event_sink: EventSink,
        run_id: str,
        config: RdeConfig,
    ) -> ExecutionResult: ...
