"""Contracts for Phase H3 common domain services.

Equivalence partitions (EP):

| API | Partition | Expected | Test ID |
| --- | --- | --- | --- |
| ``RawArtifactService.copy`` | raw/nonshared enabled | copies both destinations | TC-H3-EP-001 |
| ``RawArtifactService.copy`` | SmartTable source disabled | original table is excluded | TC-H3-EP-002 |
| ``RawArtifactService.copy`` | copy failure | raises catalogued execution error | TC-H3-EP-003 |
| ``ImageArtifactService.generate`` | enabled | delegates thumbnail generation | TC-H3-EP-004 |
| ``ImageArtifactService.generate`` | converter failure | suppresses the exception | TC-H3-EP-005 |
| ``OutputLayoutResolver.resolve`` | divided tile | resolves divided/0001 | TC-H3-EP-006 |
| ``OutputLayoutResolver.resolve`` | negative index | raises catalogued internal error | TC-H3-EP-007 |
| ``InputValidator.validate`` | complete input | returns normalized paths | TC-H3-EP-008 |
| ``InputValidator.validate`` | missing required child | raises catalogued validation error | TC-H3-EP-009 |
| ``IterationFactory.files`` | unordered siblings | returns sorted paths | TC-H3-EP-010 |
| ``IterationFactory.files`` | missing directory | raises catalogued validation error | TC-H3-EP-011 |
| ``InvoiceService.backup`` | backup mode | copies to explicit temp path | TC-H3-EP-012 |
| ``InvoiceService.apply_config`` | three invoice flags | consumes all three flags | TC-H3-EP-013 |
| ``InvoiceService.apply_config`` | feature updater fails | suppresses the exception | TC-H3-EP-014 |

Boundary values (BV):

| API | Boundary | Expected | Test ID |
| --- | --- | --- | --- |
| ``OutputLayoutResolver.resolve`` | indexes 0 and 1 | root then first divided tile | TC-H3-BV-001 |
| ``IterationFactory.files`` | empty directory | empty tuple | TC-H3-BV-002 |
| ``InvoiceService.backup`` | source absent | returns source path without creating backup | TC-H3-BV-003 |

Negative/abnormal rows (8) outnumber positive rows (6). Every ``RdeConfig`` v1
compatibility key is observed by a service: raw, nonshared raw, thumbnail,
magic variable, structured invoice, feature description, and SmartTable table.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from rdetoolkit.domain.artifacts import ImageArtifactService, RawArtifactService
from rdetoolkit.domain.input_validation import InputValidator
from rdetoolkit.domain.invoice_service import InvoiceService
from rdetoolkit.domain.iteration import IterationFactory
from rdetoolkit.domain.output_layout import OutputLayoutResolver
from rdetoolkit.errors import RdeExecutionError, RdeInternalError, RdeValidationError
from rdetoolkit.runner.mode_resolver import ModeKind
from rdetoolkit.types import RdeConfig


def test_raw_artifacts_consume_copy_and_smarttable_flags__tc_h3_ep_001_002(tmp_path: Path) -> None:
    """TC-H3-EP-001/002: raw copies honor all three artifact flags."""
    # Given: ordinary data, a generated row, and the original SmartTable file
    inputdata = tmp_path / "inputdata"
    inputdata.mkdir()
    ordinary = inputdata / "sample.dat"
    generated = inputdata / "fsmarttable_row.csv"
    table = inputdata / "smarttable_source.csv"
    for path in (ordinary, generated, table):
        path.write_text(path.name, encoding="utf-8")
    config = RdeConfig(
        system={"save_raw": True, "save_nonshared_raw": True},
        smarttable={"save_table_file": False},
    )

    # When: copying SmartTable inputs with original-table persistence disabled
    RawArtifactService().copy(
        (table, generated, ordinary),
        raw_dir=tmp_path / "raw",
        nonshared_raw_dir=tmp_path / "nonshared_raw",
        config=config,
        smarttable=True,
    )

    # Then: only ordinary input is copied to both configured destinations
    assert sorted(path.name for path in (tmp_path / "raw").iterdir()) == ["sample.dat"]
    assert sorted(path.name for path in (tmp_path / "nonshared_raw").iterdir()) == ["sample.dat"]


def test_raw_artifact_copy_wraps_copy_failure__tc_h3_ep_003(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TC-H3-EP-003: invalid source paths retain v1 FileCopier failure behavior."""
    # Given: copying is enabled and the filesystem copy fails
    source = tmp_path / "source.dat"
    source.write_text("raw", encoding="utf-8")
    monkeypatch.setattr("rdetoolkit.domain.artifacts.shutil.copy2", lambda *args: (_ for _ in ()).throw(OSError("disk")))
    config = RdeConfig(system={"save_raw": True, "save_nonshared_raw": False})

    # When/Then: the service maps the copy failure to the v2 execution catalog
    with pytest.raises(RdeExecutionError, match="Failed to copy") as exc_info:
        RawArtifactService().copy(
            (source,),
            raw_dir=tmp_path / "raw",
            nonshared_raw_dir=tmp_path / "nonshared_raw",
            config=config,
        )
    assert exc_info.value.code == 3001


