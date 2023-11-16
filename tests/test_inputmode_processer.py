import json
import os
from pathlib import Path
import shutil
import pytest

from rdetoolkit.modeproc import copy_input_to_rawfile, copy_input_to_rawfile_for_rdeformat, invoice_mode_process, excel_invoice_mode_process, multifile_mode_process, rdeformat_mode_process
from rdetoolkit.models.rde2types import RdeOutputResourcePath, RdeInputDirPaths


@pytest.fixture
def dummy_files_tuple():
    dirname = Path("tests", "input")
    dirname.mkdir(exist_ok=True)
    path1 = dirname.joinpath("dummy1.txt")
    path1.touch()
    path2 = dirname.joinpath("dummy2.txt")
    path2.touch()

    yield tuple([path1, path2])

    if os.path.exists(dirname):
        shutil.rmtree(dirname)


@pytest.fixture
def dummy_files_rdeformat():
    dirnames = ["raw", "main_image", "other_image", "meta", "structured", "logs"]
    rawfiles = []
    for name in dirnames:
        raw = Path("tests", name)
        raw.mkdir(exist_ok=True)
        rawpath = raw.joinpath("dummy.txt")
        rawpath.touch()
        rawfiles.append(rawpath)

    yield tuple(rawfiles)

    for name in dirnames:
        if os.path.exists(Path("tests", name)):
            shutil.rmtree(Path("tests", name))


def test_copy_input_to_rawfile(dummy_files_tuple):
    temp_raw_file_dirname = Path("tests", "raws")
    temp_raw_file_dirname.mkdir(parents=True, exist_ok=True)
    copy_input_to_rawfile(temp_raw_file_dirname, dummy_files_tuple)

    assert len(list(temp_raw_file_dirname.glob("*"))) == 2

    if os.path.exists(Path("tests", "raws")):
        shutil.rmtree(Path("tests", "raws"))


def test_copy_input_to_rawfile_rdeformat(dummy_files_rdeformat):
    temp_raw_file_dirname = Path("tests", "result")
    temp_raw_file_dirname.mkdir(parents=True, exist_ok=True)
    dirnames = ["raw", "main_image", "other_image", "meta", "structured", "logs"]
    for name in dirnames:
        raw = Path("tests", "result", name)
        raw.mkdir(exist_ok=True)

    paths = RdeOutputResourcePath(
        rawfiles=dummy_files_rdeformat,
        raw=Path("tests", "result", "raw"),
        main_image=Path("tests", "result", "main_image"),
        other_image=Path("tests", "result", "other_image"),
        meta=Path("tests", "result", "meta"),
        struct=Path("tests", "result", "structured"),
        logs=Path("tests", "result", "logs"),
        thumbnail=Path(),
        invoice=Path(),
        invoice_org=Path(),
        invoice_schema_json=Path()
    )

    copy_input_to_rawfile_for_rdeformat(paths)

    assert len(list(Path("tests", "result", "raw").glob("*"))) == 1
    assert len(list(Path("tests", "result", "main_image").glob("*"))) == 1
    assert len(list(Path("tests", "result", "other_image").glob("*"))) == 1
    assert len(list(Path("tests", "result", "meta").glob("*"))) == 1
    assert len(list(Path("tests", "result", "structured").glob("*"))) == 1
    assert len(list(Path("tests", "result", "logs").glob("*"))) == 1

    if os.path.exists(Path("tests", "result")):
        shutil.rmtree(Path("tests", "result"))


def test_invoice_mode_process_calls_functions(
    mocker,
    inputfile_single,
    ivnoice_json_none_sample_info,
    tasksupport,
    metadata_def_json_with_feature,
    metadata_json,
    ivnoice_schema_json
):
    """invoiceモード時、invoice上書き、データセット処理、特徴量書き込み
    既存のdescription: desc1を含む
    """
    Path("data", "raw").mkdir(parents=True, exist_ok=True)
    Path("data", "main_image").mkdir(parents=True, exist_ok=True)
    Path("data", "other_image").mkdir(parents=True, exist_ok=True)
    Path("data", "meta").mkdir(parents=True, exist_ok=True)
    Path("data", "structured").mkdir(parents=True, exist_ok=True)
    Path("data", "logs").mkdir(parents=True, exist_ok=True)
    expected_description = "desc1\n特徴量1:test-value1\n特徴量2(V):test-value2\n特徴量3(V):test-value3"
    mock_datasets_process_function = mocker.Mock()

    srcpaths = RdeInputDirPaths(
        inputdata=Path("data", "inputdata"),
        invoice=Path("data", "invoice"),
        tasksupport=Path("data", "tasksupport"))
    resource_paths = RdeOutputResourcePath(
        rawfiles=([Path(inputfile_single),]),
        raw=Path("data", "raw"),
        main_image=Path("data", "main_image"),
        other_image=Path("data", "other_image"),
        meta=Path("data", "meta"),
        struct=Path("data", "structured"),
        logs=Path("data", "logs"),
        thumbnail=Path(),
        invoice=Path("data", "invoice"),
        invoice_org=Path(ivnoice_json_none_sample_info),
        invoice_schema_json=Path(ivnoice_schema_json)
    )

    # テスト対象の処理を実行
    invoice_mode_process(srcpaths, resource_paths, mock_datasets_process_function)

    # 関数が呼び出されたかどうかをチェック
    mock_datasets_process_function.assert_called_once_with(srcpaths, resource_paths)
    # invoiceのバックアップが実行されたかチェック
    assert os.path.exists(os.path.join("data", "invoice", "invoice.json"))
    # descriptionのチェック
    with open(os.path.join("data", "invoice", "invoice.json"), mode="r", encoding="utf-8") as f:
        content = json.load(f)
    assert content['basic']['description'] == expected_description


