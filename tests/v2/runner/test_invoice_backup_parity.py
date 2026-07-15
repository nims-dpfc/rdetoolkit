"""Regression tests for v1-compatible run-level invoice backup selection.

Equivalence partitions (EP):

| API | Partition | Rationale | Expected | Test ID |
| --- | --- | --- | --- | --- |
| ``Runner.iterate`` | excelinvoice | existing positive control | temp backup exists | TC-G0-BACKUP-001 |
| ``Runner.iterate`` | rdeformat | missing v2 delegation | temp backup exists | TC-G0-BACKUP-002 |
| ``Runner.iterate`` | multidatatile | missing v2 delegation | temp backup exists | TC-G0-BACKUP-003 |
| ``Runner.iterate`` | invoice | excluded mode | temp backup absent | TC-G0-BACKUP-004 |
| ``Runner.iterate`` | smarttable | excluded mode | temp backup absent | TC-G0-BACKUP-005 |

Boundary values (BV):

| API | Boundary | Rationale | Expected | Test ID |
| --- | --- | --- | --- | --- |
| ``Runner.iterate`` | one tile | minimum run that prepares an invoice source | mode contract holds | TC-G0-BACKUP-001..005 |

NOTE (2026-07-15): reconstructed from the surviving pytest ``.pyc`` after the
original working tree was wiped before commit (see session_g0.md). Semantics,
test ids and assertions are preserved from the verified original.
"""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from rdetoolkit.runner.execute import ExecutionResult
from rdetoolkit.runner.lifecycle import Runner
from rdetoolkit.runner.mode_resolver import ModeKind
from rdetoolkit.types import InputPaths, IterationInfo, RdeConfig

_CASES = [
    pytest.param(ModeKind.excelinvoice, True, id="excelinvoice"),
    pytest.param(ModeKind.rdeformat, True, id="rdeformat"),
    pytest.param(ModeKind.multidatatile, True, id="multidatatile"),
    pytest.param(ModeKind.invoice, False, id="invoice"),
    pytest.param(ModeKind.smarttable, False, id="smarttable"),
]


@pytest.mark.parametrize(("mode", "expects_backup"), _CASES)
def test_run_level_invoice_backup_matches_v1_mode_contract__tc_g0_backup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mode: ModeKind,
    expects_backup: bool,
) -> None:
    """TC-G0-BACKUP-001..005: only the three v1 modes create a temp backup."""
    # Given: a minimal data tree with a run-level source invoice
    data_root = tmp_path / "data"
    inputdata = data_root / "inputdata"
    invoice_dir = data_root / "invoice"
    tasksupport = data_root / "tasksupport"
    unpacked = data_root / "temp"
    for path in (inputdata, invoice_dir, tasksupport, unpacked):
        path.mkdir(parents=True)
    source = {"datasetId": "source", "basic": {"dataName": "original"}}
    source_path = invoice_dir / "invoice.json"
    source_path.write_text(json.dumps(source), encoding="utf-8")
    rawfile = inputdata / ("source.xlsx" if mode is ModeKind.excelinvoice else "source.dat")
    rawfile.write_text("placeholder", encoding="utf-8")

    # And: tile machinery stubbed so only the run-level invoice-source
    # preparation (the behavior under test) touches the real filesystem
    info = IterationInfo(index=0, total=1, mode=mode.value)
    paths = InputPaths(
        inputdata=inputdata,
        invoice=invoice_dir,
        tasksupport=tasksupport,
        raw=rawfile,
        rawfiles=(rawfile,),
    )
    out = SimpleNamespace(invoice=invoice_dir)
    monkeypatch.setattr(
        "rdetoolkit.runner.lifecycle.iterate_tiles",
        lambda *args, **kwargs: iter([(info, paths, out)]),
    )
    monkeypatch.setattr("rdetoolkit.runner.lifecycle._tile_invoice", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        "rdetoolkit.runner.lifecycle.run_tile",
        lambda *args, **kwargs: ExecutionResult(
            iteration_index=0,
            status="completed",
            call_records=(),
            outputs=(),
            datatile_id="source",
        ),
    )

    # When: one Runner iteration executes in the given mode
    monkeypatch.chdir(tmp_path)
    runner = Runner(
        root=tmp_path,
        inputdata_path=inputdata,
        unpacked_dir_path=unpacked,
        run_id_factory=lambda: f"backup-{mode.value}",
    )
    runner.run_id = f"backup-{mode.value}"
    report = runner.iterate(lambda: None, mode, RdeConfig())
    backup_path = data_root / "temp" / "invoice_org.json"

    # Then: the v1 mode contract decides whether the temp backup exists
    assert report.status == "success"
    assert backup_path.exists() is expects_backup
    if expects_backup:
        assert json.loads(backup_path.read_text(encoding="utf-8")) == source
