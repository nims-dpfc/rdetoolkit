"""Build Phase G contract fixtures from the v1 runtime oracle.

Source tag: v2.0.0a1; source commit: 8db74fa.
Generated on: 2026-07-15. Re-run this script; never hand-edit snapshots.

The generator owns both static input construction and expected-output
freezing. Expected values are observed from isolated v1 executions, then
normalized before comparison or persistence. Tests may execute v1 as the
subject under test, but they must never use v1 to create expected values.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from tests.fixtures.excelinvoice import (  # noqa: E402
    EXCELINVOICE_ENTRYDATA_SHEET1_MULTI,
    EXCELINVOICE_ENTRYDATA_SHEET2,
    EXCELINVOICE_ENTRYDATA_SHEET3,
)

SOURCE_TAG = "v2.0.0a1"
SOURCE_COMMIT = "8db74fa"
GENERATED_ON = "2026-07-15"

FIXTURE_ROOT = Path(__file__).resolve().parent
INPUT_ROOT = FIXTURE_ROOT / "inputs"
EXPECTED_ROOT = FIXTURE_ROOT / "expected" / "v1"

_SEED_INVOICE = {
    "datasetId": "seed-dataset",
    "basic": {
        "dateSubmitted": "2026-07-15",
        "dataOwnerId": "0" * 56,
        "dataName": "seed",
    },
}
_EMPTY_METADATA_DEF = {"constant": {}, "variable": []}

_KEY_PLACEHOLDERS = {
    "run_id": "<RUN_ID>",
    "started_at": "<TIMESTAMP>",
    "finished_at": "<TIMESTAMP>",
    "timestamp": "<TIMESTAMP>",
    "emitted_at": "<TIMESTAMP>",
    "duration_ms": "<DURATION_MS>",
    "config_digest": "<CONFIG_DIGEST>",
    "traceback": "<TRACEBACK>",
    "stacktrace": "<TRACEBACK>",
    "dateSubmitted": "<DATE>",
}
_VERSION_PATTERN = re.compile(r"(?m)^rdetoolkit==[^\s]+$")


def _normalize_string(value: str, roots: Sequence[Path]) -> str:
    """Replace volatile path and installed-version text in a string."""
    normalized = value
    for root in sorted((path.resolve() for path in roots), key=lambda path: len(str(path)), reverse=True):
        normalized = normalized.replace(str(root), "<RUN_ROOT>")
    return _VERSION_PATTERN.sub("rdetoolkit==<VERSION>", normalized)


def normalize_snapshot(
    value: Any,
    *,
    roots: Sequence[Path] = (),
    _key: str | None = None,
) -> Any:
    """Return a JSON-compatible value with contract volatility normalized.

    Args:
        value: Arbitrarily nested JSON-compatible source value.
        roots: Isolated execution roots to replace with ``<RUN_ROOT>``.

    Returns:
        A recursively normalized JSON-compatible value.
    """
    if _key in _KEY_PLACEHOLDERS:
        return _KEY_PLACEHOLDERS[_key]

    if isinstance(value, Mapping):
        return {
            str(key): normalize_snapshot(item, roots=roots, _key=str(key))
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [normalize_snapshot(item, roots=roots) for item in value]
    if isinstance(value, Path):
        return _normalize_string(str(value), roots)
    if isinstance(value, str):
        return _normalize_string(value, roots)
    return value


def _canonical_json(value: Any) -> str:
    """Serialize a snapshot deterministically."""
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def write_json_snapshot(path: Path, value: Any) -> None:
    """Write a canonical UTF-8 JSON snapshot.

    Args:
        path: Destination below the contract fixture directory.
        value: JSON-compatible normalized value.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_canonical_json(value), encoding="utf-8", newline="\n")


