"""Explicit installation of the built-in mode handlers.

Registration is a function call, never an import side effect: importing a mode
module must leave the registry untouched so the planner fallback stays
reachable and tests can start from an empty registry.
"""

from __future__ import annotations

from rdetoolkit.modes.excelinvoice import ExcelInvoiceModeHandler
from rdetoolkit.modes.invoice import InvoiceModeHandler
from rdetoolkit.modes.multidatatile import MultiDataTileModeHandler
from rdetoolkit.modes.protocol import ModeHandler
from rdetoolkit.modes.rdeformat import RdeFormatModeHandler
from rdetoolkit.modes.registry import register
from rdetoolkit.modes.smarttable import SmartTableModeHandler


def install_default_handlers() -> None:
    """Register every built-in mode handler.

    The Runner calls this while it is constructed. Calling it again is
    idempotent because each handler replaces its own registry entry.
    """
    handlers: tuple[ModeHandler, ...] = (
        InvoiceModeHandler(),
        ExcelInvoiceModeHandler(),
        MultiDataTileModeHandler(),
        RdeFormatModeHandler(),
        SmartTableModeHandler(),
    )
    for handler in handlers:
        register(handler.kind, handler)
