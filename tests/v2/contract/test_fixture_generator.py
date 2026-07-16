"""Tests for the Session G1 contract-fixture generator foundation.

EP table:
    TC-G1-001 (normal): volatile report fields and embedded version/path text
        are normalized before a snapshot is frozen.
    TC-G1-002 (normal): canonical JSON output is byte-identical across writes.
    TC-G1-003 (abnormal): ``--check`` reports a missing frozen snapshot instead
        of silently creating an expected value.
    TC-GR-001 (abnormal): an empty-directory-free checkout still stages every
        output-tree directory required by the frozen contract.
    TC-GR-002 (normal): oracle observations freeze parsed backup content and
        complete normalized ``job.failed`` text without dropping legacy fields.
    TC-GR-003 (abnormal): ``--check`` warns when frozen and executing source
        revisions differ without turning the warning into snapshot failure.
    TC-GR-004 (abnormal): deterministic generated-input drift is reported by
        relative fixture path instead of being ignored by snapshot checking.
    TC-GR-005 (abnormal): ascending and descending rdeformat file discovery
        normalize order-dependent status targets to the same stable value.

BV table:
    TC-G1-004 (empty): normalization preserves empty containers and ``None``.
    TC-GR-001 (empty directory): missing ``data/unpacked`` is recreated during
        oracle-case materialization.
    TC-GR-002 (multiline): the first error line and trailing traceback/message
        lines are all retained in the frozen observation.
    TC-GR-003 (one revision): a single stale recorded commit emits one warning.
    TC-GR-004 (one byte): a one-byte deterministic manifest change is detected;
        XLSX validation uses values because package metadata is nondeterministic.
    TC-GR-005 (two orders): opposite first-file selections keep each tile prefix
        and replace only the nondeterministic subdirectory component.
"""

from __future__ import annotations

import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from rdetoolkit.invoicefile import SmartTableFile
from tests.v2.contract.fixtures import _generate


def test_normalize_snapshot_replaces_all_declared_volatile_values__tc_g1_001(
    tmp_path: Path,
) -> None:
    """TC-G1-001: normalization removes every volatile contract field."""
    # Given: representative v1/v2 output with every declared volatile value
    root = tmp_path / "isolated-v1-run"
    source = {
        "run_id": "2ec0bfdf-4b91-46d0-a6a8-6c7585b33f31",
        "started_at": "2026-07-15T13:52:26.123456Z",
        "duration_ms": 91.25,
        "config_digest": "sha256:abcdef",
        "traceback": "Traceback (most recent call last):\nValueError: boom",
        "requirements": "rdetoolkit==2.0.0a1\npandas==2.3.0\n",
        "path": str(root / "data" / "inputdata" / "sample.txt"),
        "nested": [{"dateSubmitted": "2026-07-15"}],
    }

    # When: normalizing before snapshot serialization
    normalized = _generate.normalize_snapshot(source, roots=(root,))

    # Then: stable placeholders replace volatility while stable text remains
    assert normalized == {
        "run_id": "<RUN_ID>",
        "started_at": "<TIMESTAMP>",
        "duration_ms": "<DURATION_MS>",
        "config_digest": "<CONFIG_DIGEST>",
        "traceback": "<TRACEBACK>",
        "requirements": "rdetoolkit==<VERSION>\npandas==2.3.0\n",
        "path": "<RUN_ROOT>/data/inputdata/sample.txt",
        "nested": [{"dateSubmitted": "<DATE>"}],
    }


def test_write_json_snapshot_is_canonical__tc_g1_002(tmp_path: Path) -> None:
    """TC-G1-002: canonical snapshots have sorted keys and a trailing newline."""
    # Given: equivalent mappings with different insertion order
    first = {"z": 1, "a": {"two": 2, "one": 1}}
    second = {"a": {"one": 1, "two": 2}, "z": 1}
    first_path = tmp_path / "first.json"
    second_path = tmp_path / "second.json"

    # When: writing both through the generator snapshot helper
    _generate.write_json_snapshot(first_path, first)
    _generate.write_json_snapshot(second_path, second)

    # Then: their frozen bytes are identical and parse to the source value
    assert first_path.read_bytes() == second_path.read_bytes()
    assert first_path.read_bytes().endswith(b"\n")
    assert json.loads(first_path.read_text(encoding="utf-8")) == first


