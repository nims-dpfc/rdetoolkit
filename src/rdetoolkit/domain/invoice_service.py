"""Run-owned, path-based invoice operations shared by all modes."""

from __future__ import annotations

import shutil
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

from rdetoolkit.domain.invoice import (
    build_excelinvoice_tile_invoice,
    build_smarttable_tile_invoice,
    load_invoice,
)
from rdetoolkit.domain.service_errors import validation_error
from rdetoolkit.invoicefile import apply_magic_variable
from rdetoolkit.processing.processors.invoice import SmartTableInvoiceInitializer
from rdetoolkit.types import InputPaths, InvoiceData, RdeConfig

if TYPE_CHECKING:
    from rdetoolkit.runner.mode_resolver import ModeKind


class InvoiceService:
    """Own run-scoped invoice preparation with explicit filesystem paths."""

    def __init__(self) -> None:
        """Create a stateless invoice service using explicit filesystem paths."""

    def begin_run(self, root: Path) -> None:
        """Invalidate only this run's SmartTable base-invoice cache entry.

        The retained v1 initializer still owns its class cache until Phase I.
        Targeted invalidation avoids the former process-wide clear that could
        evict a concurrently executing run rooted elsewhere. ``pop`` is
        idempotent, so the Runner and Planner may both call this per run.

        Args:
            root: Project or flat data root for the run.
        """
        key = (_data_root(root) / "invoice" / "invoice.json").resolve()
        SmartTableInvoiceInitializer._BASE_INVOICE_CACHE.pop(key, None)  # noqa: SLF001 -- Phase I removes the retained v1 cache

    def backup(
        self,
        mode: ModeKind,
        *,
        root: Path,
        inputdata_path: Path,
        rawfiles: tuple[Path, ...] = (),
    ) -> Path:
        """Return the run-level invoice source, backing it up when required.

        Args:
            mode: Effective Runner mode.
            root: Explicit run root.
            inputdata_path: Explicit input directory used for Excel discovery.
            rawfiles: Current tile inputs, if already known.

        Returns:
            Original or backed-up invoice path.
        """
        data_root = _data_root(root)
        invoice_source = data_root / "invoice" / "invoice.json"
        _ = inputdata_path, rawfiles
        if _mode_value(mode) not in {"excelinvoice", "multidatatile", "rdeformat"}:
            return invoice_source
        if not invoice_source.exists():
            return invoice_source
        backup_path = data_root / "temp" / "invoice_org.json"
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(invoice_source, backup_path)
        return backup_path

    def prepare_tile(
        self,
        mode: ModeKind,
        *,
        paths: InputPaths,
        invoice_dir: Path,
        iteration_index: int,
        invariant_invoice: InvoiceData | None,
        invoice_source: Path,
    ) -> InvoiceData | None:
        """Prepare one tile invoice without a legacy mode processor.

        Args:
            mode: Effective Runner mode.
            paths: Explicit input paths for the tile.
            invoice_dir: Explicit destination invoice directory.
            iteration_index: Zero-based tile index.
            invariant_invoice: Preloaded invoice shared by invariant modes.
            invoice_source: Run-level source or backup invoice.

        Returns:
            Prepared tile invoice data, or None when the mode has no builder.
        """
        destination = invoice_dir / "invoice.json"
        if invariant_invoice is not None:
            _copy_invoice(invoice_source, destination)
            return invariant_invoice
        mode_value = _mode_value(mode)
        schema = paths.tasksupport / "invoice.schema.json"
        if mode_value == "excelinvoice":
            candidates = (*paths.rawfiles, *_directory_files(paths.inputdata))
            return build_excelinvoice_tile_invoice(
                excel_path=_first_matching(candidates, suffixes=(".xlsx", ".xlsm", ".xls")),
                invoice_org=invoice_source,
                invoice_schema_path=schema,
                dist_path=destination,
                idx=iteration_index,
            )
        if mode_value == "smarttable":
            return build_smarttable_tile_invoice(
                smarttable_rowfile=_first_matching(paths.rawfiles, prefixes=("fsmarttable_",), suffixes=(".csv",)),
                invoice_org=invoice_source,
                invoice_schema_path=schema,
                dist_path=destination,
                rawfiles=paths.rawfiles,
            )
        return None

    def invariant_invoice(self, mode: ModeKind, *, root: Path) -> InvoiceData | None:
        """Load the invariant invoice for modes that share one source.

        Args:
            mode: Effective Runner mode.
            root: Explicit run root.

        Returns:
            Loaded invoice or None for per-tile invoice modes.
        """
        data_root = _data_root(root)
        invoice_path = data_root / "invoice" / "invoice.json"
        mode_value = _mode_value(mode)
        if mode_value == "invoice":
            inputdata = data_root / "inputdata"
            if not invoice_path.exists() and inputdata.exists() and not tuple(sorted(inputdata.iterdir())):
                return None
            return load_invoice(invoice_path)
        if mode_value in {"multidatatile", "rdeformat"} and invoice_path.exists():
            return load_invoice(invoice_path)
        return None

    def apply_config(
        self,
        *,
        config: RdeConfig,
        invoice_path: Path,
        structured_dir: Path,
        rawfiles: tuple[Path, ...],
        feature_updater: Callable[[], None] | None = None,
    ) -> None:
        """Apply the three canonical invoice artifact configuration flags.

        Args:
            config: Canonical run configuration.
            invoice_path: Tile invoice to update or persist.
            structured_dir: Structured artifact destination.
            rawfiles: Tile inputs used for magic-variable replacement.
            feature_updater: Optional description update operation.
        """
        if config.system.magic_variable and rawfiles:
            apply_magic_variable(
                invoice_path,
                rawfiles[0],
                save_filepath=invoice_path,
            )
        if config.system.save_invoice_to_structured:
            structured_dir.mkdir(parents=True, exist_ok=True)
            destination = structured_dir / "invoice.json"
            if invoice_path.resolve() != destination.resolve():
                shutil.copy2(invoice_path, destination)
        if config.system.feature_description and feature_updater is not None:
            try:
                feature_updater()
            except Exception:  # noqa: BLE001
                return


def _data_root(root: Path) -> Path:
    candidate = root / "data"
    if any((candidate / name).exists() for name in ("inputdata", "invoice", "tasksupport")):
        return candidate
    return root


def _directory_files(directory: Path) -> tuple[Path, ...]:
    return tuple(sorted(directory.iterdir())) if directory.exists() else ()


def _first_matching(
    paths: tuple[Path, ...],
    *,
    suffixes: tuple[str, ...],
    prefixes: tuple[str, ...] = (),
) -> Path:
    ordered = tuple(sorted(paths))
    for path in ordered:
        if path.suffix.lower() in suffixes and (not prefixes or path.name.startswith(prefixes)):
            return path
    for path in ordered:
        if path.suffix.lower() in suffixes:
            return path
    message = f"No input file matched suffixes {suffixes}"
    raise validation_error(4003, message)


def _copy_invoice(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != destination.resolve():
        shutil.copy2(source, destination)


def _mode_value(mode: Any) -> str:
    value = getattr(mode, "value", mode)
    return str(value)
