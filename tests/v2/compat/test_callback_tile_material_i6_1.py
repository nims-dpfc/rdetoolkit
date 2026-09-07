"""Tile material handed to v1 callbacks (Session I6-1, ruling #3 and S14).

Session I5 left ``temp``, ``invoice_patch``, ``smarttable_rowfile`` and
``smarttable_row_data`` as ``None`` on the ``RdeOutputResourcePath`` given to a
v1 callback, so a migrated program could not reach material v1 always provided.
The rules ported here are v1's own: ``workflows.generate_folder_paths_iterator``
(per-tile ``temp``/``invoice_patch``), ``workflows._select_smarttable_rowfile``
(row CSV selection) and ``SmartTableInvoiceInitializer`` (the row dictionary,
which is now retained instead of discarded).

EP table:
| TC | Class | Input | Expected |
|----|-------|-------|----------|
| TC-I6-1-EP-050 | tile 0 | invoice-mode context | ``temp``/``invoice_patch`` are the tile-0 directories |
| TC-I6-1-EP-051 | divided tile | tile 1 context | both point below ``divided/0001`` |
| TC-I6-1-EP-052 | SmartTable | generated row CSV in rawfiles | ``smarttable_rowfile`` is that CSV |
| TC-I6-1-EP-053 | SmartTable | prepared tile invoice | ``smarttable_row_data`` is the initializer's row dict |

BV / negative table:
| TC | Class | Input | Expected |
|----|-------|-------|----------|
| TC-I6-1-EV-054 | non-SmartTable | plain rawfiles | both SmartTable fields stay ``None`` |
| TC-I6-1-EV-055 | divided tile | tile 1 with a run-level backup | ``invoice_org`` stays run-level |
| TC-I6-1-EV-056 | wrong prefix | ``other_0000.csv`` first rawfile | ``smarttable_rowfile`` stays ``None`` |
| TC-I6-1-EV-057 | empty tile | no rawfiles | both SmartTable fields stay ``None`` |
| TC-I6-1-EV-058 | run lifetime | three runs on distinct roots | no row data is retained afterwards |
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from rdetoolkit.compat.v1.callback import to_legacy_dataset_paths
from rdetoolkit.core.context import RunContext
from rdetoolkit.domain.invoice_service import InvoiceService
from rdetoolkit.runner.mode_resolver import ModeKind
from rdetoolkit.runner.paths import resolve_tile_paths
from rdetoolkit.types import InputPaths, IterationInfo, OutputContext, RdeConfig
from tests.v2.contract.fixtures import _generate


def _context(root: Path, *, idx: int = 0, rawfiles: tuple[Path, ...] = ()) -> RunContext:
    data_root = root / "data"
    for name in ("inputdata", "invoice", "tasksupport"):
        (data_root / name).mkdir(parents=True, exist_ok=True)
    tile = resolve_tile_paths(data_root, idx)
    return RunContext(
        paths=InputPaths(
            inputdata=data_root / "inputdata",
            invoice=data_root / "invoice",
            tasksupport=data_root / "tasksupport",
            raw=rawfiles[0] if len(rawfiles) == 1 else None,
            rawfiles=rawfiles,
        ),
        out=OutputContext.from_resource_paths(tile),
        config=RdeConfig(),
        iteration=IterationInfo(index=idx, total=idx + 1, mode="invoice"),
    )


def test_root_tile_exposes_temp_and_invoice_patch__tc_i6_1_ep_050(tmp_path: Path) -> None:
    """TC-I6-1-EP-050: tile 0 receives the real data/temp and data/invoice_patch."""
    # Given: a tile-0 context
    context = _context(tmp_path)

    # When: converting to v1 dataset paths
    legacy = to_legacy_dataset_paths(context)

    # Then: both directories are the tile-0 paths, not None
    assert legacy.output_paths.temp == tmp_path / "data" / "temp"
    assert legacy.output_paths.invoice_patch == tmp_path / "data" / "invoice_patch"


def test_divided_tile_exposes_its_own_directories__tc_i6_1_ep_051(tmp_path: Path) -> None:
    """TC-I6-1-EP-051: a divided tile owns divided/0001/temp and invoice_patch."""
    # Given: a tile-1 context
    context = _context(tmp_path, idx=1)

    # When: converting to v1 dataset paths
    legacy = to_legacy_dataset_paths(context)

    # Then: the divided tile's own directories are exposed
    assert legacy.output_paths.temp == tmp_path / "data" / "divided" / "0001" / "temp"
    assert legacy.output_paths.invoice_patch == tmp_path / "data" / "divided" / "0001" / "invoice_patch"


def test_smarttable_rowfile_follows_the_v1_rule__tc_i6_1_ep_052(tmp_path: Path) -> None:
    """TC-I6-1-EP-052: the generated row CSV is selected exactly as v1 selects it."""
    # Given: a tile whose first raw file is a generated SmartTable row CSV
    rowfile = tmp_path / "data" / "temp" / "fsmarttable_full_0001.csv"
    rowfile.parent.mkdir(parents=True, exist_ok=True)
    rowfile.write_text("a,b\n1,2\n", encoding="utf-8")
    other = tmp_path / "data" / "temp" / "measurement.txt"
    other.write_text("data", encoding="utf-8")
    context = _context(tmp_path, rawfiles=(rowfile, other))

    # When: converting to v1 dataset paths
    legacy = to_legacy_dataset_paths(context)

    # Then: the row CSV is exposed to the callback
    assert legacy.output_paths.smarttable_rowfile == rowfile


def test_smarttable_row_data_survives_invoice_preparation__tc_i6_1_ep_053(tmp_path: Path) -> None:
    """TC-I6-1-EP-053: the initializer's row dict reaches the callback."""
    # Given: a SmartTable fixture whose tiles were prepared by the invoice service
    root = tmp_path / "smarttable"
    _generate.materialize_sut_case("smarttable", root)
    data_root = root / "data"
    service = InvoiceService()
    service.begin_run(root)
    from rdetoolkit.runner.iterator import iterate_tiles  # noqa: PLC0415 -- exercises the production enumeration

    tiles = list(iterate_tiles(ModeKind.smarttable, data_root / "inputdata", data_root / "temp", data_root))
    info, paths, out = tiles[0]
    service.prepare_tile(
        ModeKind.smarttable,
        paths=paths,
        invoice_dir=out.invoice,
        iteration_index=info.index,
        invariant_invoice=None,
        invoice_source=data_root / "invoice" / "invoice.json",
    )
    context = RunContext(paths=paths, out=out, config=RdeConfig(), iteration=info)

    # When: converting to v1 dataset paths
    legacy = to_legacy_dataset_paths(context)

    # Then: the callback sees the same row dictionary the initializer computed
    row_data = legacy.output_paths.smarttable_row_data
    assert row_data is not None
    expected = json.loads((out.invoice / "invoice.json").read_text(encoding="utf-8"))
    assert row_data["basic/dataName"] == expected["basic"]["dataName"]
    assert legacy.output_paths.smarttable_rowfile == paths.rawfiles[0]


