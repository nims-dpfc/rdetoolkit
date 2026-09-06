from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from rdetoolkit.domain.invoice_service import InvoiceService
from rdetoolkit.runner.mode_resolver import ModeKind
from rdetoolkit.runner.planner import TilePlan

@dataclass(frozen=True, slots=True)
class PlanningContext:
    root: Path
    inputdata_path: Path
    unpacked_dir_path: Path
    invoice_service: InvoiceService

class ModeHandler(Protocol):
    kind: ModeKind
    def create_tiles(self, context: PlanningContext) -> Iterable[TilePlan]: ...
