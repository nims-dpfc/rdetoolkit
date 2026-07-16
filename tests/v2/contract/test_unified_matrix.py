"""Unified callback/flow compatibility matrix for ADR-023.

EP table:
    TC-UM-*-CB-OK: v1 callback SUT succeeds and matches its frozen observation.
    TC-UM-*-CB-USERERR: callback StructuredError exits with frozen job.failed.
    TC-UM-*-CB-VALERR: invalid invoice exits with frozen validation artifact.
    TC-UM-*-FLOW-OK: eager v2 Runner succeeds against the same static input.
    TC-UM-*-FLOW-USERERR/VALERR: placed as Phase H/I non-strict xfails.
    TC-UM-*-CB-OBS: callback Events/Provenance/RunReport columns are Phase J xfails.

BV table:
    TC-UM-XLS/MDT/SMT-FLOW-CONTINUE-PARTIAL: partial multi-tile policy xfails.
    TC-UM-XLS/MDT/SMT-FLOW-FAIL-FAST: fail-fast policy xfails.
    TC-UM-MDT-FLOW-SIGTERM: representative termination flush contract xfail.

All expected callback values are static JSON produced by ``_generate.py`` at
the ``source.commit`` recorded in each snapshot. The tests execute v1 only as
the SUT; they never create an expected value at test time.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from rdetoolkit.core.flow import flow
from rdetoolkit.runner.lifecycle import Runner
from rdetoolkit.types import InputPaths, InvoiceData
from tests.v2.contract.fixtures import _generate

_MODES = ("invoice", "excelinvoice", "multidatatile", "rdeformat", "smarttable")
_MODE_IDS = {
    "invoice": "INV",
    "excelinvoice": "XLS",
    "multidatatile": "MDT",
    "rdeformat": "RDF",
    "smarttable": "SMT",
}
_FLOW_INVOICES: list[dict] = []


@flow
def _contract_noop_flow(paths: InputPaths, invoice: InvoiceData) -> None:
    """Exercise flow-boundary injection without changing v1-owned artifacts."""
    assert paths.inputdata.is_dir()
    _FLOW_INVOICES.append(deepcopy(invoice.raw))


def _frozen(mode: str, outcome: str) -> dict:
    path = _generate.EXPECTED_ROOT / mode / f"{outcome}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _v2_overrides(mode: str) -> dict:
    extended_mode = {
        "multidatatile": "MultiDataTile",
        "rdeformat": "rdeformat",
    }.get(mode)
    return {"system": {"extended_mode": extended_mode}} if extended_mode else {}


def _expected_invoice_sequence(invoices: dict[str, object]) -> list[object]:
    def _tile_index(path: str) -> int:
        if path == "data/invoice/invoice.json":
            return 0
        return int(Path(path).parts[2]) + 1

    return [value for path, value in sorted(invoices.items(), key=lambda item: _tile_index(item[0]))]


@pytest.mark.parametrize(
    ("mode", "outcome"),
    [
        pytest.param(mode, outcome, id=f"TC-UM-{_MODE_IDS[mode]}-CB-{outcome.upper()}")
        for mode in _MODES
        for outcome in ("ok", "usererr", "valerr")
    ],
)
def test_callback_entry_matches_frozen_v1_contract(mode: str, outcome: str) -> None:
    """Callback matrix cells compare the v1 SUT with static generated expectations."""
    # Given: the immutable snapshot generated from v1 at its recorded source.commit
    expected = _frozen(mode, outcome)["observed"]

    # When: executing the same v1 path as the subject under test in isolation
    actual = _generate.run_v1_sut(mode, outcome)

    # Then: all frozen artifacts and legacy return fields remain compatible
    assert actual == expected
    if outcome == "ok":
        assert actual["exit_code"] == 0
        assert actual["callback_count"] >= 1
        assert actual["job_failed_error_code"] is None
    else:
        assert actual["exit_code"] == 1
        assert actual["job_failed_error_code"].startswith("ErrorCode=")


@pytest.mark.parametrize(
    "mode",
    [pytest.param(mode, id=f"TC-UM-{_MODE_IDS[mode]}-FLOW-OK") for mode in _MODES],
)
def test_flow_entry_success_matches_frozen_v1_primary_contract(
    mode: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Flow OK cells preserve tile counts and invoice values from frozen v1 output."""
    # Given: a static mode fixture and its v1 callback-success snapshot
    root = tmp_path / mode
    _generate.materialize_sut_case(mode, root)
    monkeypatch.chdir(root)
    _FLOW_INVOICES.clear()
    expected = _frozen(mode, "ok")["observed"]
    runner = Runner(
        root=root,
        inputdata_path=root / "data" / "inputdata",
        unpacked_dir_path=root / "data" / "unpacked",
    )

    # When: running the eager flow through the v2 Runner
    report = runner.run(_contract_noop_flow, **_v2_overrides(mode))

    # Then: success, tile count, and primary invoice artifacts match frozen v1
    assert report.status == "success"
    assert len(report.iterations) == expected["callback_count"]
    assert _generate.normalize_snapshot(_FLOW_INVOICES, roots=(root,)) == _expected_invoice_sequence(expected["invoices"])


