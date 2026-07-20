from rdetoolkit.report.events import EventSink
from rdetoolkit.runner.execute import ExecutionResult
from rdetoolkit.runner.invoker import TargetInvoker
from rdetoolkit.runner.planner import ExecutionPlan, TilePlan

class TileExecutor:
    def __init__(
        self,
        *,
        event_sink: EventSink,
        flow_invoker: TargetInvoker | None = None,
    ) -> None: ...
    def execute(self, plan: ExecutionPlan, tile: TilePlan) -> ExecutionResult: ...
