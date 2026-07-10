"""Runner lifecycle skeleton for rdetoolkit v2."""

from __future__ import annotations

import hashlib
import time
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any

from rdetoolkit.errors import ERROR_CATALOG, RdeValidationError
from rdetoolkit.exceptions import InvoiceSchemaValidationError, MetadataValidationError
from rdetoolkit.report.events import EventSink, MemoryEventSink
from rdetoolkit.report.run_report import RunReport
from rdetoolkit.runner.finalize import finalize as _finalize_run
from rdetoolkit.runner.config_loader import load_config as load_config_from_root
from rdetoolkit.runner.execute import run_tile
from rdetoolkit.runner.iterator import iterate_tiles
from rdetoolkit.runner.mode_resolver import ModeKind, resolve_mode as resolve_mode_from_paths
from rdetoolkit.core.context import RunContext
from rdetoolkit.types import RdeConfig


class Runner:
    """Execute the v2 Runner lifecycle without flow dispatch.

    Phase B1 owns the six-step lifecycle skeleton. Actual flow execution and
    dependency injection are later phases, so ``iterate`` is intentionally a
    replaceable stub.
    """

    def __init__(
        self,
        *,
        root: Path | None = None,
        inputdata_path: Path | None = None,
        unpacked_dir_path: Path | None = None,
        event_sink: EventSink | None = None,
        run_id_factory: Callable[[], str] | None = None,
    ) -> None:
        """Create a Runner.

        Args:
            root: Project or data root used for config loading.
            inputdata_path: Input data directory for mode resolution.
            unpacked_dir_path: Legacy unpack directory for input checkers.
            event_sink: Event sink owned by this run.
            run_id_factory: Optional factory for deterministic tests.
        """
        self.root = root or Path.cwd()
        self.inputdata_path = inputdata_path or self.root / "inputdata"
        self.unpacked_dir_path = unpacked_dir_path or self.root / "unpacked"
        self.event_sink = event_sink or MemoryEventSink()
        self._run_id_factory = run_id_factory or (lambda: uuid.uuid4().hex)
        self.run_id = ""

    def run(self, flow_fn: Callable[..., Any], **overrides: Any) -> RunReport:
        """Execute the six Runner lifecycle steps in Design §6.1 order.

        Args:
            flow_fn: Flow function placeholder for later phases.
            **overrides: Config values merged over file configuration.

        Returns:
            Run report produced by ``iterate`` and finalized by this Runner.
        """
        self.run_id = self._run_id_factory()
        self.event_sink.open(self.run_id)
        try:
            config = self.load_config(overrides)
            mode = self.resolve_mode(config)
            self.pre_validate(config)
            report = self.iterate(flow_fn, mode, config)
            self.post_validate(config, report)
            self.finalize(report, config)
            return report
        finally:
            self.event_sink.close()

    def load_config(self, overrides: dict[str, Any] | None = None) -> RdeConfig:
        """Load the effective v2 Runner config.

        Args:
            overrides: Values merged over file configuration.

        Returns:
            Effective configuration.
        """
        return load_config_from_root(self.root, overrides=overrides)

    def resolve_mode(self, config: RdeConfig) -> ModeKind:
        """Resolve the effective mode for this run.

        Args:
            config: Effective configuration.

        Returns:
            Effective internal mode.
        """
        return resolve_mode_from_paths(
            config,
            self.inputdata_path,
            self.unpacked_dir_path,
            self.event_sink,
            self.run_id,
        )

    def pre_validate(self, config: RdeConfig) -> None:
        """Run pre-flow domain validation hooks.

        B1 wires the method and preserves the validation error contract. Concrete
        invoice and metadata paths are supplied by later path-resolution phases.

        Args:
            config: Effective configuration.
        """
        _ = config

    def iterate(
        self,
        flow_fn: Callable[..., Any],
        mode: ModeKind,
        config: RdeConfig,
    ) -> RunReport:
        """Execute the flow once per tile and return a minimal run report.

        Args:
            flow_fn: Flow function placeholder.
            mode: Effective mode.
            config: Effective configuration.

        Returns:
            Minimal successful run report.
        """
        started = time.time()
        iterations: list[dict[str, Any]] = []
        for info, paths, out in iterate_tiles(
            mode,
            self.inputdata_path,
            self.unpacked_dir_path,
            Path("data"),
        ):
            result = run_tile(
                flow_fn,
                RunContext(paths=paths, out=out, config=config, invoice=None, iteration=info),
                event_sink=self.event_sink,
                run_id=self.run_id,
                config=config,
            )
            iterations.append(
                {
                    "iteration_index": result.iteration_index,
                    "status": result.status,
                    "call_count": len(result.call_records),
                    "output_count": len(result.outputs),
                },
            )
        return RunReport(
            run_id=self.run_id,
            status="success",
            flow_id=_flow_id(flow_fn),
            mode=mode.value,
            started_at=_iso_timestamp(started),
            duration_ms=(time.time() - started) * 1000.0,
            config_digest=_config_digest(config),
            iterations=iterations,
            warnings=[],
        )

    def post_validate(self, config: RdeConfig, report: RunReport) -> None:
        """Run post-flow domain validation hooks.

        Args:
            config: Effective configuration.
            report: Report produced by iteration.
        """
        _ = (config, report)

    def finalize(self, report: RunReport, config: RdeConfig) -> None:
        """Finalize the report and job failure contract (Design §6.1 step 6, §6.3).

        Persists the RunReport JSON and, for failed runs, writes ``data/job.failed``
        through the v1 contract. This is the production path; tests may still
        replace this step through the injectable-step seam.

        Args:
            report: Report produced by iteration.
            config: Effective configuration.
        """
        _finalize_run(report, config)


def _flow_id(flow_fn: Callable[..., Any]) -> str:
    module = getattr(flow_fn, "__module__", "")
    qualname = getattr(flow_fn, "__qualname__", getattr(flow_fn, "__name__", repr(flow_fn)))
    return f"{module}.{qualname}" if module else qualname


def _config_digest(config: RdeConfig) -> str:
    encoded = config.model_dump_json().encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _iso_timestamp(timestamp: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(timestamp))


def _validation_error(code: int, reason: str) -> RdeValidationError:
    error_def = ERROR_CATALOG[code]
    error_cls: Any = RdeValidationError
    return error_cls(
        code=code,
        name=error_def.name,
        message=error_def.message_template.format(reason=reason),
    )


def _wrap_domain_validation_error(exc: Exception) -> RdeValidationError:
    if isinstance(exc, InvoiceSchemaValidationError):
        return _validation_error(4001, str(exc))
    if isinstance(exc, MetadataValidationError):
        return _validation_error(4002, str(exc))
    return _validation_error(4003, str(exc))
