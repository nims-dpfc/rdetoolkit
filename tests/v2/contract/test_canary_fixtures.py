"""Contracts for five real-data canary observations frozen from the v1 SUT.

Equivalence partitions prepared before implementation:

| Family | Partition | Expected | Test IDs |
| --- | --- | --- | --- |
| real canary | invoice | frozen match and v1 mode ``invoice`` | TC-H4-CANARY-001 |
| real canary | ExcelInvoice | frozen match and v1 mode ``Excelinvoice`` | TC-H4-CANARY-002 |
| real canary | MultiDataTile | frozen match and v1 mode ``MultiDataTile`` | TC-H4-CANARY-003 |
| real canary | RDEFormat | frozen match and v1 mode ``rdeformat`` | TC-H4-CANARY-004 |
| real canary | SmartTable | frozen match and v1 mode ``SmartTableInvoice`` | TC-H4-CANARY-005 |

Boundary values prepared before implementation:

| Family | Boundary | Expected | Test ID |
| --- | --- | --- | --- |
| frozen inventory | exactly five OK-only paths | no synthetic/error snapshot is replaced | TC-H4-CANARY-BV-001 |
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tests.v2.contract.fixtures import _generate

_CASES = [
    pytest.param("invoice", id="TC-H4-CANARY-001"),
    pytest.param("excelinvoice", id="TC-H4-CANARY-002"),
    pytest.param("multidatatile", id="TC-H4-CANARY-003"),
    pytest.param("rdeformat", id="TC-H4-CANARY-004"),
    pytest.param("smarttable", id="TC-H4-CANARY-005"),
]

_EXPECTED_V1_MODE_LABELS = {
    "excelinvoice": "Excelinvoice",
    "invoice": "invoice",
    "multidatatile": "MultiDataTile",
    "rdeformat": "rdeformat",
    "smarttable": "SmartTableInvoice",
}


@pytest.mark.parametrize("mode", _CASES)
def test_real_canary_matches_frozen_v1_observation(mode: str) -> None:
    """TC-H4-CANARY-001..005: real inputs retain their v1 OK contract."""
    # Given: an OK-only snapshot frozen by the canonical generator
    snapshot_path = _generate.CANARY_EXPECTED_ROOT / mode / "ok.json"
    fixture: dict[str, Any] = json.loads(snapshot_path.read_text(encoding="utf-8"))
    # When: executing the v1 SUT against the same imported real input
    actual = _generate.run_v1_canary_sut(mode)
    # Then: every normalized primary observation matches the frozen oracle
    assert fixture["case"] == {
        "entry": "custom_dataset_function",
        "family": "canary",
        "mode": mode,
        "outcome": "ok",
    }
    assert actual == fixture["observed"]
    assert actual["exit_code"] == 0
    assert actual["callback_count"] >= 1
    status_modes = {
        status["mode"] for status in actual["legacy_return"]["statuses"]
    }
    assert status_modes == {_EXPECTED_V1_MODE_LABELS[mode]}
    if mode == "excelinvoice":
        divided_invoices = {
            path: invoice
            for path, invoice in actual["invoices"].items()
            if path.startswith("data/divided/")
        }
        divided_tile_roots = {
            path.split("/", maxsplit=3)[2]
            for path in actual["output_tree"]["directories"]
            if path.startswith("data/divided/000")
        }
        assert actual["callback_count"] == 2
        assert len(actual["invoices"]) == 2
        assert len(divided_invoices) == 1
        assert divided_tile_roots == {"0001"}
        assert {
            invoice["basic"]["dataName"] for invoice in actual["invoices"].values()
        } == {"CrossBeam550_手動_1.tif", "CrossBeam550_自動_1.tif"}


def test_canary_snapshot_inventory_is_five_ok_only__tc_h4_canary_bv_001() -> None:
    """TC-H4-CANARY-BV-001: canary adds five OK snapshots and no error cases."""
    # Given: the generator's real-canary inventory
    snapshots = _generate.canary_snapshot_paths()
    # When: rendering paths relative to the fixture root
    relative = [path.relative_to(_generate.FIXTURE_ROOT) for path in snapshots]
    # Then: the sorted inventory is exactly one OK snapshot per mode
    assert relative == [
        Path("expected/canary") / mode / "ok.json"
        for mode in ("excelinvoice", "invoice", "multidatatile", "rdeformat", "smarttable")
    ]
