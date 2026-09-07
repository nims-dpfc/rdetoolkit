"""Invoice-mode artifact seams stay generic (Session I6-A).

Invoice is the reference mode: its v1 pipeline
(``processing/factories.py::InvoicePipelineBuilder``) uses the plain
``FileCopier`` and runs the complete invoice stage, so both Session I6-1 seams
must keep resolving to their generic defaults. Session I6-A adds RDEFormat's
overrides next door, and these tests pin the invariant that adding a
mode-specific strategy for one mode does not leak into another.

EP table:
| TC | Class | Input | Expected |
|----|-------|-------|----------|
| TC-I6-A-EP-020 | raw seam | ``InvoiceModeHandler.raw_copy_strategy`` | ``None`` (generic ``RawArtifactService``) |
| TC-I6-A-EP-021 | invoice seam | ``InvoiceModeHandler.invoice_stage_steps`` | ``None`` (all three v1 steps) |

BV / negative table:
| TC | Class | Input | Expected |
|----|-------|-------|----------|
| TC-I6-A-EV-022 | isolation | the four non-RDEFormat built-in handlers | every ``raw_copy_strategy`` is ``None`` |
| TC-I6-A-EV-023 | isolation | the four non-RDEFormat built-in handlers | every ``invoice_stage_steps`` is ``None`` |
| TC-I6-A-EV-024 | statelessness | two consecutive seam queries | the answer does not depend on call order |
"""

from __future__ import annotations

import pytest

from rdetoolkit.modes.excelinvoice import ExcelInvoiceModeHandler
from rdetoolkit.modes.invoice import InvoiceModeHandler
from rdetoolkit.modes.multidatatile import MultiDataTileModeHandler
from rdetoolkit.modes.smarttable import SmartTableModeHandler

_GENERIC_HANDLERS = (
    InvoiceModeHandler,
    ExcelInvoiceModeHandler,
    MultiDataTileModeHandler,
    SmartTableModeHandler,
)


def test_invoice_keeps_the_generic_raw_service__tc_i6_a_ep_020() -> None:
    """TC-I6-A-EP-020: invoice mode publishes raw through RawArtifactService."""
    # Given: the production invoice handler
    handler = InvoiceModeHandler()

    # When: the executor asks for a mode-specific raw strategy
    strategy = handler.raw_copy_strategy(None)  # type: ignore[arg-type]

    # Then: none is installed, so the generic service stays in charge
    assert strategy is None


def test_invoice_runs_the_full_invoice_stage__tc_i6_a_ep_021() -> None:
    """TC-I6-A-EP-021: invoice mode runs structured, magic and description."""
    # Given: the production invoice handler
    handler = InvoiceModeHandler()

    # When: the executor asks which invoice artifact steps this mode runs
    steps = handler.invoice_stage_steps(None)  # type: ignore[arg-type]

    # Then: ``None`` selects the complete v1 invoice stage
    assert steps is None


@pytest.mark.parametrize(
    "handler_type",
    [pytest.param(handler_type, id=handler_type.__name__) for handler_type in _GENERIC_HANDLERS],
)
def test_non_rdeformat_handlers_keep_the_generic_raw_service__tc_i6_a_ev_022(
    handler_type: type,
) -> None:
    """TC-I6-A-EV-022: RDEFormat's strategy must not leak into other modes."""
    # Given: a built-in handler whose v1 pipeline uses FileCopier or SmartTableFileCopier
    handler = handler_type()

    # When/Then: raw publication stays with the generic service
    assert handler.raw_copy_strategy(None) is None


@pytest.mark.parametrize(
    "handler_type",
    [pytest.param(handler_type, id=handler_type.__name__) for handler_type in _GENERIC_HANDLERS],
)
def test_non_rdeformat_handlers_keep_the_full_invoice_stage__tc_i6_a_ev_023(
    handler_type: type,
) -> None:
    """TC-I6-A-EV-023: RDEFormat's step narrowing must not leak into other modes."""
    # Given: a built-in handler whose v1 pipeline has all three invoice processors
    handler = handler_type()

    # When/Then: the full invoice stage stays selected
    assert handler.invoice_stage_steps(None) is None


def test_seam_answers_are_stateless__tc_i6_a_ev_024() -> None:
    """TC-I6-A-EV-024: querying one mode's seam does not change another's."""
    # Given: the RDEFormat handler, which does install overrides
    from rdetoolkit.modes.rdeformat import RdeFormatModeHandler

    rdeformat = RdeFormatModeHandler()
    invoice = InvoiceModeHandler()

    # When: interleaving seam queries across the two handlers
    first = invoice.raw_copy_strategy(None)  # type: ignore[arg-type]
    assert rdeformat.raw_copy_strategy(None) is not None  # type: ignore[arg-type]
    second = invoice.raw_copy_strategy(None)  # type: ignore[arg-type]

    # Then: the invoice answer is unchanged in both directions
    assert first is None
    assert second is None