def test_check_snapshot_rejects_missing_expected_file__tc_g1_003(
    tmp_path: Path,
) -> None:
    """TC-G1-003: check mode never creates a missing expected snapshot."""
    # Given: a generated candidate with no corresponding frozen snapshot
    missing = tmp_path / "missing.json"

    # When: comparing the candidate in check mode
    mismatch = _generate.compare_snapshot(missing, {"status": "success"})

    # Then: the mismatch is explicit and the expected file remains absent
    assert mismatch == "missing frozen snapshot: missing.json"
    assert not missing.exists()


def test_normalize_snapshot_preserves_empty_values__tc_g1_004() -> None:
    """TC-G1-004: empty and null boundary values remain semantically intact."""
    # Given: the empty-container and null boundaries
    source = {"mapping": {}, "sequence": [], "value": None, "text": ""}

    # When: normalizing the value
    normalized = _generate.normalize_snapshot(source)

    # Then: no placeholder is invented for stable empty values
    assert normalized == source


def test_build_static_inputs_covers_all_modes__tc_g1_005(tmp_path: Path) -> None:
    """TC-G1-005: input generation registers each of the five contract modes."""
    # Given: an empty destination outside the repository fixture tree
    destination = tmp_path / "inputs"

    # When: building the static Phase G inputs
    manifest = _generate.build_static_inputs(destination)

    # Then: every canonical mode has a generated or registered input definition
    assert set(manifest) == {
        "excelinvoice",
        "invoice",
        "multidatatile",
        "rdeformat",
        "smarttable",
    }
    assert all((destination / mode).exists() for mode in manifest)


def test_excelinvoice_inputs_include_multi_and_zero_row_workbooks__tc_g1_006(
    tmp_path: Path,
) -> None:
    """TC-G1-006: ExcelInvoice covers normal multi-row and zero-row boundaries."""
    # Given: generated ExcelInvoice inputs derived from tests/fixtures row data
    destination = tmp_path / "inputs"
    _generate.build_static_inputs(destination)
    inputdata = destination / "excelinvoice" / "data" / "inputdata"

    # When: reading the invoice_form sheets without interpreting their headers
    multi = pd.read_excel(inputdata / "excelinvoice_multi.xlsx", sheet_name="invoice_form", header=None)
    zero_workbook = pd.ExcelFile(inputdata / "excelinvoice_zero_rows.xlsx")

    # Then: the normal workbook has two source rows and the boundary has none
    assert multi.iloc[:, 0].astype(str).isin({"test_child1.txt", "test_child2.txt"}).sum() == 2
    assert "invoice_form" not in zero_workbook.sheet_names


def test_rdeformat_zip_contains_numbered_and_japanese_members__tc_g1_007(
    tmp_path: Path,
) -> None:
    """TC-G1-007: the representative RDEFormat archive preserves Unicode paths."""
    # Given: a generated RDEFormat contract archive
    destination = tmp_path / "inputs"
    _generate.build_static_inputs(destination)
    archive = destination / "rdeformat" / "data" / "inputdata" / "rdeformat_sample.zip"

    # When: inspecting its committed member list
    with zipfile.ZipFile(archive) as source:
        members = source.namelist()

    # Then: numbered tile groups and a Japanese filename are both represented
    assert "0000/raw/first.txt" in members
    assert "0001/raw/日本語データ.txt" in members


def test_smarttable_workbooks_are_spec_complete_and_equivalent__tc_g1_008(
    tmp_path: Path,
) -> None:
    """TC-G1-008: SmartTable xlsx/csv inputs cover mappings and edge values."""
    # Given: the generated spec-complete workbook in both supported formats
    destination = tmp_path / "inputs"
    _generate.build_static_inputs(destination)
    smarttable = destination / "smarttable"
    xlsx_path = smarttable / "data" / "inputdata" / "smarttable_full.xlsx"
    csv_path = smarttable / "smarttable_full.csv"

    # When: loading both through the public SmartTable reader
    xlsx = SmartTableFile(xlsx_path).read_table()
    csv = SmartTableFile(csv_path).read_table()

    # Then: the mapping rows agree and cover every required prefix with 3 rows
    assert xlsx.fillna("").astype(str).to_dict("records") == csv.fillna("").astype(str).to_dict("records")
    assert len(xlsx) == 3
    expected_prefixes = {
        "basic/",
        "custom/",
        "sample/generalAttributes.",
        "sample/specificAttributes.",
        "sample/",
        "meta/",
        "inputdata",
    }
    assert all(any(column.startswith(prefix) for column in xlsx.columns) for prefix in expected_prefixes)
    assert xlsx.isna().any().any()

    # And: the xlsx source cells retain numeric and date types before dtype=str reading
    source = pd.read_excel(xlsx_path, header=None)
    assert any(isinstance(value, (int, float)) for value in source.iloc[2:].to_numpy().flat)
    assert any(isinstance(value, datetime) for value in source.iloc[2:].to_numpy().flat)