def test_excel_invoice_mode_process_calls_functions(
    mocker,
    inputfile_single_dummy_header_excelinvoice,
    inputfile_zip_with_file,
    ivnoice_json_with_sample_info,
    tasksupport,
    metadata_def_json_with_feature,
    metadata_json,
    ivnoice_schema_json
):
    """excelinvoiceモード時、invoice上書き、データセット処理、特徴量書き込み
    既存のdescription: desc1を含む
    """
    # 事前準備: フィクスチャ
    Path("data", "raw").mkdir(parents=True, exist_ok=True)
    Path("data", "main_image").mkdir(parents=True, exist_ok=True)
    Path("data", "other_image").mkdir(parents=True, exist_ok=True)
    Path("data", "meta").mkdir(parents=True, exist_ok=True)
    Path("data", "structured").mkdir(parents=True, exist_ok=True)
    Path("data", "logs").mkdir(parents=True, exist_ok=True)
    Path("data", "temp").mkdir(parents=True, exist_ok=True)
    shutil.copy(Path("data", "invoice").joinpath("invoice.json"), Path("data", "temp","invoice_org.json"))
    shutil.unpack_archive(Path("data", "inputdata", "test_input_multi.zip"), Path("data", "temp"))
    expected_description = "特徴量1:test-value1\n特徴量2(V):test-value2\n特徴量3(V):test-value3"

    srcpaths = RdeInputDirPaths(
        inputdata=Path("data", "inputdata"),
        invoice=Path("data", "invoice"),
        tasksupport=Path("data", "tasksupport"))
    resource_paths = RdeOutputResourcePath(
        rawfiles=([Path("data", "temp", "test_child1.txt"),]),
        raw=Path("data", "raw"),
        main_image=Path("data", "main_image"),
        other_image=Path("data", "other_image"),
        meta=Path("data", "meta"),
        struct=Path("data", "structured"),
        logs=Path("data", "logs"),
        thumbnail=Path(),
        invoice=Path("data", "invoice"),
        invoice_org=Path("data", "temp", "invoice_org.json"),
        invoice_schema_json=Path(ivnoice_schema_json)
    )

    # 関数のモック
    mock_datasets_process_function = mocker.Mock()

    # テスト対象の関数を実行
    excel_invoice_mode_process(srcpaths, resource_paths, inputfile_single_dummy_header_excelinvoice, 0, mock_datasets_process_function)

    # 関数が呼び出されたかどうかをチェック
    mock_datasets_process_function.assert_called_once_with(srcpaths, resource_paths)
    # invoiceのバックアップが実行されたかチェック
    # descriptionがバックアップ後に実行されるため内容が一致しない。
    with open(os.path.join("data", "temp", "invoice_org.json"), mode="r", encoding="utf-8") as f:
        contents_backup = json.load(f)
    with open(os.path.join("data", "invoice", "invoice.json"), mode="r", encoding="utf-8") as f:
        contents_origin = json.load(f)
    assert contents_backup != contents_origin
    # descriptionのチェック
    with open(os.path.join("data", "invoice", "invoice.json"), mode="r", encoding="utf-8") as f:
        content = json.load(f)
    assert content['basic']['description'] == expected_description


