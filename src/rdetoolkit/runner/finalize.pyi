from pathlib import Path

from rdetoolkit.report.run_report import RunReport
from rdetoolkit.types import RdeConfig

def finalize(report: RunReport, config: RdeConfig, *, root: Path) -> None: ...
