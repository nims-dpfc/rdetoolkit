"""Lazy execution planning for the v2 Runner."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from functools import partial
from itertools import chain
from pathlib import Path
from typing import Literal

from rdetoolkit.api.request import ExecutionTarget, RunRequest
from rdetoolkit.domain.invoice_service import InvoiceService
from rdetoolkit.modes.protocol import PlanningContext
from rdetoolkit.modes.registry import handler_for
from rdetoolkit.runner.iterator import iterate_tiles
from rdetoolkit.runner.mode_resolver import ModeKind
from rdetoolkit.types import InputPaths, InvoiceData, IterationInfo, OutputContext, RdeConfig


@dataclass(frozen=True, slots=True)
class TilePlan:
    """Immutable execution material for one tile."""

    iteration: IterationInfo
    paths: InputPaths
    out: OutputContext
    invoice: InvoiceData | None
    prepare_invoice: Callable[[], InvoiceData | None] | None = None


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    """Immutable run plan with lazily produced tile plans."""

    run_id: str
    target: ExecutionTarget
    mode: ModeKind
    config: RdeConfig
    root: Path
    error_policy: Literal["continue", "fail_fast"]
    tiles: Iterable[TilePlan]


@dataclass(slots=True)
class _InvoiceSourceState:
    path: Path
    prepared: bool


PathProvider = Path | Callable[[], Path]


class RunPlanner:
    """Convert a normalized request into one lazy common execution plan."""

    def __init__(
        self,
        *,
        inputdata_path: PathProvider,
        unpacked_dir_path: PathProvider,
        run_id_factory: Callable[[], str],
        invoice_service: InvoiceService | None = None,
    ) -> None:
        """Create a planner.

        Args:
            inputdata_path: Current input directory or a lazy path provider.
            unpacked_dir_path: Current unpack directory or a lazy path provider.
            run_id_factory: Provider for the active Runner run identifier.
            invoice_service: Run-owned path-based invoice operations.
        """
        self._inputdata_path = inputdata_path
        self._unpacked_dir_path = unpacked_dir_path
        self._run_id_factory = run_id_factory
        self._invoice_service = invoice_service or InvoiceService()

    def create(
        self,
        request: RunRequest,
        *,
        config: RdeConfig,
        mode: ModeKind,
    ) -> ExecutionPlan:
        """Create an execution plan without eagerly enumerating tiles.

        Args:
            request: Normalized run request.
            config: Effective canonical configuration.
            mode: Resolved internal mode.

        Returns:
            Frozen plan whose ``tiles`` iterable performs existing tile discovery lazily.
        """
        context = PlanningContext(
            root=request.root,
            inputdata_path=_resolve_path(self._inputdata_path),
            unpacked_dir_path=_resolve_path(self._unpacked_dir_path),
            invoice_service=self._invoice_service,
            config=config,
        )
        self._invoice_service.begin_run(request.root)
        handler = handler_for(mode)
        tiles: Iterable[TilePlan] = (
            create_common_tiles(mode, context) if handler is None else handler.create_tiles(context)
        )
        return ExecutionPlan(
            run_id=self._run_id_factory(),
            target=request.target,
            mode=mode,
            config=config,
            root=request.root,
            error_policy=config.execution.on_iteration_error,
            tiles=tiles,
        )


def create_common_tiles(mode: ModeKind, context: PlanningContext) -> Iterator[TilePlan]:
    """Enumerate the common tile plans for one mode.

    This is the single tile-construction body shared by the planner fallback
    and the thin mode handlers installed in Session I5. Mode-specific
    behavior belongs in the handlers themselves (Session I6), not here.

    Args:
        mode: Resolved internal mode.
        context: Run-scoped paths and invoice operations.

    Yields:
        One immutable ``TilePlan`` per discovered tile.
    """
    root = context.root
    inputdata_path = context.inputdata_path
    invoice_service = context.invoice_service
    # Resolve the run data root once, before any tile directory exists. An
    # alias-flat root gains a ``data`` child as soon as tile 0 is created, so a
    # later resolution would silently switch roots mid-run.
    data_root = _data_root(root)
    invariant_invoice = _invariant_invoice(mode, root=data_root, invoice_service=invoice_service)
    invoice_org = data_root / "invoice" / "invoice.json"
    source = _InvoiceSourceState(path=invoice_org, prepared=mode is not ModeKind.excelinvoice)
    tiles = iter(
        iterate_tiles(
            mode,
            inputdata_path,
            context.unpacked_dir_path,
            root / "data",
            context.config,
        ),
    )
    # v1 backs the invoice up AFTER check_files (workflows.py), so
    # data/temp/invoice_org.json does not exist while an input checker scans
    # the unpack directory. Pulling the first tile forces the checker's parse
    # (including unpacking) to finish first, which keeps the backup out of the
    # RDEFormat checker's data/temp/** glob.
    first = next(tiles, None)
    if mode in {ModeKind.multidatatile, ModeKind.rdeformat}:
        source.path = _run_invoice_source(
            mode,
            root=data_root,
            inputdata_path=inputdata_path,
            invoice_service=invoice_service,
        )
    if first is None:
        return
    for info, paths, out in chain((first,), tiles):
        yield TilePlan(
            iteration=info,
            paths=paths,
            out=out,
            invoice=None,
            prepare_invoice=partial(
                _prepare_tile_invoice,
                mode,
                root=data_root,
                inputdata_path=inputdata_path,
                paths=paths,
                invoice_dir=out.invoice,
                iteration_index=info.index,
                invariant_invoice=invariant_invoice,
                source=source,
                invoice_service=invoice_service,
            ),
        )


def _prepare_tile_invoice(
    mode: ModeKind,
    *,
    root: Path,
    inputdata_path: Path,
    paths: InputPaths,
    invoice_dir: Path,
    iteration_index: int,
    invariant_invoice: InvoiceData | None,
    source: _InvoiceSourceState,
    invoice_service: InvoiceService,
) -> InvoiceData | None:
    if not source.prepared:
        source.path = _run_invoice_source(
            mode,
            root=root,
            inputdata_path=inputdata_path,
            rawfiles=paths.rawfiles,
            invoice_service=invoice_service,
        )
        source.prepared = True
    return _tile_invoice(
        mode,
        root=root,
        paths=paths,
        invoice_dir=invoice_dir,
        iteration_index=iteration_index,
        invariant_invoice=invariant_invoice,
        invoice_org=source.path,
        invoice_service=invoice_service,
    )


def _invariant_invoice(
    mode: ModeKind,
    *,
    root: Path,
    invoice_service: InvoiceService | None = None,
) -> InvoiceData | None:
    return (invoice_service or InvoiceService()).invariant_invoice(mode, root=root)


def _tile_invoice(
    mode: ModeKind,
    *,
    root: Path,
    paths: InputPaths,
    invoice_dir: Path,
    iteration_index: int,
    invariant_invoice: InvoiceData | None,
    invoice_org: Path,
    invoice_service: InvoiceService | None = None,
) -> InvoiceData | None:
    _ = root
    return (invoice_service or InvoiceService()).prepare_tile(
        mode,
        paths=paths,
        invoice_dir=invoice_dir,
        iteration_index=iteration_index,
        invariant_invoice=invariant_invoice,
        invoice_source=invoice_org,
    )


def _run_invoice_source(
    mode: ModeKind,
    *,
    root: Path,
    inputdata_path: Path,
    rawfiles: tuple[Path, ...] = (),
    invoice_service: InvoiceService | None = None,
) -> Path:
    """Return the v1-compatible run-level invoice source for a backup mode."""
    return (invoice_service or InvoiceService()).backup(
        mode,
        root=root,
        inputdata_path=inputdata_path,
        rawfiles=rawfiles,
    )


def _flat_layout_invoice_source(*, invoice_org: Path) -> Path:
    """Compatibility wrapper for the former flat-layout helper."""
    return InvoiceService().backup(
        ModeKind.rdeformat,
        root=invoice_org.parent.parent,
        inputdata_path=invoice_org.parent.parent / "inputdata",
    )


def _data_root(root: Path) -> Path:
    candidate = root / "data"
    if (candidate / "inputdata").exists() or (candidate / "invoice").exists() or (candidate / "tasksupport").exists():
        return candidate
    return root


def _resolve_path(provider: PathProvider) -> Path:
    return provider() if callable(provider) else provider
