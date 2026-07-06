from collections.abc import Callable
from pathlib import Path
from typing import Any

from rdetoolkit.report.events import EventSink
from rdetoolkit.report.run_report import RunReport
from rdetoolkit.runner.mode_resolver import ModeKind
from rdetoolkit.types import RdeConfig

class Runner:
    root: Path
    inputdata_path: Path
    unpacked_dir_path: Path
    event_sink: EventSink
    run_id: str
    def __init__(
        self,
        *,
        root: Path | None = None,
        inputdata_path: Path | None = None,
        unpacked_dir_path: Path | None = None,
        event_sink: EventSink | None = None,
        run_id_factory: Callable[[], str] | None = None,
    ) -> None: ...
    def run(self, flow_fn: Callable[..., Any], **overrides: Any) -> RunReport: ...
    def load_config(self, overrides: dict[str, Any] | None = None) -> RdeConfig: ...
    def resolve_mode(self, config: RdeConfig) -> ModeKind: ...
    def pre_validate(self, config: RdeConfig) -> None: ...
    def iterate(self, flow_fn: Callable[..., Any], mode: ModeKind, config: RdeConfig) -> RunReport: ...
    def post_validate(self, config: RdeConfig, report: RunReport) -> None: ...
    def finalize(self, report: RunReport, config: RdeConfig) -> None: ...
