"""ExcelInvoice real-canary FLOW parity for Session I6-B (ruling #1).

The synthetic ExcelInvoice FLOW-OK cell is already pinned to full artifact
parity in ``tests/v2/contract/test_unified_matrix.py``. This module extends the
same comparison to the imported real-canary family (a SEM structured program),
which exercises material the synthetic fixture cannot: a formula-bearing
workbook, a Japanese schema, and an ``rdeconfig.yaml`` shipped inside
``data/tasksupport``.

Because v2 configuration discovery reads only ``root/rdeconfig.yaml`` and
``pyproject.toml`` (contracts.md §I6-1 debt 2), the canary's effective
configuration is handed to the Runner as overrides. The projection is performed
by the production ``ConfigNormalizer`` with ``origin="v1"`` rather than by a
hand-written mapping, so this harness cannot drift away from the v1 -> v2
configuration contract it depends on.

EP table:
| TC | Class | Input | Expected |
|----|-------|-------|----------|
| TC-I6-B-EP-001 | canary FLOW | real ExcelInvoice canary + its effective config | observation equals ``expected/canary/excelinvoice/ok.json`` |

BV / negative table:
| TC | Class | Input | Expected |
|----|-------|-------|----------|
| TC-I6-B-EV-002 | config omitted | same canary, Runner defaults | observation differs — the overrides are load-bearing, not decorative |
| TC-I6-B-EV-003 | projection | frozen ``case.effective_config`` | the recorded v1 config is reproducible and non-default |
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from rdetoolkit.config.normalize import ConfigNormalizer
from rdetoolkit.core.flow import flow
from rdetoolkit.models.config import Config
from rdetoolkit.runner.lifecycle import Runner
from rdetoolkit.types import InputPaths, InvoiceData
from tests.v2.contract.fixtures import _generate
from tests.v2.contract.observe import observe_v2_run, parity_view

_MODE = "excelinvoice"
#: Tiles the frozen canary observation records for this family.
_CANARY_TILE_COUNT = 2


@flow
def _canary_flow(paths: InputPaths, invoice: InvoiceData) -> None:
    """Consume one tile without writing anything the Runner does not own."""
    assert paths.inputdata.is_dir()
    assert invoice.raw


def _frozen_canary() -> dict[str, Any]:
    path = _generate.CANARY_EXPECTED_ROOT / _MODE / "ok.json"
    return json.loads(path.read_text(encoding="utf-8"))


def canary_overrides(mode: str) -> dict[str, Any]:
    """Project a frozen canary ``effective_config`` onto v2 Runner overrides.

    Args:
        mode: Canary mode whose frozen snapshot carries the record.

    Returns:
        Canonical v2 configuration mapping accepted by ``Runner.run``.
    """
    path = _generate.CANARY_EXPECTED_ROOT / mode / "ok.json"
    recorded = json.loads(path.read_text(encoding="utf-8"))["case"]["effective_config"]["config"]
    # origin="v1" is the production projection: the canary config file is v1
    # material, so re-deriving the mapping here would fork the contract.
    normalized = ConfigNormalizer().normalize(
        Config(**recorded),
        root=Path(path.parent),
        origin="v1",
    )
    return normalized.model_dump()


def _run_canary(root: Path, monkeypatch: pytest.MonkeyPatch, **overrides: Any) -> Any:
    _generate._materialize_canary_case(_MODE, root)  # noqa: SLF001 -- shared canary assembly
    monkeypatch.chdir(root)
    runner = Runner(
        root=root,
        inputdata_path=root / "data" / "inputdata",
        # The flow entry unpacks into data/temp, as v1 does (contracts.md §I6-1).
        unpacked_dir_path=root / "data" / "temp",
    )
    return runner.run(_canary_flow, **overrides)


def test_canary_flow_matches_the_frozen_v1_observation__tc_i6_b_ep_001(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TC-I6-B-EP-001: the real ExcelInvoice canary reaches full artifact parity."""
    # Given: the imported canary family and the configuration v1 ran it with
    root = tmp_path / _MODE
    root.mkdir()
    expected = _frozen_canary()["observed"]

    # When: running the eager flow through the v2 Runner
    report = _run_canary(root, monkeypatch, **canary_overrides(_MODE))

    # Then: every compared artifact key equals the frozen v1 observation
    assert report.status == "success"
    assert len(report.iterations) == _CANARY_TILE_COUNT
    assert observe_v2_run(root) == parity_view(expected)


def test_default_config_does_not_reproduce_the_canary__tc_i6_b_ev_002(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TC-I6-B-EV-002: the canary's own config is required, so parity is not luck.

    v2 discovery ignores ``data/tasksupport/rdeconfig.yaml`` (contracts.md
    §I6-1 debt 2). Without the overrides the Runner falls back to
    ``RdeConfig`` defaults, whose artifact switches differ, and the comparison
    must notice.
    """
    # Given: the same canary family, run with no configuration at all
    root = tmp_path / _MODE
    root.mkdir()
    expected = _frozen_canary()["observed"]

    # When: running the eager flow without the canary's effective config
    report = _run_canary(root, monkeypatch)

    # Then: the run still succeeds but its artifacts are not the v1 ones
    assert report.status == "success"
    assert observe_v2_run(root) != parity_view(expected)


def test_recorded_effective_config_is_reproducible__tc_i6_b_ev_003() -> None:
    """TC-I6-B-EV-003: the frozen record round-trips and is not the default."""
    # Given: the provenance the generator froze alongside the observation
    record = _frozen_canary()["case"]["effective_config"]
    assert record["source"]["path"] == "data/tasksupport/rdeconfig.yaml"

    # When: re-deriving it from the committed canary configuration file
    rederived = _generate.canary_effective_config_record(_MODE)

    # Then: the record is reproducible and carries non-default switches
    assert rederived == record
    overrides = canary_overrides(_MODE)
    assert overrides["system"]["save_raw"] is True
    assert overrides["system"]["save_thumbnail_image"] is True
    assert overrides != ConfigNormalizer().normalize(None, root=Path("/nonexistent"), origin="v2").model_dump()