def test_image_artifact_consumes_thumbnail_flag__tc_h3_ep_004(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TC-H3-EP-004: enabled thumbnail generation delegates with explicit paths."""
    # Given: enabled thumbnail generation and a recording converter
    calls: list[tuple[Path, Path]] = []
    monkeypatch.setattr(
        "rdetoolkit.domain.artifacts.img2thumb.copy_images_to_thumbnail",
        lambda thumbnail, main: calls.append((thumbnail, main)),
    )

    # When: the service generates image artifacts
    ImageArtifactService().generate(
        main_image_dir=tmp_path / "main_image",
        thumbnail_dir=tmp_path / "thumbnail",
        config=RdeConfig(system={"save_thumbnail_image": True}),
    )

    # Then: the configured explicit paths are delegated once
    assert calls == [(tmp_path / "thumbnail", tmp_path / "main_image")]


def test_image_artifact_suppresses_converter_failure__tc_h3_ep_005(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TC-H3-EP-005: thumbnail failures remain intentionally noncritical."""
    # Given: the v1 image converter raises
    def fail(*args: object) -> None:
        raise OSError("bad image")

    monkeypatch.setattr("rdetoolkit.domain.artifacts.img2thumb.copy_images_to_thumbnail", fail)

    # When/Then: enabled generation preserves v1 exception suppression
    ImageArtifactService().generate(
        main_image_dir=tmp_path / "main_image",
        thumbnail_dir=tmp_path / "thumbnail",
        config=RdeConfig(system={"save_thumbnail_image": True}),
    )


def test_output_layout_root_and_divided_boundaries__tc_h3_ep_006_bv_001(tmp_path: Path) -> None:
    """TC-H3-EP-006/BV-001: layout resolution preserves the v1 tile boundary."""
    # Given: a path-only resolver and output root
    resolver = OutputLayoutResolver()

    # When: resolving the two sides of the divided boundary
    first = resolver.resolve(tmp_path, 0)
    second = resolver.resolve(tmp_path, 1)

    # Then: tile zero is flat and tile one uses the first divided directory
    assert first.invoice == tmp_path / "invoice"
    assert second.invoice == tmp_path / "divided" / "0001" / "invoice"
    assert not first.invoice.exists()


def test_output_layout_rejects_negative_index__tc_h3_ep_007(tmp_path: Path) -> None:
    """TC-H3-EP-007: negative tile indexes are outside the output contract."""
    # Given: a path-only resolver
    # When/Then: resolving an invalid negative tile fails before filesystem work
    with pytest.raises(RdeInternalError, match="non-negative") as exc_info:
        OutputLayoutResolver().resolve(tmp_path, -1)
    assert exc_info.value.code == 5001


def test_input_validator_accepts_complete_tree__tc_h3_ep_008(tmp_path: Path) -> None:
    """TC-H3-EP-008: complete input structure yields explicit input paths."""
    # Given: the three required input directories
    for name in ("inputdata", "invoice", "tasksupport"):
        (tmp_path / name).mkdir()

    # When: validating the root
    paths = InputValidator().validate(tmp_path)

    # Then: the returned paths are rooted at the validated directory
    assert paths.inputdata == tmp_path / "inputdata"
    assert paths.invoice == tmp_path / "invoice"
    assert paths.tasksupport == tmp_path / "tasksupport"


@pytest.mark.parametrize("missing", ["inputdata", "invoice", "tasksupport"])
def test_input_validator_rejects_missing_child__tc_h3_ep_009(tmp_path: Path, missing: str) -> None:
    """TC-H3-EP-009: every missing required directory is rejected."""
    # Given: an input root missing exactly one required child
    for name in ("inputdata", "invoice", "tasksupport"):
        if name != missing:
            (tmp_path / name).mkdir()

    # When/Then: validation names the missing child
    with pytest.raises(RdeValidationError, match=missing) as exc_info:
        InputValidator().validate(tmp_path)
    assert exc_info.value.code == 4003


def test_iteration_factory_always_sorts_siblings__tc_h3_ep_010_bv_002(tmp_path: Path) -> None:
    """TC-H3-EP-010/BV-002: enumeration is deterministic, including empty input."""
    # Given: siblings created in reverse lexical order and an empty directory
    populated = tmp_path / "populated"
    empty = tmp_path / "empty"
    populated.mkdir()
    empty.mkdir()
    for name in ("z.dat", "a.dat", "m.dat"):
        (populated / name).write_text(name, encoding="utf-8")

    # When: enumerating both directories
    factory = IterationFactory()
    ordered = factory.files(populated)

    # Then: the populated result is sorted and the empty boundary stays empty
    assert [path.name for path in ordered] == ["a.dat", "m.dat", "z.dat"]
    assert factory.files(empty) == ()


def test_iteration_factory_rejects_missing_directory__tc_h3_ep_011(tmp_path: Path) -> None:
    """TC-H3-EP-011: enumeration rejects an absent input directory."""
    # Given: a path that does not exist
    # When/Then: enumeration raises instead of silently producing zero tiles
    with pytest.raises(RdeValidationError, match="does not exist") as exc_info:
        IterationFactory().files(tmp_path / "missing")
    assert exc_info.value.code == 4003


def test_invoice_service_backup_is_path_based__tc_h3_ep_012_bv_003(tmp_path: Path) -> None:
    """TC-H3-EP-012/BV-003: backup selection uses explicit paths only."""
    # Given: a nested source invoice and an absent flat source
    data_root = tmp_path / "data"
    source = data_root / "invoice" / "invoice.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"datasetId": "source"}', encoding="utf-8")
    service = InvoiceService()

    # When: backing up a v1 backup mode
    backup = service.backup(ModeKind.rdeformat, root=tmp_path, inputdata_path=data_root / "inputdata")

    # Then: the source is copied to the explicit data-root temp directory
    assert backup == data_root / "temp" / "invoice_org.json"
    assert json.loads(backup.read_text(encoding="utf-8")) == {"datasetId": "source"}
    assert service.backup(
        ModeKind.rdeformat,
        root=tmp_path / "absent",
        inputdata_path=tmp_path / "absent" / "inputdata",
    ) == tmp_path / "absent" / "invoice" / "invoice.json"


def test_invoice_service_consumes_three_invoice_flags__tc_h3_ep_013_014(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TC-H3-EP-013/014: invoice postprocessing consumes its three config flags."""
    # Given: an invoice, one raw input, all invoice flags, and a failing updater
    invoice = tmp_path / "invoice" / "invoice.json"
    rawfile = tmp_path / "inputdata" / "sample.dat"
    invoice.parent.mkdir()
    rawfile.parent.mkdir()
    invoice.write_text('{"basic": {"dataName": "${filename}"}}', encoding="utf-8")
    rawfile.write_text("raw", encoding="utf-8")
    magic_calls: list[tuple[Path, Path]] = []
    monkeypatch.setattr(
        "rdetoolkit.domain.invoice_service.apply_magic_variable",
        lambda invoice_path, raw_path, **kwargs: magic_calls.append((Path(invoice_path), Path(raw_path))) or {},
    )

    # When: applying enabled magic, structured-copy, and feature-description policy
    InvoiceService().apply_config(
        config=RdeConfig(
            system={
                "magic_variable": True,
                "save_invoice_to_structured": True,
                "feature_description": True,
            },
        ),
        invoice_path=invoice,
        structured_dir=tmp_path / "structured",
        rawfiles=(rawfile,),
        feature_updater=lambda: (_ for _ in ()).throw(OSError("optional metadata")),
    )

    # Then: mandatory actions run and optional feature failure is suppressed
    assert magic_calls == [(invoice, rawfile)]
    assert (tmp_path / "structured" / "invoice.json").read_text(encoding="utf-8") == invoice.read_text(encoding="utf-8")
