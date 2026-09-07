"""Run-owned, path-based invoice operations shared by all modes."""

from __future__ import annotations

import contextlib
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

from rdetoolkit.domain.invoice import (
    build_excelinvoice_tile_invoice,
    build_smarttable_tile_invoice,
    clear_tile_row_data,
    load_invoice,
    smarttable_invoice_builder,
)
from rdetoolkit.domain.service_errors import validation_error
from rdetoolkit.invoicefile import apply_magic_variable, update_description_with_features
from rdetoolkit.models.rde2types import RdeDatasetPaths, RdeInputDirPaths, RdeOutputResourcePath
from rdetoolkit.types import InputPaths, InvoiceData, RdeConfig

if TYPE_CHECKING:
    from rdetoolkit.runner.mode_resolver import ModeKind


class InvoiceService:
    """Own run-scoped invoice preparation with explicit filesystem paths."""

    def __init__(self) -> None:
        """Create an invoice service owning this run's SmartTable material."""
        self._smarttable_builder = smarttable_invoice_builder()

    def begin_run(self, root: Path) -> None:
        """Release the SmartTable material of any previously executed run.

        The base invoice is owned by this service's builder rather than by a
        process-global cache keyed by path (Session I6-C): two runs over one
        root can no longer observe each other's source invoice, and a service
        reused for a second run always re-reads it.

        Args:
            root: Project or flat data root for the run.
        """
        self._smarttable_builder.reset()
        clear_tile_row_data(_data_root(root))

    def end_run(self, root: Path) -> None:
        """Release this run's retained SmartTable material.

        Runs are bounded, so the row-data handoff and the base invoice snapshot
        are released here as well as at ``begin_run``: a long-lived process
        that executes many runs never accumulates the material of the runs it
        already finished.

        Args:
            root: Project or flat data root for the run.
        """
        self._smarttable_builder.reset()
        clear_tile_row_data(_data_root(root))

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
                data_root=paths.invoice.parent,
                builder=self._smarttable_builder,
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
        dataset_paths: RdeDatasetPaths,
        steps: frozenset[str] | None = None,
        feature_updater: Callable[[], None] | None = None,
    ) -> None:
        """Apply the three canonical invoice artifact configuration flags.

        The step order and the copy source are ported from the v1 invoice
        pipeline (``processing/factories.py``: StructuredInvoiceSaver ->
        VariableApplier -> DescriptionUpdater). The structured copy takes
        ``invoice_org`` — the run-level source invoice — exactly like v1's
        ``StructuredInvoiceSaver``; copying the tile invoice instead would
        publish magic-variable substitutions v1 never writes there.

        The three steps touch disjoint state (``structured/invoice.json``, the
        tile invoice's ``basic.dataName`` and its ``basic.description``), which
        is why the MultiDataTile/ExcelInvoice pipelines can interleave them
        differently without changing any observable artifact.

        The whole v1 dataset bundle is required — not just a few paths —
        because ``apply_magic_variable`` resolves ``${invoice:...}`` from
        ``dataset_paths.invoice_org`` and ``${metadata:...}`` from the tile's
        ``meta/metadata.json``, exactly as v1's ``VariableApplier`` does.

        Args:
            config: Canonical run configuration.
            dataset_paths: v1 dataset bundle for the tile being finalized.
            steps: Steps this mode runs (``structured`` / ``magic`` /
                ``description``). ``None`` runs all three, which is the v1
                invoice, MultiDataTile, ExcelInvoice and SmartTable behavior.
            feature_updater: Optional replacement for the description update.

        Raises:
            FileNotFoundError: If the structured copy is enabled but the source
                invoice is missing (v1 ``StructuredInvoiceSaver`` behavior).
        """
        resource = dataset_paths.output_paths
        invoice_path = resource.invoice / "invoice.json"
        if _step_enabled(steps, INVOICE_STEP_STRUCTURED) and config.system.save_invoice_to_structured:
            self._save_structured_invoice(resource.invoice_org, resource.struct)
        if _step_enabled(steps, INVOICE_STEP_MAGIC) and config.system.magic_variable and resource.rawfiles:
            apply_magic_variable(
                invoice_path,
                resource.rawfiles[0],
                save_filepath=invoice_path,
                dataset_paths=dataset_paths,
            )
        if _step_enabled(steps, INVOICE_STEP_DESCRIPTION) and config.system.feature_description:
            updater = feature_updater or build_description_updater(dataset_paths)
            # v1's DescriptionUpdater suppresses every failure because the
            # description transfer is optional enrichment, not an artifact.
            with contextlib.suppress(Exception):
                updater()

    @staticmethod
    def _save_structured_invoice(invoice_org: Path, structured_dir: Path) -> None:
        if not invoice_org.exists():
            msg = f"Original invoice not found for structured export: {invoice_org}"
            raise FileNotFoundError(msg)
        structured_dir.mkdir(parents=True, exist_ok=True)
        destination = structured_dir / "invoice.json"
        if invoice_org.resolve() != destination.resolve():
            shutil.copy2(invoice_org, destination)


