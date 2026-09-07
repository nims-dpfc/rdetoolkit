"""Narrow contract for mode-owned execution planning."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from rdetoolkit.domain.invoice_service import InvoiceService
    from rdetoolkit.runner.mode_resolver import ModeKind
    from rdetoolkit.runner.planner import ExecutionPlan, TilePlan
    from rdetoolkit.types import RdeConfig


@dataclass(frozen=True, slots=True)
class PlanningContext:
    """Explicit run material available to a mode handler.

    Args:
        root: Project or flat data root for the run.
        inputdata_path: Directory containing run inputs.
        unpacked_dir_path: Directory used for unpacked inputs.
        invoice_service: Run-owned invoice operations used while creating tiles.
        config: Effective run configuration consumed by legacy input checkers.
    """

    root: Path
    inputdata_path: Path
    unpacked_dir_path: Path
    invoice_service: InvoiceService
    config: RdeConfig | None = None


class RawCopyStrategy(Protocol):
    """Publish one tile's raw inputs.

    ``RawArtifactService`` is the generic implementation; a mode installs its
    own strategy when v1 copies raw files by a different rule (RDEFormat
    dispatches by path component, for example).
    """

    def copy(
        self,
        source_files: tuple[Path, ...],
        *,
        raw_dir: Path,
        nonshared_raw_dir: Path,
        config: RdeConfig,
        smarttable: bool = False,
    ) -> None:
        """Copy the configured raw artifacts for one tile."""
        ...


class ModeHandler(Protocol):
    """Create common tile plans for one resolved Runner mode."""

    kind: ModeKind

    def create_tiles(self, context: PlanningContext) -> Iterable[TilePlan]:
        """Create tile plans from explicit planning material.

        Args:
            context: Run-scoped paths and invoice operations.

        Returns:
            Lazily iterable common tile plans for the executor.
        """
        ...

    def raw_copy_strategy(self, plan: ExecutionPlan) -> RawCopyStrategy | None:
        """Return the mode-specific raw copy strategy, if any.

        This member is optional: the executor uses ``getattr`` so a handler
        that never customizes raw publication does not have to declare it.
        Returning ``None`` selects the generic ``RawArtifactService``.

        Args:
            plan: Immutable run execution plan.

        Returns:
            Mode-owned strategy, or ``None`` for the generic service.
        """
        ...

    def invoice_stage_steps(self, plan: ExecutionPlan) -> frozenset[str] | None:
        """Return the invoice artifact steps this mode runs.

        Optional, like ``raw_copy_strategy``. ``None`` runs all three steps
        (``structured`` / ``magic`` / ``description``), which matches the v1
        invoice, MultiDataTile, ExcelInvoice and SmartTable pipelines. A mode
        whose v1 pipeline omits a processor — RDEFormat has neither
        ``StructuredInvoiceSaver`` nor ``VariableApplier`` — returns the subset
        it actually runs.

        Args:
            plan: Immutable run execution plan.

        Returns:
            Selected step names, or ``None`` for the full v1 invoice stage.
        """
        ...