def compare_snapshot(path: Path, value: Any) -> str | None:
    """Compare a candidate with a frozen snapshot without modifying files.

    Args:
        path: Existing frozen snapshot.
        value: Newly generated and normalized candidate.

    Returns:
        ``None`` on equality, otherwise a concise mismatch description.
    """
    if not path.exists():
        return f"missing frozen snapshot: {path.name}"
    expected = path.read_text(encoding="utf-8")
    candidate = _canonical_json(value)
    if expected == candidate:
        return None
    return f"snapshot differs: {path.name}"


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_canonical_json(value), encoding="utf-8", newline="\n")


def _build_data_layout(
    mode_root: Path,
    *,
    invoice: Mapping[str, Any] = _SEED_INVOICE,
    schema: Mapping[str, Any] | None = None,
    metadata_def: Mapping[str, Any] = _EMPTY_METADATA_DEF,
) -> Path:
    data_root = mode_root / "data"
    for name in ("inputdata", "invoice", "tasksupport", "unpacked"):
        (data_root / name).mkdir(parents=True, exist_ok=True)
    _write_json(data_root / "invoice" / "invoice.json", invoice)
    _write_json(
        data_root / "tasksupport" / "invoice.schema.json",
        {"properties": {}} if schema is None else schema,
    )
    _write_json(data_root / "tasksupport" / "metadata-def.json", metadata_def)
    return data_root


