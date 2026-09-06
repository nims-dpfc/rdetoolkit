from collections.abc import Iterable

from rdetoolkit.modes.protocol import PlanningContext
from rdetoolkit.runner.mode_resolver import ModeKind
from rdetoolkit.runner.planner import TilePlan

class SmartTableModeHandler:
    kind: ModeKind
    def create_tiles(self, context: PlanningContext) -> Iterable[TilePlan]: ...
