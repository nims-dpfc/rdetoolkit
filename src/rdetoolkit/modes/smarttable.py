"""SmartTable-mode planning handler for the unified Runner."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from rdetoolkit.runner.mode_resolver import ModeKind
from rdetoolkit.runner.planner import create_common_tiles

if TYPE_CHECKING:
    from rdetoolkit.modes.protocol import PlanningContext
    from rdetoolkit.runner.planner import TilePlan


class SmartTableModeHandler:
    """Plan SmartTable-mode tiles.

    Session I5 keeps this adapter deliberately thin: it owns the mode identity
    and nothing else, so the planned tiles stay identical to the pre-handler
    Runner. SmartTable-specific settings arrive in Session I6.
    """

    kind = ModeKind.smarttable

    def create_tiles(self, context: PlanningContext) -> Iterable[TilePlan]:
        """Create SmartTable-mode tile plans.

        Args:
            context: Run-scoped paths and invoice operations.

        Returns:
            Lazily iterable common tile plans for the executor.
        """
        return create_common_tiles(self.kind, context)
