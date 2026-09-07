from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from rdetoolkit.domain.invoice_service import InvoiceService
from rdetoolkit.runner.mode_resolver import ModeKind
from rdetoolkit.runner.planner import ExecutionPlan, TilePlan
from rdetoolkit.types import RdeConfig

@dataclass(frozen=True, slots=True)
class PlanningContext:
    root: Path
    inputdata_path: Path
    unpacked_dir_path: Path
    invoice_service: InvoiceService
    config: RdeConfig | None = ...

class RawCopyStrategy(Protocol):
    def copy(
        self,
        source_files: tuple[Path, ...],
        *,
        raw_dir: Path,
        nonshared_raw_dir: Path,
        config: RdeConfig,
        smarttable: bool = ...,
    ) -> None: ...

class ModeHandler(Protocol):
    kind: ModeKind
    def create_tiles(self, context: PlanningContext) -> Iterable[TilePlan]: ...
    def raw_copy_strategy(self, plan: ExecutionPlan) -> RawCopyStrategy | None: ...
    def invoice_stage_steps(self, plan: ExecutionPlan) -> frozenset[str] | None: ...
