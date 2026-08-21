from collections.abc import Callable
from pathlib import Path

from rdetoolkit.report.run_report import RunReport
from rdetoolkit.types import RdeConfig

class RunFinalizer:
    def __init__(self, *, root: Path | Callable[[], Path]) -> None: ...
    def finalize(self, report: RunReport, config: RdeConfig) -> None: ...

def finalize(report: RunReport, config: RdeConfig, *, root: Path) -> None: ...
