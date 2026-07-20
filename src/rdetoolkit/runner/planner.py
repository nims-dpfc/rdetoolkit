"""Lazy execution planning for the v2 Runner."""

from __future__ import annotations

import shutil
from collections.abc import Callable, Iterable, Iterator
from contextlib import chdir
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Literal

from rdetoolkit.api.request import ExecutionTarget, RunRequest
from rdetoolkit.domain.invoice import (
    build_excelinvoice_tile_invoice,
    build_smarttable_tile_invoice,
    load_invoice,
)
from rdetoolkit.invoicefile import backup_invoice_json_files
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
    ) -> None:
        """Create a planner.

        Args:
            inputdata_path: Current input directory or a lazy path provider.
            unpacked_dir_path: Current unpack directory or a lazy path provider.
            run_id_factory: Provider for the active Runner run identifier.
        """
        self._inputdata_path = inputdata_path
        self._unpacked_dir_path = unpacked_dir_path
        self._run_id_factory = run_id_factory

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
        inputdata_path = _resolve_path(self._inputdata_path)
        unpacked_dir_path = _resolve_path(self._unpacked_dir_path)
        return ExecutionPlan(
            run_id=self._run_id_factory(),
            target=request.target,
            mode=mode,
            config=config,
            root=request.root,
            error_policy=config.execution.on_iteration_error,
            tiles=self._create_tiles(
                mode,
                root=request.root,
                inputdata_path=inputdata_path,
                unpacked_dir_path=unpacked_dir_path,
            ),
        )

    def _create_tiles(
        self,
        mode: ModeKind,
        *,
        root: Path,
        inputdata_path: Path,
        unpacked_dir_path: Path,
    ) -> Iterator[TilePlan]:
        invariant_invoice = _invariant_invoice(mode, root=root)
        invoice_org = _data_root(root) / "invoice" / "invoice.json"
        source = _InvoiceSourceState(path=invoice_org, prepared=mode is not ModeKind.excelinvoice)
        if mode in {ModeKind.multidatatile, ModeKind.rdeformat}:
            source.path = _run_invoice_source(mode, root=root, inputdata_path=inputdata_path)
        for info, paths, out in iterate_tiles(
            mode,
            inputdata_path,
            unpacked_dir_path,
            root / "data",
        ):
            yield TilePlan(
                iteration=info,
                paths=paths,
                out=out,
                invoice=None,
                prepare_invoice=partial(
                    _prepare_tile_invoice,
                    mode,
                    root=root,
                    inputdata_path=inputdata_path,
                    paths=paths,
                    invoice_dir=out.invoice,
                    iteration_index=info.index,
                    invariant_invoice=invariant_invoice,
                    source=source,
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
) -> InvoiceData | None:
    if not source.prepared:
        source.path = _run_invoice_source(
            mode,
            root=root,
            inputdata_path=inputdata_path,
            rawfiles=paths.rawfiles,
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
    )


def _invariant_invoice(mode: ModeKind, *, root: Path) -> InvoiceData | None:
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
    paths: InputPaths,
    invoice_dir: Path,
    iteration_index: int,
    invariant_invoice: InvoiceData | None,
    invoice_org: Path,
) -> InvoiceData | None:
    _ = root
    invoice_schema_path = paths.tasksupport / "invoice.schema.json"
    dist_path = invoice_dir / "invoice.json"
    if invariant_invoice is not None:
        _copy_invoice(invoice_org, dist_path)
        return invariant_invoice
    if mode is ModeKind.excelinvoice:
        inputdata_path = paths.inputdata
        input_candidates = tuple(sorted(inputdata_path.iterdir())) if inputdata_path.exists() else ()
        excel_candidates = (*paths.rawfiles, *input_candidates)
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


def _copy_invoice(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != destination.resolve():
        shutil.copy2(source, destination)


def _run_invoice_source(
    mode: ModeKind,
    *,
    root: Path,
    inputdata_path: Path,
    rawfiles: tuple[Path, ...] = (),
) -> Path:
    """Return the v1-compatible run-level invoice source for a backup mode."""
    data_root = _data_root(root)
    invoice_org = data_root / "invoice" / "invoice.json"
    excel_path: Path | None = None
    if mode is ModeKind.excelinvoice and data_root != root:
        input_candidates = tuple(sorted(inputdata_path.iterdir())) if inputdata_path.exists() else ()
        candidates = (*rawfiles, *input_candidates)
        excel_path = _first_matching(candidates, suffixes=(".xlsx", ".xlsm", ".xls"))
    if data_root == root:
        return _flat_layout_invoice_source(invoice_org=invoice_org)
    with chdir(root):
        return backup_invoice_json_files(excel_path, _legacy_backup_mode(mode))


def _flat_layout_invoice_source(*, invoice_org: Path) -> Path:
    """Preserve the test/public flat-root layout unsupported by the v1 helper."""
    if not invoice_org.exists():
        return invoice_org
    backup_path = invoice_org.parent.parent / "temp" / "invoice_org.json"
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(invoice_org, backup_path)
    return backup_path


def _legacy_backup_mode(mode: ModeKind) -> str | None:
    if mode is ModeKind.multidatatile:
        return "MultiDataTile"
    if mode is ModeKind.rdeformat:
        return "rdeformat"
    return None


def _first_matching(
    paths: tuple[Path, ...],
    *,
    prefixes: tuple[str, ...] = (),
    suffixes: tuple[str, ...],
) -> Path:
    ordered = tuple(sorted(paths))
    for path in ordered:
        if path.suffix.lower() in suffixes and (not prefixes or path.name.startswith(prefixes)):
            return path
    for path in ordered:
        if path.suffix.lower() in suffixes:
            return path
    msg = f"No input file matched suffixes {suffixes}"
    raise FileNotFoundError(msg)


def _data_root(root: Path) -> Path:
    candidate = root / "data"
    if (candidate / "inputdata").exists() or (candidate / "invoice").exists() or (candidate / "tasksupport").exists():
        return candidate
    return root


def _resolve_path(provider: PathProvider) -> Path:
    return provider() if callable(provider) else provider