def test_invoice_references_resolve_without_copying_assets__tc_g1_009(
    tmp_path: Path,
) -> None:
    """TC-G1-009: invoice mode registers immutable tests/samplefile assets."""
    # Given: the generated invoice-mode reference registry
    destination = tmp_path / "inputs"
    manifest = _generate.build_static_inputs(destination)

    # When: resolving its paths against the repository root
    references = manifest["invoice"]["references"]
    resolved = [(_generate.REPOSITORY_ROOT / reference).resolve() for reference in references]

    # Then: all references target existing canonical sample assets
    assert {path.name for path in resolved} == {
        "invoice.json",
        "invoice.schema.basic.json",
        "invoice.schema.full.json",
        "invoice.schema.json",
    }
    assert all(path.is_file() for path in resolved)


def test_frozen_v1_scenarios_cover_matrix_and_excel_zero_boundary__tc_g1_010() -> None:
    """TC-G1-010: frozen v1 observations cover 15 callback cells plus zero rows."""
    # Given: the generator's declared frozen-snapshot inventory
    snapshots = _generate.expected_snapshot_paths()

    # When: grouping the declared cases by mode and outcome
    relative = {
        path.relative_to(_generate.FIXTURE_ROOT).as_posix()
        for path in snapshots
    }

    # Then: every mode/outcome callback cell and the Excel zero-row BV exist
    expected = {
        f"expected/v1/{mode}/{outcome}.json"
        for mode in ("invoice", "excelinvoice", "multidatatile", "rdeformat", "smarttable")
        for outcome in ("ok", "usererr", "valerr")
    }
    expected.add("expected/v1/excelinvoice/zero_rows.json")
    assert relative == expected
    assert all(path.is_file() for path in snapshots)

    # And: each value records the generator provenance and observed v1 result.
    # source.commit is the revision that WROTE the snapshot (recorded at
    # regeneration time), so it must be one non-empty value shared by every
    # snapshot (single-regeneration invariant) — it intentionally does NOT
    # have to match the currently checked-out revision; staleness is a
    # non-failing warning surfaced by _generate.source_revision_warnings.
    recorded_commits: set[str] = set()
    for path in snapshots:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["source"]["tag"] == _generate.SOURCE_TAG
        commit = payload["source"]["commit"]
        assert isinstance(commit, str) and commit and commit != "<unrecorded>"
        recorded_commits.add(commit)
        assert payload["observed"]["exit_code"] in {0, 1}
        assert "output_tree" in payload["observed"]
    assert len(recorded_commits) == 1, (
        f"snapshots must come from one regeneration run, got {sorted(recorded_commits)}"
    )


