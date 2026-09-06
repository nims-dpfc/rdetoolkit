from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from rdetoolkit.api.request import ExecutionTarget, RunRequest
from rdetoolkit.domain.invoice_service import InvoiceService
from rdetoolkit.modes.protocol import PlanningContext
from rdetoolkit.runner.mode_resolver import ModeKind
from rdetoolkit.types import InputPaths, InvoiceData, IterationInfo, OutputContext, RdeConfig

@dataclass(frozen=True, slots=True)
class TilePlan:
    iteration: IterationInfo
    paths: InputPaths
    out: OutputContext
    invoice: InvoiceData | None
    prepare_invoice: Callable[[], InvoiceData | None] | None = ...

@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    run_id: str
    target: ExecutionTarget
    mode: ModeKind
    config: RdeConfig
    root: Path
    error_policy: Literal["continue", "fail_fast"]
    tiles: Iterable[TilePlan]

PathProvider = Path | Callable[[], Path]

class RunPlanner:
    def __init__(
        self,
        *,
        inputdata_path: PathProvider,
        unpacked_dir_path: PathProvider,
        run_id_factory: Callable[[], str],
        invoice_service: InvoiceService | None = ...,
    ) -> None: ...
    def create(
        self,
        request: RunRequest,
        *,
        config: RdeConfig,
        mode: ModeKind,
    ) -> ExecutionPlan: ...

def create_common_tiles(mode: ModeKind, context: PlanningContext) -> Iterator[TilePlan]: ...
