"""ExcelInvoice-mode planning handler for the unified Runner."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from rdetoolkit.runner.mode_resolver import ModeKind
from rdetoolkit.runner.planner import create_common_tiles

if TYPE_CHECKING:
    from rdetoolkit.modes.protocol import PlanningContext, RawCopyStrategy
    from rdetoolkit.runner.planner import ExecutionPlan, TilePlan


class ExcelInvoiceModeHandler:
    """Plan ExcelInvoice-mode tiles.

    Session I5 keeps this adapter deliberately thin: it owns the mode identity
    and nothing else, so the planned tiles stay identical to the pre-handler
    Runner. Empty-row and missing-row compatibility arrives in Session I6.
    """

    kind = ModeKind.excelinvoice

    def create_tiles(self, context: PlanningContext) -> Iterable[TilePlan]:
        """Create ExcelInvoice-mode tile plans.

        Args:
            context: Run-scoped paths and invoice operations.

        Returns:
            Lazily iterable common tile plans for the executor.
        """
        return create_common_tiles(self.kind, context)

    def raw_copy_strategy(self, plan: ExecutionPlan) -> RawCopyStrategy | None:
        """Return no mode-specific raw copy strategy.

        Args:
            plan: Immutable run execution plan.

        Returns:
            ``None``, selecting the generic ``RawArtifactService``.
        """
        _ = plan
        return None

    def invoice_stage_steps(self, plan: ExecutionPlan) -> frozenset[str] | None:
        """Run every invoice artifact step, as the v1 pipeline for this mode does.

        Args:
            plan: Immutable run execution plan.

        Returns:
            ``None``, selecting structured, magic variable, and description.
        """
        _ = plan
        return None