def test_non_smarttable_tiles_keep_the_fields_empty__tc_i6_1_ev_054(tmp_path: Path) -> None:
    """TC-I6-1-EV-054: an ordinary tile exposes no SmartTable material."""
    # Given: a tile whose raw file is an ordinary input
    rawfile = tmp_path / "data" / "inputdata" / "sample.txt"
    rawfile.parent.mkdir(parents=True, exist_ok=True)
    rawfile.write_text("raw", encoding="utf-8")
    context = _context(tmp_path, rawfiles=(rawfile,))

    # When: converting to v1 dataset paths
    legacy = to_legacy_dataset_paths(context)

    # Then: both SmartTable fields stay empty
    assert legacy.output_paths.smarttable_rowfile is None
    assert legacy.output_paths.smarttable_row_data is None


def test_divided_tile_keeps_the_run_level_invoice_org__tc_i6_1_ev_055(tmp_path: Path) -> None:
    """TC-I6-1-EV-055: divided tiles read the run-level backup, as v1 does."""
    # Given: a run-level backup and a divided tile
    backup = tmp_path / "data" / "temp" / "invoice_org.json"
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_text("{}", encoding="utf-8")
    context = _context(tmp_path, idx=1)

    # When: converting to v1 dataset paths
    legacy = to_legacy_dataset_paths(context)

    # Then: the tile's own temp directory never shadows the run-level backup
    assert legacy.output_paths.invoice_org == backup


@pytest.mark.parametrize(
    "filename",
    ["other_0000.csv", "fsmarttable_full.csv", "fsmarttable_full_abcd.csv", "fsmarttable_full_0000.txt"],
)
def test_non_matching_first_rawfile_is_not_a_rowfile__tc_i6_1_ev_056(tmp_path: Path, filename: str) -> None:
    """TC-I6-1-EV-056: only v1's row-CSV pattern selects a SmartTable row file."""
    # Given: a first raw file that fails one clause of the v1 rule
    candidate = tmp_path / "data" / "temp" / filename
    candidate.parent.mkdir(parents=True, exist_ok=True)
    candidate.write_text("x", encoding="utf-8")
    context = _context(tmp_path, rawfiles=(candidate,))

    # When: converting to v1 dataset paths
    legacy = to_legacy_dataset_paths(context)

    # Then: no row file is advertised
    assert legacy.output_paths.smarttable_rowfile is None


def test_empty_tile_exposes_no_smarttable_material__tc_i6_1_ev_057(tmp_path: Path) -> None:
    """TC-I6-1-EV-057: a tile without raw files exposes no SmartTable material."""
    # Given: a tile with no raw files
    context = _context(tmp_path)

    # When: converting to v1 dataset paths
    legacy = to_legacy_dataset_paths(context)

    # Then: both SmartTable fields stay empty
    assert legacy.output_paths.smarttable_rowfile is None
    assert legacy.output_paths.smarttable_row_data is None


def test_sequential_runs_retain_no_row_data__tc_i6_1_ev_058(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TC-I6-1-EV-058: the row-data handoff does not accumulate across runs."""
    # Given: three SmartTable runs rooted in three different directories
    from rdetoolkit.core.flow import flow
    from rdetoolkit.domain import invoice as invoice_module
    from rdetoolkit.runner.lifecycle import Runner

    @flow
    def _noop(paths: InputPaths) -> None:
        assert paths.inputdata.is_dir()

    invoice_module._TILE_ROW_DATA.clear()  # noqa: SLF001 -- isolate this test from earlier runs

    # When: running them one after another
    for index in range(3):
        root = tmp_path / f"run_{index}"
        _generate.materialize_sut_case("smarttable", root)
        monkeypatch.chdir(root)
        runner = Runner(
            root=root,
            inputdata_path=root / "data" / "inputdata",
            unpacked_dir_path=root / "data" / "temp",
        )
        report = runner.run(_noop)
        assert report.status == "success", report.error

    # Then: every run released its own material at the end of the run
    assert invoice_module._TILE_ROW_DATA == {}  # noqa: SLF001 -- the handoff must be empty
