from collections.abc import Callable
from pathlib import Path
from typing import Any

from rdetoolkit.report.run_report import RunReport
from rdetoolkit.types import OutputContext

def run_flow(flow_fn_or_template: Callable[..., Any], fixture_dir: Path) -> RunReport: ...
def assert_output_tree(out: OutputContext, golden_dir: Path) -> None: ...