def test_multifile_mode_process_calls_functions(
    mocker,
    inputfile_multi,
    ivnoice_json_none_sample_info,
    tasksupport,
    metadata_def_json_with_feature,
    metadata_json,
    ivnoice_schema_json
):
    """multifile_mode_processモード時、invoice上書き、データセット処理、特徴量書き込み
    既存のdescription: desc1を含む
    """
    Path("data", "raw").mkdir(parents=True, exist_ok=True)
    Path("data", "main_image").mkdir(parents=True, exist_ok=True)
    Path("data", "other_image").mkdir(parents=True, exist_ok=True)
    Path("data", "meta").mkdir(parents=True, exist_ok=True)
    Path("data", "structured").mkdir(parents=True, exist_ok=True)
    Path("data", "logs").mkdir(parents=True, exist_ok=True)
    Path("data", "temp").mkdir(parents=True, exist_ok=True)
    shutil.copy(Path("data", "invoice").joinpath("invoice.json"), Path("data", "temp", "invoice_org.json"))
    expected_description = "desc1\n特徴量1:test-value1\n特徴量2(V):test-value2\n特徴量3(V):test-value3"
    mock_datasets_process_function = mocker.Mock()

    srcpaths = RdeInputDirPaths(
        inputdata=Path("data", "inputdata"),
        invoice=Path("data", "invoice"),
        tasksupport=Path("data", "tasksupport"))
    resource_paths = RdeOutputResourcePath(
        rawfiles=(inputfile_multi),
        raw=Path("data", "raw"),
        main_image=Path("data", "main_image"),
        other_image=Path("data", "other_image"),
        meta=Path("data", "meta"),
        struct=Path("data", "structured"),
        logs=Path("data", "logs"),
        thumbnail=Path(),
        invoice=Path("data", "invoice"),
        invoice_org=Path("data", "temp", "invoice_org.json"),
        invoice_schema_json=Path(ivnoice_schema_json)
    )

    # テスト対象の処理を実行
    multifile_mode_process(srcpaths, resource_paths, mock_datasets_process_function)

    # 関数が呼び出されたかどうかをチェック
    mock_datasets_process_function.assert_called_once_with(srcpaths, resource_paths)

    # invoiceのバックアップが実行されたかチェック
    # descriptionがバックアップ後に実行されるため内容が一致しない。
    with open(os.path.join("data", "temp", "invoice_org.json"), mode="r", encoding="utf-8") as f:
        contents_backup = json.load(f)
    with open(os.path.join("data", "invoice", "invoice.json"), mode="r", encoding="utf-8") as f:
        contents_origin = json.load(f)
    assert contents_backup != contents_origin

    # rawfileのバックアップが実行されたかチェック
    for file in resource_paths.rawfiles:
        assert os.path.exists(file)

    # descriptionのチェック
    with open(os.path.join("data", "invoice", "invoice.json"), mode="r", encoding="utf-8") as f:
        content = json.load(f)
    assert content['basic']['description'] == expected_description


def test_rdeformat_mode_process_alls_functions(
    mocker,
    inputfile_multi,
    ivnoice_json_none_sample_info,
    tasksupport,
    metadata_def_json_with_feature,
    metadata_json,
    ivnoice_schema_json
):
    """rdeformat_mode_processモード時、invoice上書き、データセット処理、特徴量書き込み
    既存のdescription: desc1を含む
    """
    Path("data", "raw").mkdir(parents=True, exist_ok=True)
    Path("data", "main_image").mkdir(parents=True, exist_ok=True)
    Path("data", "other_image").mkdir(parents=True, exist_ok=True)
    Path("data", "meta").mkdir(parents=True, exist_ok=True)
    Path("data", "structured").mkdir(parents=True, exist_ok=True)
    Path("data", "logs").mkdir(parents=True, exist_ok=True)
    Path("data", "temp").mkdir(parents=True, exist_ok=True)
    shutil.copy(Path("data", "invoice").joinpath("invoice.json"), Path("data", "temp","invoice_org.json"))
    expected_description = "desc1\n特徴量1:test-value1\n特徴量2(V):test-value2\n特徴量3(V):test-value3"
    mock_datasets_process_function = mocker.Mock()

    srcpaths = RdeInputDirPaths(
        inputdata=Path("data", "inputdata"),
        invoice=Path("data", "invoice"),
        tasksupport=Path("data", "tasksupport"))
    resource_paths = RdeOutputResourcePath(
        rawfiles=([Path("data", "inputdata", "test_child1.txt"), Path("data", "inputdata", "test_child2.txt")]),
        raw=Path("data", "raw"),
        main_image=Path("data", "main_image"),
        other_image=Path("data", "other_image"),
        meta=Path("data", "meta"),
        struct=Path("data", "structured"),
        logs=Path("data", "logs"),
        thumbnail=Path(),
        invoice=Path("data", "invoice"),
        invoice_org=Path("data", "temp", "invoice_org.json"),
        invoice_schema_json=Path(ivnoice_schema_json)
    )

    # テスト対象の処理を実行
    rdeformat_mode_process(srcpaths, resource_paths, mock_datasets_process_function)

    # 関数が呼び出されたかどうかをチェック
    mock_datasets_process_function.assert_called_once_with(srcpaths, resource_paths)

    # descriptionのチェック
    with open(os.path.join("data", "invoice", "invoice.json"), mode="r", encoding="utf-8") as f:
        content = json.load(f)
    assert content['basic']['description'] == expected_description
