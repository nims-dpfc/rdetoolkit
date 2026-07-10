"""Runner lifecycle skeleton for rdetoolkit v2."""

from __future__ import annotations

import hashlib
import sys
import time
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any

from rdetoolkit.errors import ERROR_CATALOG, RdeConfigError, RdeError, RdeValidationError
from rdetoolkit.exceptions import InvoiceSchemaValidationError, MetadataValidationError
from rdetoolkit.invoicefile import backup_invoice_json_files
from rdetoolkit.report.events import Event, EventSink, MemoryEventSink
from rdetoolkit.report.run_report import RunReport
from rdetoolkit.runner.finalize import finalize as _finalize_run
from rdetoolkit.runner.aggregator import RunAggregator
from rdetoolkit.runner.config_loader import load_config as load_config_from_root
from rdetoolkit.runner.execute import ExecutionResult, TileExecutionError
from rdetoolkit.runner.execute import run_tile
from rdetoolkit.runner.iterator import iterate_tiles
from rdetoolkit.runner.mode_resolver import ModeKind, resolve_mode as resolve_mode_from_paths
from rdetoolkit.core.context import RunContext
from rdetoolkit.domain.invoice import (
    build_excelinvoice_tile_invoice,
    build_smarttable_tile_invoice,
    load_invoice,
)
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
        started = time.time()
        config: RdeConfig | None = None
        mode: ModeKind | None = None
        report: RunReport | None = None
        try:
            self.event_sink.emit(Event.run_started(run_id=self.run_id))
            config = self.load_config(overrides)
            mode = self.resolve_mode(config)
            self.pre_validate(config)
            report = self.iterate(flow_fn, mode, config)
            self.post_validate(config, report)
            self.finalize(report, config)
            return report
        except Exception as exc:  # noqa: BLE001
            effective_config = config or RdeConfig()
            error = _lifecycle_error(exc)
            report = RunReport(
                run_id=self.run_id,
                status="failed",
                flow_id=_flow_id(flow_fn),
                mode=mode.value if mode is not None else "unknown",
                started_at=_iso_timestamp(started),
                duration_ms=(time.time() - started) * 1000.0,
                config_digest=_config_digest(effective_config),
                iterations=[],
                warnings=[],
                error=_exception_error(error),
            )
            self.finalize(report, effective_config)
            return report
        finally:
            if report is not None:
                self.event_sink.emit(Event.run_completed(run_id=self.run_id, status=report.status))
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
        aggregator = RunAggregator(
            run_id=self.run_id,
            flow_id=_flow_id(flow_fn),
            mode=mode.value,
            config_digest=_config_digest(config),
            logs_dir=Path("data") / "logs",
        )
        failed_count = 0
        completed_count = 0
        terminal_error: dict[str, Any] | None = None
        invariant_invoice = _invariant_invoice(mode, root=self.root)
        invoice_org = _data_root(self.root) / "invoice" / "invoice.json"
        invoice_source_prepared = mode is not ModeKind.excelinvoice
        for info, paths, out in iterate_tiles(
            mode,
            self.inputdata_path,
            self.unpacked_dir_path,
            Path("data"),
        ):
            iteration_status = "failed"
            self.event_sink.emit(Event.iteration_started(run_id=self.run_id, index=info.index))
            try:
                if not invoice_source_prepared:
                    invoice_org = _run_invoice_source(
                        mode,
                        root=self.root,
                        inputdata_path=self.inputdata_path,
                        rawfiles=paths.rawfiles,
                    )
                    invoice_source_prepared = True
                result = run_tile(
                    flow_fn,
                    RunContext(
                        paths=paths,
                        out=out,
                        config=config,
                        invoice=_tile_invoice(
                            mode,
                            root=self.root,
                            paths=paths,
                            invoice_dir=out.invoice,
                            iteration_index=info.index,
                            invariant_invoice=invariant_invoice,
                            invoice_org=invoice_org,
                        ),
                        iteration=info,
                    ),
                    event_sink=self.event_sink,
                    run_id=self.run_id,
                    config=config,
                    emit_iteration_events=False,
                )
                iteration_status = "completed"
            except Exception as exc:  # noqa: BLE001
                failed_count += 1
                failed_result = (
                    exc.result
                    if isinstance(exc, TileExecutionError)
                    else ExecutionResult(
                        iteration_index=info.index,
                        status="failed",
                        call_records=(),
                        outputs=(),
                        error=_exception_error(exc),
                        datatile_id=_datatile_id(paths.rawfiles, info.index),
                    )
                )
                error = failed_result.error or _exception_error(exc)
                terminal_error = error
                aggregator.record(failed_result)
                if config.execution.on_iteration_error == "fail_fast":
                    break
                continue
            finally:
                self.event_sink.emit(
                    Event(
                        run_id=self.run_id,
                        name="iteration.completed",
                        payload={"iteration_index": info.index, "status": iteration_status},
                    ),
                )
            completed_count += 1
            aggregator.record(result)
        status = _run_status(
            completed_count=completed_count,
            failed_count=failed_count,
            fail_fast=config.execution.on_iteration_error == "fail_fast",
        )
        warnings = _failure_warnings(failed_count) if failed_count else []
        if failed_count:
            sys.stderr.write(f"{failed_count} iteration(s) failed\n")
        return aggregator.build_report(
            status=status,
            started_at=_iso_timestamp(started),
            duration_ms=(time.time() - started) * 1000.0,
            warnings=warnings,
            error=terminal_error if status == "failed" else None,
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


def _exception_error(exc: Exception) -> dict[str, Any]:
    code = getattr(exc, "code", 3001)
    error_def = ERROR_CATALOG.get(code) if isinstance(code, int) else None
    error: dict[str, Any] = {
        "code": code,
        "name": getattr(exc, "name", error_def.name if error_def is not None else type(exc).__name__),
        "message": getattr(exc, "message", str(exc)),
    }
    if error_def is not None:
        error["remediation"] = error_def.remediation
    return error


def _lifecycle_error(exc: Exception) -> RdeError:
    if isinstance(exc, RdeError):
        return exc
    error_def = ERROR_CATALOG[1002]
    message = error_def.message_template.format(reason=str(exc))
    message = f"{message} Remediation: {error_def.remediation}"
    error_cls: Any = RdeConfigError
    return error_cls(
        code=1002,
        name=error_def.name,
        message=message,
    )


def _run_status(*, completed_count: int, failed_count: int, fail_fast: bool = False) -> str:
    """Classify the run outcome (Design §7.2).

    Under fail_fast, any tile failure aborts the run, so the run as a whole is
    "failed" even when earlier tiles completed — "partial" exists only for the
    continue policy (no implicit partial success).
    """
    if failed_count == 0:
        return "success"
    if fail_fast or completed_count == 0:
        return "failed"
    return "partial"


def _datatile_id(rawfiles: tuple[Path, ...], iteration_index: int) -> str:
    """Return the first raw-file stem, falling back to the decimal tile index."""
    return rawfiles[0].stem if rawfiles else str(iteration_index)


def _failure_warnings(failed_count: int) -> list[dict[str, Any]]:
    return [
        {
            "code": 3001,
            "message": f"{failed_count} iteration(s) failed",
            "failed_count": failed_count,
        },
    ]


def _invariant_invoice(mode: ModeKind, *, root: Path) -> Any:
    data_root = _data_root(root)
    invoice_path = data_root / "invoice" / "invoice.json"
    if mode is ModeKind.invoice:
        inputdata_path = data_root / "inputdata"
        if not invoice_path.exists() and inputdata_path.exists() and not any(inputdata_path.iterdir()):
            return None
        return load_invoice(invoice_path)
    if mode in {ModeKind.multidatatile, ModeKind.rdeformat} and invoice_path.exists():
        return load_invoice(invoice_path)
    return None


def _tile_invoice(
    mode: ModeKind,
    *,
    root: Path,
    paths: Any,
    invoice_dir: Path,
    iteration_index: int,
    invariant_invoice: Any,
    invoice_org: Path,
) -> Any:
    if invariant_invoice is not None:
        return invariant_invoice
    data_root = _data_root(root)
    invoice_schema_path = data_root / "tasksupport" / "invoice.schema.json"
    dist_path = invoice_dir / "invoice.json"
    if mode is ModeKind.excelinvoice:
        inputdata_path = data_root / "inputdata"
        excel_candidates = (*paths.rawfiles, *tuple(inputdata_path.iterdir() if inputdata_path.exists() else ()))
        return build_excelinvoice_tile_invoice(
            excel_path=_first_matching(excel_candidates, suffixes=(".xlsx", ".xlsm", ".xls")),
            invoice_org=invoice_org,
            invoice_schema_path=invoice_schema_path,
            dist_path=dist_path,
            idx=iteration_index,
        )
    if mode is ModeKind.smarttable:
        return build_smarttable_tile_invoice(
            smarttable_rowfile=_first_matching(paths.rawfiles, prefixes=("fsmarttable_",), suffixes=(".csv",)),
            invoice_org=invoice_org,
            invoice_schema_path=invoice_schema_path,
            dist_path=dist_path,
            rawfiles=paths.rawfiles,
        )
    return None


def _run_invoice_source(
    mode: ModeKind,
    *,
    root: Path,
    inputdata_path: Path,
    rawfiles: tuple[Path, ...] = (),
) -> Path:
    """Return the run-level source invoice, using the v1 Excel backup once."""
    invoice_org = _data_root(root) / "invoice" / "invoice.json"
    if mode is not ModeKind.excelinvoice:
        return invoice_org
    input_candidates = tuple(inputdata_path.iterdir()) if inputdata_path.exists() else ()
    candidates = (*rawfiles, *input_candidates)
    excel_path = _first_matching(candidates, suffixes=(".xlsx", ".xlsm", ".xls"))
    return backup_invoice_json_files(excel_path, None)


def _first_matching(
    paths: tuple[Path, ...],
    *,
    prefixes: tuple[str, ...] = (),
    suffixes: tuple[str, ...],
) -> Path:
    for path in paths:
        if path.suffix.lower() not in suffixes:
            continue
        if prefixes and not path.name.startswith(prefixes):
            continue
        return path
    for path in paths:
        if path.suffix.lower() in suffixes:
            return path
    msg = f"No input file matched suffixes {suffixes}"
    raise FileNotFoundError(msg)


def _data_root(root: Path) -> Path:
    candidate = root / "data"
    if (candidate / "inputdata").exists() or (candidate / "invoice").exists() or (candidate / "tasksupport").exists():
        return candidate
    return root


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