def test_materialize_oracle_case_recreates_unpacked_after_fresh_checkout__tc_gr_001(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TC-GR-001: staging recreates contract directories Git cannot preserve."""
    # Given: a copied input tree with all empty directories removed like Git checkout
    checkout_inputs = tmp_path / "checkout-inputs"
    shutil.copytree(_generate.INPUT_ROOT, checkout_inputs)
    for path in sorted(checkout_inputs.rglob("*"), reverse=True):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()
    assert not (checkout_inputs / "multidatatile" / "data" / "unpacked").exists()
    monkeypatch.setattr(_generate, "INPUT_ROOT", checkout_inputs)

    # When: materializing a v1 oracle case from that Git-representable input
    staged_root = tmp_path / "staged"
    _generate._materialize_oracle_case("multidatatile", staged_root)

    # Then: the staged output tree contains the required empty directory
    assert (staged_root / "data" / "unpacked").is_dir()


def test_oracle_observation_freezes_backup_and_full_normalized_job_failed__tc_gr_002(
    tmp_path: Path,
) -> None:
    """TC-GR-002: observations retain backup JSON and every job.failed line."""
    # Given: an oracle tree with a backup and multiline failure containing its root
    data_root = tmp_path / "data"
    backup = data_root / "temp" / "invoice_org.json"
    backup.parent.mkdir(parents=True)
    backup_value = {"datasetId": "source", "basic": {"dataName": "original"}}
    backup.write_text(json.dumps(backup_value), encoding="utf-8")
    job_failed = data_root / "job.failed"
    job_failed.write_text(
        f"ErrorCode=999\nErrorMessage=failed at {tmp_path}/input.txt\nTraceback: detail\n",
        encoding="utf-8",
    )

    # When: collecting and normalizing the complete oracle observation
    observed = _generate._collect_oracle_observation(tmp_path, None, 1)
    normalized = _generate.normalize_snapshot(observed, roots=(tmp_path,))

    # Then: new full-content fields and the legacy compatibility fields coexist
    assert normalized["invoice_backup"] == backup_value
    assert normalized["invoice_backup_exists"] is True
    assert normalized["job_failed_error_code"] == "ErrorCode=999"
    assert normalized["job_failed_text"] == (
        "ErrorCode=999\nErrorMessage=failed at <RUN_ROOT>/input.txt\nTraceback: detail\n"
    )


def test_source_revision_warning_is_explicit_and_non_failing__tc_gr_003(
    tmp_path: Path,
) -> None:
    """TC-GR-003: stale snapshot provenance produces remediation-rich warning."""
    # Given: one frozen snapshot recorded from a different source revision
    snapshot = tmp_path / "invoice" / "ok.json"
    snapshot.parent.mkdir(parents=True)
    snapshot.write_text(json.dumps({"source": {"commit": "old-revision"}}), encoding="utf-8")

    # When: checking provenance against the executing revision
    warnings = _generate.source_revision_warnings(
        root=tmp_path,
        current_commit="new-revision",
    )

    # Then: the warning names both revisions and embeds the regeneration remedy
    assert warnings == [
        "warning: frozen source.commit old-revision differs from current revision "
        "new-revision; remediation: regenerate all contract snapshots with _generate.py"
    ]


def test_static_input_check_detects_deterministic_manifest_drift__tc_gr_004(
    tmp_path: Path,
) -> None:
    """TC-GR-004: one deterministic input byte change is reported by --check."""
    # Given: a committed-input copy with one deterministic manifest byte changed
    committed = tmp_path / "committed-inputs"
    shutil.copytree(_generate.INPUT_ROOT, committed)
    (committed / "manifest.json").write_text("{}\n", encoding="utf-8")

    # When: rebuilding inputs and comparing deterministic bytes/XLSX values
    mismatches, xlsx_note = _generate.check_static_input_drift(committed)

    # Then: deterministic drift fails explicitly while XLSX policy is documented
    assert any("manifest.json" in mismatch for mismatch in mismatches)
    assert xlsx_note == (
        "xlsx drift check: compared workbook cell values; byte comparison skipped "
        "because openpyxl metadata is nondeterministic"
    )


def test_rdeformat_targets_match_for_ascending_and_descending_discovery__tc_gr_005() -> None:
    """TC-GR-005: opposite scandir orders produce identical normalized targets."""
    # Given: rdeformat statuses produced by opposite first-file discovery orders
    ascending = [
        {"target": "data/temp/0000/raw"},
        {"target": "data/temp/0001/meta"},
    ]
    descending = [
        {"target": "data/temp/0000/structured"},
        {"target": "data/temp/0001/raw"},
    ]

    # When: normalizing both v1 observations through the contract generator
    ascending_normalized = _generate.normalize_snapshot(ascending)
    descending_normalized = _generate.normalize_snapshot(descending)

    # Then: deterministic tile prefixes remain and order-dependent suffixes agree
    expected = [
        {"target": "data/temp/0000/<TILE_SUBDIR>"},
        {"target": "data/temp/0001/<TILE_SUBDIR>"},
    ]
    assert ascending_normalized == expected
    assert descending_normalized == expected
