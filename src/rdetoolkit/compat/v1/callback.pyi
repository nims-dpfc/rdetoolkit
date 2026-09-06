from collections.abc import Callable
from typing import Any

from rdetoolkit.api.request import ExecutionTarget
from rdetoolkit.core.context import RunContext
from rdetoolkit.models.rde2types import RdeDatasetPaths
from rdetoolkit.report.events import EventSink
from rdetoolkit.runner.execute import ExecutionResult
from rdetoolkit.types import RdeConfig

def accepts_unified_argument(callback: Callable[..., Any]) -> bool | None: ...
def to_legacy_dataset_paths(context: RunContext) -> RdeDatasetPaths: ...

class LegacyCallbackInvoker:
    def invoke(
        self,
        target: ExecutionTarget,
        context: RunContext,
        *,
        event_sink: EventSink,
        run_id: str,
        config: RdeConfig,
    ) -> ExecutionResult: ...
