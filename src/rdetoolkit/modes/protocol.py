"""Narrow contract for mode-owned execution planning."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from rdetoolkit.domain.invoice_service import InvoiceService
    from rdetoolkit.runner.mode_resolver import ModeKind
    from rdetoolkit.runner.planner import TilePlan


@dataclass(frozen=True, slots=True)
class PlanningContext:
    """Explicit run material available to a mode handler.

    Args:
        root: Project or flat data root for the run.
        inputdata_path: Directory containing run inputs.
        unpacked_dir_path: Directory used for unpacked inputs.
        invoice_service: Run-owned invoice operations used while creating tiles.
    """

    root: Path
    inputdata_path: Path
    unpacked_dir_path: Path
    invoice_service: InvoiceService


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