def _write_deterministic_zip(path: Path, members: Mapping[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for member_name, content in sorted(members.items()):
            info = zipfile.ZipInfo(member_name, date_time=(2026, 7, 15, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content.encode())


def _excelinvoice_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "required": ["custom", "sample"],
        "properties": {
            "custom": {
                "type": "object",
                "label": {"ja": "固有情報", "en": "Custom Information"},
                "required": ["key1"],
                "properties": {
                    "key1": {
                        "type": "string",
                        "label": {"ja": "キー1", "en": "Key 1"},
                    },
                    "key2": {
                        "type": "string",
                        "label": {"ja": "キー2", "en": "Key 2"},
                    },
                },
            },
            "sample": {
                "type": "object",
                "label": {"ja": "試料情報", "en": "Sample Information"},
                "properties": {},
            },
        },
    }


def _write_excelinvoice(path: Path, *, zero_rows: bool) -> None:
    sheet2 = pd.DataFrame(
        EXCELINVOICE_ENTRYDATA_SHEET2,
        columns=["term_id", "key_name"],
    )
    sheet3 = pd.DataFrame(
        EXCELINVOICE_ENTRYDATA_SHEET3,
        columns=["sample_class_id", "term_id", "key_name"],
    )
    with pd.ExcelWriter(path) as writer:
        if not zero_rows:
            source_rows = EXCELINVOICE_ENTRYDATA_SHEET1_MULTI[3:]
            owner_id = "0" * 56
            derived_rows = [
                ["", "basic", "basic"],
                ["name", "dataName", "dataOwnerId"],
                ["Input filename", "Data name", "Data owner ID"],
                *[[row[0], row[4], owner_id] for row in source_rows],
            ]
            sheet1 = pd.DataFrame(
                derived_rows,
                columns=["invoiceList_format_id", "Sample_RDE_DataSet", ""],
            )
            sheet1.to_excel(writer, sheet_name="invoice_form", index=False)
        sheet2.to_excel(writer, sheet_name="generalTerm", index=False)
        sheet3.to_excel(writer, sheet_name="specificTerm", index=False)


def _build_excelinvoice_inputs(destination: Path) -> dict[str, Any]:
    data_root = _build_data_layout(destination)
    inputdata = data_root / "inputdata"
    _write_excelinvoice(inputdata / "excelinvoice_multi.xlsx", zero_rows=False)
    _write_excelinvoice(inputdata / "excelinvoice_zero_rows.xlsx", zero_rows=True)
    _write_deterministic_zip(
        destination / "excelinvoice_files.zip",
        {
            "test_child1.txt": "excelinvoice child 1\n",
            "test_child2.txt": "excelinvoice child 2\n",
        },
    )
    return {
        "multi_workbook": "data/inputdata/excelinvoice_multi.xlsx",
        "zero_row_workbook": "data/inputdata/excelinvoice_zero_rows.xlsx",
        "raw_archive": "excelinvoice_files.zip",
        "source_rows": "tests/fixtures/excelinvoice.py:EXCELINVOICE_ENTRYDATA_SHEET1_MULTI",
    }


def _build_multidatatile_inputs(destination: Path) -> dict[str, Any]:
    data_root = _build_data_layout(destination)
    inputdata = data_root / "inputdata"
    (inputdata / "tile_00.txt").write_text("first tile\n", encoding="utf-8")
    (inputdata / "tile_日本語.txt").write_text("二番目のタイル\n", encoding="utf-8")
    return {
        "files": [
            "data/inputdata/tile_00.txt",
            "data/inputdata/tile_日本語.txt",
        ],
        "expected_tree": "../../expected/multidatatile/ok.json",
    }


def _build_rdeformat_inputs(destination: Path) -> dict[str, Any]:
    data_root = _build_data_layout(destination)
    archive_path = data_root / "inputdata" / "rdeformat_sample.zip"
    _write_deterministic_zip(
        archive_path,
        {
            "0000/raw/first.txt": "first RDE tile\n",
            "0000/structured/result.csv": "x,y\n1,2\n",
            "0001/raw/日本語データ.txt": "日本語のRDEデータ\n",
            "0001/meta/metadata.json": '{"constant": {}, "variable": []}\n',
        },
    )
    return {"archive": "data/inputdata/rdeformat_sample.zip"}


def _smarttable_schema() -> dict[str, Any]:
    schema_path = REPOSITORY_ROOT / "tests" / "samplefile" / "invoice.schema.json"
    return json.loads(schema_path.read_text(encoding="utf-8"))


def _smarttable_invoice() -> dict[str, Any]:
    invoice_path = REPOSITORY_ROOT / "tests" / "samplefile" / "invoice.json"
    invoice = json.loads(invoice_path.read_text(encoding="utf-8"))
    invoice["basic"]["description"] = ""
    return invoice


def _smarttable_rows() -> list[list[Any]]:
    general_term = "3adf9874-7bcb-e5f8-99cb-3d6fd9d7b55e"
    class_id = "01cb3c01-37a4-5a43-d8ca-f523ca99a75b"
    specific_term = "3250c45d-0ed6-1438-43b5-eb679918604a"
    return [
        [
            "Data name", "Measured date", "Numeric value", "General attribute",
            "Specific attribute", "Sample name", "Description", "Comment",
            "Temperature", "Mapped input file",
        ],
        [
            "basic/dataName", "custom/sample1", "custom/sample2",
            f"sample/generalAttributes.{general_term}",
            f"sample/specificAttributes.{class_id}.{specific_term}",
            "sample/names", "sample/description", "meta/comment",
            "meta/temperature", "inputdata1",
        ],
        [
            "smarttable_value_0", date(2026, 7, 15), 1,
            "general-a", "specific-a", "sample-a", "first row", "memo-a",
            20.5, "measurements/row0.txt",
        ],
        [
            "smarttable_value_1", date(2026, 7, 16), 2.5,
            "general-b", "specific-b", "sample-b", "", "memo-b",
            21, "測定/行1.txt",
        ],
        [
            "smarttable_value_2", date(2026, 7, 17), 3,
            "", "specific-c", "sample-c", "third row", "", "",
            "",
        ],
    ]


def _build_smarttable_inputs(destination: Path) -> dict[str, Any]:
    metadata_def = {
        "comment": {
            "name": {"ja": "コメント", "en": "Comment"},
            "schema": {"type": "string"},
        },
        "temperature": {
            "name": {"ja": "温度", "en": "Temperature"},
            "schema": {"type": "number"},
            "unit": "C",
        },
    }
    data_root = _build_data_layout(
        destination,
        invoice=_smarttable_invoice(),
        schema=_smarttable_schema(),
        metadata_def=metadata_def,
    )
    rows = pd.DataFrame(_smarttable_rows())
    xlsx_path = data_root / "inputdata" / "smarttable_full.xlsx"
    rows.to_excel(xlsx_path, index=False, header=False)
    csv_path = destination / "smarttable_full.csv"
    pd.read_excel(xlsx_path, header=None).to_csv(csv_path, index=False, header=False)
    _write_deterministic_zip(
        data_root / "inputdata" / "smarttable_inputs.zip",
        {
            "measurements/row0.txt": "row zero measurement\n",
            "測定/行1.txt": "行1の測定\n",
        },
    )
    return {
        "workbook": "data/inputdata/smarttable_full.xlsx",
        "csv_equivalent": "smarttable_full.csv",
        "file_archive": "data/inputdata/smarttable_inputs.zip",
        "rows": 3,
    }


def _build_invoice_references(destination: Path) -> dict[str, Any]:
    destination.mkdir(parents=True, exist_ok=True)
    references = [
        "tests/samplefile/invoice.json",
        "tests/samplefile/invoice.schema.json",
        "tests/samplefile/invoice.schema.full.json",
        "tests/samplefile/invoice.schema.basic.json",
    ]
    registry = {"references": references}
    _write_json(destination / "registered_references.json", registry)
    return registry


def build_static_inputs(destination: Path = INPUT_ROOT) -> dict[str, dict[str, Any]]:
    """Build all five mode input families below ``destination``.

    Args:
        destination: Root for generated input fixtures.

    Returns:
        Mode-keyed manifest describing generated files and registered assets.
    """
    destination.mkdir(parents=True, exist_ok=True)
    manifest = {
        "invoice": _build_invoice_references(destination / "invoice"),
        "excelinvoice": _build_excelinvoice_inputs(destination / "excelinvoice"),
        "multidatatile": _build_multidatatile_inputs(destination / "multidatatile"),
        "rdeformat": _build_rdeformat_inputs(destination / "rdeformat"),
        "smarttable": _build_smarttable_inputs(destination / "smarttable"),
    }
    _write_json(destination / "manifest.json", manifest)
    return manifest


def expected_snapshot_paths(root: Path = EXPECTED_ROOT) -> list[Path]:
    """Return the complete frozen v1 snapshot inventory."""
    modes = ("invoice", "excelinvoice", "multidatatile", "rdeformat", "smarttable")
    outcomes = ("ok", "usererr", "valerr")
    snapshots = [root / mode / f"{outcome}.json" for mode in modes for outcome in outcomes]
    snapshots.append(root / "excelinvoice" / "zero_rows.json")
    return snapshots


def _materialize_oracle_case(mode: str, root: Path, *, zero_rows: bool = False) -> None:
    if mode == "invoice":
        data_root = _build_data_layout(root)
        (data_root / "inputdata" / "invoice_input.txt").write_text(
            "invoice input\n",
            encoding="utf-8",
        )
        return

    shutil.copytree(INPUT_ROOT / mode / "data", root / "data")
    if mode == "excelinvoice":
        _select_excelinvoice_case(root, zero_rows=zero_rows)


def _select_excelinvoice_case(root: Path, *, zero_rows: bool) -> None:
    inputdata = root / "data" / "inputdata"
    selected_name = "excelinvoice_zero_rows.xlsx" if zero_rows else "excelinvoice_multi.xlsx"
    for workbook in inputdata.glob("*.xlsx"):
        if workbook.name != selected_name:
            workbook.unlink()
    (inputdata / selected_name).rename(inputdata / "contract_excel_invoice.xlsx")
    shutil.copy2(
        INPUT_ROOT / "excelinvoice" / "excelinvoice_files.zip",
        inputdata / "excelinvoice_files.zip",
    )


def _invalidate_invoice(root: Path) -> None:
    invoice_path = root / "data" / "invoice" / "invoice.json"
    invoice = json.loads(invoice_path.read_text(encoding="utf-8"))
    invoice["basic"] = None
    _write_json(invoice_path, invoice)


def _oracle_config(mode: str) -> Any:
    from rdetoolkit.models.config import (  # noqa: PLC0415
        Config,
        MultiDataTileSettings,
        SmartTableSettings,
        SystemSettings,
    )

    extended_mode = {
        "multidatatile": "MultiDataTile",
        "rdeformat": "rdeformat",
    }.get(mode)
    return Config(
        system=SystemSettings(
            extended_mode=extended_mode,
            save_raw=True,
            save_nonshared_raw=True,
            save_thumbnail_image=False,
            magic_variable=False,
        ),
        multidata_tile=MultiDataTileSettings(ignore_errors=False),
        smarttable=SmartTableSettings(save_table_file=False),
    )


def _record_callback_call() -> None:
    marker = Path(".callback_calls")
    with marker.open("a", encoding="utf-8") as stream:
        stream.write("called\n")


def _oracle_callback_ok(srcpaths: object, resource_paths: object) -> None:
    del srcpaths, resource_paths
    _record_callback_call()


def _oracle_callback_usererr(srcpaths: object, resource_paths: object) -> None:
    from rdetoolkit.exceptions import StructuredError  # noqa: PLC0415

    del srcpaths, resource_paths
    _record_callback_call()
    message = (
        "Contract callback failed. Remediation: inspect the fixture callback "
        "and correct its input."
    )
    raise StructuredError(message, ecode=999)


def _normalize_output_path(path: str) -> str:
    return re.sub(
        r"rdesys_\d{8}_\d{6}\.log",
        "rdesys_<LOG_TIMESTAMP>.log",
        path,
    )


def _output_tree(data_root: Path) -> dict[str, list[str]]:
    directories = sorted(
        _normalize_output_path(path.relative_to(data_root.parent).as_posix()) + "/"
        for path in data_root.rglob("*")
        if path.is_dir()
    )
    files = sorted(
        _normalize_output_path(path.relative_to(data_root.parent).as_posix())
        for path in data_root.rglob("*")
        if path.is_file()
    )
    return {"directories": directories, "files": files}


def _invoice_outputs(data_root: Path) -> dict[str, Any]:
    outputs: dict[str, Any] = {}
    for path in sorted(data_root.rglob("invoice/invoice.json")):
        relative = path.relative_to(data_root.parent).as_posix()
        outputs[relative] = json.loads(path.read_text(encoding="utf-8"))
    return outputs


def _raw_hashes(data_root: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(data_root.rglob("*")):
        if not path.is_file() or not {"raw", "nonshared_raw"}.intersection(path.parts):
            continue
        relative = path.relative_to(data_root.parent).as_posix()
        hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def _read_legacy_return(value: str | None) -> Any:
    if value is None:
        return None
    return json.loads(value)


def _collect_oracle_observation(root: Path, result: str | None, exit_code: int) -> dict[str, Any]:
    data_root = root / "data"
    job_failed = data_root / "job.failed"
    callback_marker = root / ".callback_calls"
    callback_count = (
        len(callback_marker.read_text(encoding="utf-8").splitlines())
        if callback_marker.exists() else 0
    )
    job_failed_error_code = (
        job_failed.read_text(encoding="utf-8").splitlines()[0]
        if job_failed.exists() else None
    )
    return {
        "exit_code": exit_code,
        "callback_count": callback_count,
        "legacy_return": _read_legacy_return(result),
        "output_tree": _output_tree(data_root),
        "invoices": _invoice_outputs(data_root),
        "raw_sha256": _raw_hashes(data_root),
        "job_failed_error_code": job_failed_error_code,
        "invoice_backup_exists": (data_root / "temp" / "invoice_org.json").exists(),
    }


def _run_oracle_worker(mode: str, outcome: str, root: Path) -> int:
    from rdetoolkit.workflows import run as v1_run  # noqa: PLC0415

    if outcome == "valerr":
        _invalidate_invoice(root)
    callback = _oracle_callback_usererr if outcome == "usererr" else _oracle_callback_ok
    previous = Path.cwd()
    result: str | None = None
    exit_code = 0
    try:
        os.chdir(root)
        try:
            result = v1_run(
                custom_dataset_function=callback,
                config=_oracle_config(mode),
            )
        except SystemExit as error:
            exit_code = int(error.code or 0)
    finally:
        os.chdir(previous)
    observation = _collect_oracle_observation(root, result, exit_code)
    _write_json(root / ".oracle_observation.json", observation)
    return 0


def _observe_v1(mode: str, outcome: str, *, zero_rows: bool = False) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix=f"rdetoolkit-g1-{mode}-") as temporary:
        root = Path(temporary)
        _materialize_oracle_case(mode, root, zero_rows=zero_rows)
        command = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--oracle-worker",
            mode,
            outcome,
            str(root),
        ]
        completed = subprocess.run(  # noqa: S603
            command,
            cwd=REPOSITORY_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        observation_path = root / ".oracle_observation.json"
        if completed.returncode != 0 or not observation_path.exists():
            message = (
                f"v1 oracle worker failed for {mode}/{outcome}: "
                f"exit={completed.returncode}; stderr={completed.stderr[-1000:]}"
            )
            raise RuntimeError(message)
        observation = json.loads(observation_path.read_text(encoding="utf-8"))
        return normalize_snapshot(observation, roots=(root,))


def materialize_sut_case(mode: str, root: Path) -> None:
    """Copy a committed mode input into an isolated SUT working directory."""
    _materialize_oracle_case(mode, root)


def run_v1_sut(mode: str, outcome: str) -> dict[str, Any]:
    """Execute v1 as the SUT and return a normalized observation.

    Expected values are deliberately not read or written here. Contract tests
    compare this observation with already-frozen JSON snapshots.
    """
    return _observe_v1(mode, outcome)


def _snapshot_case_from_path(path: Path) -> tuple[str, str, bool]:
    mode = path.parent.name
    outcome = path.stem
    zero_rows = outcome == "zero_rows"
    return mode, "ok" if zero_rows else outcome, zero_rows


def freeze_expected_outputs(*, check: bool) -> list[str]:
    """Observe every v1 scenario and write or compare normalized snapshots."""
    mismatches: list[str] = []
    for path in expected_snapshot_paths():
        mode, outcome, zero_rows = _snapshot_case_from_path(path)
        payload = {
            "source": {"tag": SOURCE_TAG, "commit": SOURCE_COMMIT},
            "case": {
                "mode": mode,
                "outcome": "zero_rows" if zero_rows else outcome,
                "entry": "custom_dataset_function",
            },
            "observed": _observe_v1(mode, outcome, zero_rows=zero_rows),
        }
        if check:
            mismatch = compare_snapshot(path, payload)
            if mismatch is not None:
                mismatches.append(f"{mode}/{path.stem}: {mismatch}")
        else:
            write_json_snapshot(path, payload)
    return mismatches


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="regenerate normalized expectations in isolation and compare only",
    )
    parser.add_argument("--oracle-worker", nargs=3, metavar=("MODE", "OUTCOME", "ROOT"), help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> int:
    """Run fixture generation or deterministic comparison."""
    args = _parse_args()
    if args.oracle_worker is not None:
        mode, outcome, root = args.oracle_worker
        return _run_oracle_worker(mode, outcome, Path(root))
    if args.check:
        mismatches = freeze_expected_outputs(check=True)
        if mismatches:
            print("\n".join(mismatches), file=sys.stderr)  # noqa: T201
            return 1
        print("all normalized v1 snapshots match frozen expectations")  # noqa: T201
        return 0
    manifest = build_static_inputs()
    freeze_expected_outputs(check=False)
    message = f"built inputs and froze v1 outputs for {', '.join(sorted(manifest))}"
    print(message)  # noqa: T201
    return 0


if __name__ == "__main__":
    main()