@pytest.mark.xfail(strict=False, reason="Phase H/I: unified flow error translation is not wired")
@pytest.mark.parametrize(
    ("mode", "outcome"),
    [
        pytest.param(mode, outcome, id=f"TC-UM-{_MODE_IDS[mode]}-FLOW-{outcome.upper()}")
        for mode in _MODES
        for outcome in ("usererr", "valerr")
    ],
)
def test_flow_error_cells_are_placed_for_phase_h_i(mode: str, outcome: str) -> None:
    """Flow error cells reserve the Phase H/I translation contract."""
    # Given: a matrix cell whose unified error adapter does not exist yet
    assert mode in _MODES
    assert outcome in {"usererr", "valerr"}
    # When/Then: the explicit failure keeps the non-strict xfail visible
    pytest.fail("Phase H/I must implement flow error parity against frozen fixtures")


@pytest.mark.xfail(strict=False, reason="Phase H/I: multi-tile policy integration is not wired")
@pytest.mark.parametrize(
    ("mode", "policy"),
    [
        pytest.param(mode, policy, id=f"TC-UM-{_MODE_IDS[mode]}-FLOW-{policy}")
        for mode in ("excelinvoice", "multidatatile", "smarttable")
        for policy in ("CONTINUE-PARTIAL", "FAIL-FAST")
    ],
)
def test_multitile_policy_cells_are_placed(mode: str, policy: str) -> None:
    """Multi-tile boundary cells reserve partial and fail-fast behavior."""
    # Given: a multi-tile mode and required future policy
    assert mode in {"excelinvoice", "multidatatile", "smarttable"}
    assert policy in {"CONTINUE-PARTIAL", "FAIL-FAST"}
    # When/Then: Phase H/I owns the unified policy implementation
    pytest.fail("Phase H/I must implement unified multi-tile error policies")


@pytest.mark.xfail(strict=False, reason="Phase J: deterministic SIGTERM flush integration is not wired")
def test_multidatatile_sigterm_cell_is_placed__tc_um_mdt_flow_sigterm() -> None:
    """TC-UM-MDT-FLOW-SIGTERM reserves RunReport/job.failed signal flushing."""
    # Given: the representative MultiDataTile termination contract
    signal_name = "SIGTERM"
    # When/Then: Phase J must wire and verify deterministic signal flushing
    assert signal_name == "SIGTERM"
    pytest.fail("Phase J must implement SIGTERM RunReport/job.failed flushing")


@pytest.mark.xfail(strict=False, reason="Phase J: callback observability is unavailable before unification")
@pytest.mark.parametrize(
    "mode",
    [pytest.param(mode, id=f"TC-UM-{_MODE_IDS[mode]}-CB-OBS") for mode in _MODES],
)
def test_callback_observability_columns_are_placed(mode: str) -> None:
    """Callback Events, Provenance, and RunReport columns remain visible for Phase J."""
    # Given: a legacy callback execution with no unified observability artifacts
    expected_columns = {"events", "provenance", "run_report"}
    assert mode in _MODES
    # When/Then: Phase J must populate every declared comparison column
    assert expected_columns
    pytest.fail("Phase J must add callback Events/Provenance/RunReport parity")