def resolve_invoice_source(root: Path) -> Path:
    """Return the run-level ``invoice_org`` source for a run root.

    The v1 ``backup_invoice_json_files`` contract is: modes that back the
    original invoice up read ``data/temp/invoice_org.json``, every other mode
    reads ``data/invoice/invoice.json``. The backup's presence — not a mode
    branch — therefore selects the source, and the source is run-level, so
    divided tiles share the tile-0 backup exactly as v1 does.

    Args:
        root: Project or flat data root for the run.

    Returns:
        Path of the run-level source invoice.
    """
    data_root = _data_root(root)
    backup = data_root / "temp" / "invoice_org.json"
    return backup if backup.exists() else data_root / "invoice" / "invoice.json"


def build_tile_dataset_paths(
    *,
    paths: InputPaths,
    out: Any,
    invoice_org: Path,
) -> RdeDatasetPaths:
    """Build the v1 dataset bundle for one tile's invoice artifact stage.

    ``RdeDatasetPaths`` is a v1 primitive (``models.rde2types``) that the v1
    invoice helpers consume directly, so the domain layer constructs it here
    rather than importing the ``compat`` adapter. ``RdeInputDirPaths.config``
    keeps its v1 default: none of the invoice steps reads it.

    Args:
        paths: Runner input paths for the tile.
        out: Runner output context for the tile.
        invoice_org: Run-level source invoice.

    Returns:
        The v1 bundle expected by ``apply_magic_variable`` and
        ``update_description_with_features``.
    """
    resource = RdeOutputResourcePath(
        raw=out.raw,
        nonshared_raw=out.nonshared_raw,
        rawfiles=paths.rawfiles,
        struct=out.struct,
        main_image=out.main_image,
        other_image=out.other_image,
        meta=out.meta,
        thumbnail=out.thumbnail,
        logs=out.logs,
        invoice=out.invoice,
        invoice_schema_json=paths.tasksupport / "invoice.schema.json",
        invoice_org=invoice_org,
        attachment=out.attachment,
    )
    return RdeDatasetPaths(
        input_paths=RdeInputDirPaths(
            inputdata=paths.inputdata,
            invoice=paths.invoice,
            tasksupport=paths.tasksupport,
        ),
        output_paths=resource,
    )


def build_description_updater(dataset_paths: RdeDatasetPaths) -> Callable[[], None]:
    """Build the v1 feature-description update operation for one tile.

    Args:
        dataset_paths: v1 dataset bundle for the tile.

    Returns:
        Callable performing the v1 ``update_description_with_features`` call.
    """

    def _update() -> None:
        update_description_with_features(
            dataset_paths.output_paths,
            dataset_paths.output_paths.invoice / "invoice.json",
            dataset_paths.tasksupport / "metadata-def.json",
        )

    return _update


#: Canonical names of the three invoice artifact steps a mode may select.
INVOICE_STEP_STRUCTURED = "structured"
INVOICE_STEP_MAGIC = "magic"
INVOICE_STEP_DESCRIPTION = "description"
INVOICE_STEPS = frozenset({INVOICE_STEP_STRUCTURED, INVOICE_STEP_MAGIC, INVOICE_STEP_DESCRIPTION})


def _step_enabled(steps: frozenset[str] | None, step: str) -> bool:
    return steps is None or step in steps


_RDE_MARKERS = ("inputdata", "invoice", "tasksupport")


def _data_root(root: Path) -> Path:
    """Resolve the directory that owns this run's invoice inputs.

    A root that *directly* holds the RDE marker directories is the data root,
    even once tile creation adds a ``data`` child below it. Resolving the
    ``data`` child first would make the answer depend on when it is asked:
    the invoice source would silently move from ``<root>/invoice`` to
    ``<root>/data/invoice`` in the middle of a run over an alias-flat root.
    """
    if any((root / name).exists() for name in _RDE_MARKERS):
        return root
    candidate = root / "data"
    if any((candidate / name).exists() for name in _RDE_MARKERS):
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
