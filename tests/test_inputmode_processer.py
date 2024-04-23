import json
import os
import shutil
from pathlib import Path

import pytest
from rdetoolkit.models.rde2types import RdeInputDirPaths, RdeOutputResourcePath
from rdetoolkit.modeproc import (
    copy_input_to_rawfile,
    copy_input_to_rawfile_for_rdeformat,
    excel_invoice_mode_process,
    invoice_mode_process,
    multifile_mode_process,
    rdeformat_mode_process,
)
from rdetoolkit.config import Config


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
    dirnames = ["raw", "main_image", "other_image", "meta", "structured", "logs", "nonshared_raw"]
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


@pytest.fixture
def invoice_json_with_desc():
    Path("data", "invoice").mkdir(parents=True, exist_ok=True)
    test_invoice_file = Path("data", "invoice").joinpath("invoice.json")
    shutil.copy(os.path.join(os.path.dirname(__file__), "samplefile", "invoice.json"), test_invoice_file)
    yield test_invoice_file

    if test_invoice_file.exists():
        test_invoice_file.unlink()


@pytest.fixture
def invoice_shcema_json_full():
    test_shcema_invoice_file = Path("data", "tasksupport").joinpath("invoice.schema.json")
    shutil.copy(os.path.join(os.path.dirname(__file__), "samplefile", "invoice.schema.json"), test_shcema_invoice_file)
    yield test_shcema_invoice_file

    if test_shcema_invoice_file.exists():
        test_shcema_invoice_file.unlink()


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
    dirnames = ["raw", "main_image", "other_image", "meta", "structured", "logs", "nonshared_raw"]
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
        invoice_schema_json=Path(),
        nonshared_raw=Path("tests", "result", "nonshared_raw")
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
    ivnoice_schema_json_none_sample,
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
        tasksupport=Path("data", "tasksupport"),
    )
    resource_paths = RdeOutputResourcePath(
        rawfiles=(
            [
                Path(inputfile_single),
            ]
        ),
        raw=Path("data", "raw"),
        main_image=Path("data", "main_image"),
        other_image=Path("data", "other_image"),
        meta=Path("data", "meta"),
        struct=Path("data", "structured"),
        logs=Path("data", "logs"),
        thumbnail=Path(),
        invoice=Path("data", "invoice"),
        invoice_org=Path(ivnoice_json_none_sample_info),
        invoice_schema_json=Path(ivnoice_schema_json_none_sample),
    )

    # テスト対象の処理を実行
    config = Config(extendeds_mode=None, save_raw=True, magic_variable=False, save_thumbnail_image=True)
    invoice_mode_process(srcpaths, resource_paths, mock_datasets_process_function, config=config)

    # 関数が呼び出されたかどうかをチェック
    mock_datasets_process_function.assert_called_once_with(srcpaths, resource_paths)
    # invoiceのバックアップが実行されたかチェック
    assert os.path.exists(os.path.join("data", "invoice", "invoice.json"))
    # descriptionのチェック
    with open(os.path.join("data", "invoice", "invoice.json"), encoding="utf-8") as f:
        content = json.load(f)
    assert content["basic"]["description"] == expected_description


def test_invoice_mode_process_calls_functions_with_magic_variable(
    mocker,
    inputfile_single,
    ivnoice_json_magic_filename_variable,
    tasksupport,
    metadata_def_json_with_feature,
    metadata_json,
    ivnoice_schema_json,
):
    """invoiceモード時、invoice上書き、データセット処理、${filename}書き換え
    invoice.jsonに記載された${filename}が書き換えられるかテスト
    """
    Path("data", "raw").mkdir(parents=True, exist_ok=True)
    Path("data", "main_image").mkdir(parents=True, exist_ok=True)
    Path("data", "other_image").mkdir(parents=True, exist_ok=True)
    Path("data", "meta").mkdir(parents=True, exist_ok=True)
    Path("data", "structured").mkdir(parents=True, exist_ok=True)
    Path("data", "logs").mkdir(parents=True, exist_ok=True)
    mock_datasets_process_function = mocker.Mock()

    srcpaths = RdeInputDirPaths(
        inputdata=Path("data", "inputdata"),
        invoice=Path("data", "invoice"),
        tasksupport=Path("data", "tasksupport"),
    )
    resource_paths = RdeOutputResourcePath(
        rawfiles=(
            [
                Path(inputfile_single),
            ]
        ),
        raw=Path("data", "raw"),
        main_image=Path("data", "main_image"),
        other_image=Path("data", "other_image"),
        meta=Path("data", "meta"),
        struct=Path("data", "structured"),
        logs=Path("data", "logs"),
        thumbnail=Path(),
        invoice=Path("data", "invoice"),
        invoice_org=Path(ivnoice_json_magic_filename_variable),
        invoice_schema_json=Path(ivnoice_schema_json),
    )

    # テスト対象の処理を実行
    config = Config(extendeds_mode=None, save_raw=True, magic_variable=True, save_thumbnail_image=True)
    invoice_mode_process(srcpaths, resource_paths, mock_datasets_process_function, config=config)

    # 関数が呼び出されたかどうかをチェック
    mock_datasets_process_function.assert_called_once_with(srcpaths, resource_paths)
    # invoiceのバックアップが実行されたかチェック
    assert os.path.exists(os.path.join("data", "invoice", "invoice.json"))
    # descriptionのチェック
    with open(os.path.join("data", "invoice", "invoice.json"), encoding="utf-8") as f:
        content = json.load(f)
    assert content["basic"]["dataName"] == "test_single.txt"


def test_excel_invoice_mode_process_calls_functions(
    mocker,
    inputfile_single_dummy_header_excelinvoice,
    inputfile_zip_with_file,
    ivnoice_json_with_sample_info,
    tasksupport,
    metadata_def_json_with_feature,
    metadata_json,
    ivnoice_schema_json_none_specificAttributes,
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
    shutil.copy(
        Path("data", "invoice").joinpath("invoice.json"),
        Path("data", "temp", "invoice_org.json"),
    )
    shutil.unpack_archive(Path("data", "inputdata", "test_input_multi.zip"), Path("data", "temp"))
    expected_description = "desc1\n特徴量1:test-value1\n特徴量2(V):test-value2\n特徴量3(V):test-value3"

    srcpaths = RdeInputDirPaths(
        inputdata=Path("data", "inputdata"),
        invoice=Path("data", "invoice"),
        tasksupport=Path("data", "tasksupport"),
    )
    resource_paths = RdeOutputResourcePath(
        rawfiles=(
            [
                Path("data", "temp", "test_child1.txt"),
            ]
        ),
        raw=Path("data", "raw"),
        main_image=Path("data", "main_image"),
        other_image=Path("data", "other_image"),
        meta=Path("data", "meta"),
        struct=Path("data", "structured"),
        logs=Path("data", "logs"),
        thumbnail=Path(),
        invoice=Path("data", "invoice"),
        invoice_org=Path("data", "temp", "invoice_org.json"),
        invoice_schema_json=Path(ivnoice_schema_json_none_specificAttributes),
    )
    config = Config(extendeds_mode=None, save_raw=True, magic_variable=True, save_thumbnail_image=True)

    # 関数のモック
    mock_datasets_process_function = mocker.Mock()

    # テスト対象の関数を実行
    excel_invoice_mode_process(
        srcpaths,
        resource_paths,
        inputfile_single_dummy_header_excelinvoice,
        0,
        mock_datasets_process_function,
        config=config
    )

    # 関数が呼び出されたかどうかをチェック
    mock_datasets_process_function.assert_called_once_with(srcpaths, resource_paths)
    # invoiceのバックアップが実行されたかチェック
    # descriptionがバックアップ後に実行されるため内容が一致しない。
    with open(os.path.join("data", "temp", "invoice_org.json"), encoding="utf-8") as f:
        contents_backup = json.load(f)
    with open(os.path.join("data", "invoice", "invoice.json"), encoding="utf-8") as f:
        contents_origin = json.load(f)
    assert contents_backup != contents_origin
    # descriptionのチェック
    with open(os.path.join("data", "invoice", "invoice.json"), encoding="utf-8") as f:
        content = json.load(f)
    assert content["basic"]["description"] == expected_description


def test_excel_invoice_mode_process_calls_functions_replace_magic_variable(
    mocker,
    inputfile_single_dummy_header_excelinvoice_with_magic_variable,
    inputfile_zip_with_file,
    ivnoice_json_none_sample_info,
    tasksupport,
    metadata_def_json_with_feature,
    metadata_json,
    ivnoice_schema_json_none_sample,
):
    """excelinvoiceモード時、invoice上書き、データセット処理、${filename}の書き換え
    ファイルモードのとき、${filename}の書き換えが実行されるか
    """
    # 事前準備: フィクスチャ
    Path("data", "raw").mkdir(parents=True, exist_ok=True)
    Path("data", "main_image").mkdir(parents=True, exist_ok=True)
    Path("data", "other_image").mkdir(parents=True, exist_ok=True)
    Path("data", "meta").mkdir(parents=True, exist_ok=True)
    Path("data", "structured").mkdir(parents=True, exist_ok=True)
    Path("data", "logs").mkdir(parents=True, exist_ok=True)
    Path("data", "temp").mkdir(parents=True, exist_ok=True)
    shutil.copy(
        Path("data", "invoice").joinpath("invoice.json"),
        Path("data", "temp", "invoice_org.json"),
    )
    shutil.unpack_archive(Path("data", "inputdata", "test_input_multi.zip"), Path("data", "temp"))

    srcpaths = RdeInputDirPaths(
        inputdata=Path("data", "inputdata"),
        invoice=Path("data", "invoice"),
        tasksupport=Path("data", "tasksupport"),
    )
    resource_paths = RdeOutputResourcePath(
        rawfiles=(
            [
                Path("data", "temp", "test_child1.txt"),
            ]
        ),
        raw=Path("data", "raw"),
        main_image=Path("data", "main_image"),
        other_image=Path("data", "other_image"),
        meta=Path("data", "meta"),
        struct=Path("data", "structured"),
        logs=Path("data", "logs"),
        thumbnail=Path(),
        invoice=Path("data", "invoice"),
        invoice_org=Path("data", "temp", "invoice_org.json"),
        invoice_schema_json=Path(ivnoice_schema_json_none_sample),
    )
    # 関数のモック
    mock_datasets_process_function = mocker.Mock()

    # テスト対象の関数を実行
    config = Config(extendeds_mode=None, save_raw=True, magic_variable=True, save_thumbnail_image=True)
    excel_invoice_mode_process(
        srcpaths,
        resource_paths,
        inputfile_single_dummy_header_excelinvoice_with_magic_variable,
        0,
        mock_datasets_process_function,
        config=config
    )

    # 関数が呼び出されたかどうかをチェック
    mock_datasets_process_function.assert_called_once_with(srcpaths, resource_paths)
    # invoiceのバックアップが実行されたかチェック
    # descriptionがバックアップ後に実行されるため内容が一致しない。
    with open(os.path.join("data", "temp", "invoice_org.json"), encoding="utf-8") as f:
        contents_backup = json.load(f)
    with open(os.path.join("data", "invoice", "invoice.json"), encoding="utf-8") as f:
        contents_origin = json.load(f)
    assert contents_backup != contents_origin
    # descriptionのチェック
    with open(os.path.join("data", "invoice", "invoice.json"), encoding="utf-8") as f:
        content = json.load(f)
    assert content["basic"]["dataName"] == "test_child1.txt"


def test_multifile_mode_process_calls_functions(
    mocker,
    inputfile_multi,
    ivnoice_json_magic_filename_variable,
    tasksupport,
    metadata_def_json_with_feature,
    metadata_json,
    ivnoice_schema_json,
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
    shutil.copy(
        Path("data", "invoice").joinpath("invoice.json"),
        Path("data", "temp", "invoice_org.json"),
    )
    expected_description = "desc1\n特徴量1:test-value1\n特徴量2(V):test-value2\n特徴量3(V):test-value3"
    mock_datasets_process_function = mocker.Mock()

    srcpaths = RdeInputDirPaths(
        inputdata=Path("data", "inputdata"),
        invoice=Path("data", "invoice"),
        tasksupport=Path("data", "tasksupport"),
    )
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
        invoice_schema_json=Path(ivnoice_schema_json),
    )

    # テスト対象の処理を実行
    config = Config(extendeds_mode="multifile", save_raw=True, magic_variable=True, save_thumbnail_image=True)
    multifile_mode_process(srcpaths, resource_paths, mock_datasets_process_function, config=config)

    # 関数が呼び出されたかどうかをチェック
    mock_datasets_process_function.assert_called_once_with(srcpaths, resource_paths)

    # invoiceのバックアップが実行されたかチェック
    # descriptionがバックアップ後に実行されるため内容が一致しない。
    with open(os.path.join("data", "temp", "invoice_org.json"), encoding="utf-8") as f:
        contents_backup = json.load(f)
    with open(os.path.join("data", "invoice", "invoice.json"), encoding="utf-8") as f:
        contents_origin = json.load(f)
    assert contents_backup != contents_origin

    # rawfileのバックアップが実行されたかチェック
    for file in resource_paths.rawfiles:
        assert os.path.exists(file)

    # descriptionのチェック
    with open(os.path.join("data", "invoice", "invoice.json"), encoding="utf-8") as f:
        content = json.load(f)
    assert content["basic"]["description"] == expected_description


def test_multifile_mode_process_calls_functions_replace_magic_filename(
    mocker,
    inputfile_multi,
    ivnoice_json_magic_filename_variable,
    tasksupport,
    metadata_def_json_with_feature,
    metadata_json,
    ivnoice_schema_json,
):
    """multifile_mode_processモード時、invoice上書き、データセット処理、特徴量書き込み
    既存のdescription: desc1を含む
    """
    inputfile_multi.sort()
    input1_path_lists = [
        Path("data", "raw"),
        Path("data", "main_image"),
        Path("data", "other_image"),
        Path("data", "meta"),
        Path("data", "structured"),
        Path("data", "logs"),
        Path("data", "temp"),
    ]
    for path in input1_path_lists:
        path.mkdir(parents=True, exist_ok=True)

    # common process
    shutil.copy(
        Path("data", "invoice").joinpath("invoice.json"),
        Path("data", "temp", "invoice_org.json"),
    )

    srcpaths = RdeInputDirPaths(
        inputdata=Path("data", "inputdata"),
        invoice=Path("data", "invoice"),
        tasksupport=Path("data", "tasksupport"),
    )
    resource_paths1 = RdeOutputResourcePath(
        rawfiles=(inputfile_multi[0],),
        raw=Path("data", "raw"),
        main_image=Path("data", "main_image"),
        other_image=Path("data", "other_image"),
        meta=Path("data", "meta"),
        struct=Path("data", "structured"),
        logs=Path("data", "logs"),
        thumbnail=Path(),
        invoice=Path("data", "invoice"),
        invoice_org=Path("data", "temp", "invoice_org.json"),
        invoice_schema_json=Path(ivnoice_schema_json),
    )

    input2_path_lists = [
        Path("data", "divided", f"{1:04d}", "invoice"),
        Path("data", "divided", f"{1:04d}", "raw"),
        Path("data", "divided", f"{1:04d}", "main_image"),
        Path("data", "divided", f"{1:04d}", "other_image"),
        Path("data", "divided", f"{1:04d}", "meta"),
        Path("data", "divided", f"{1:04d}", "structured"),
        Path("data", "divided", f"{1:04d}", "logs"),
    ]
    for path in input2_path_lists:
        path.mkdir(parents=True, exist_ok=True)

    resource_paths2 = RdeOutputResourcePath(
        rawfiles=(inputfile_multi[1],),
        raw=Path("data", "divided", f"{1:04d}", "raw"),
        main_image=Path("data", "divided", f"{1:04d}", "main_image"),
        other_image=Path("data", "divided", f"{1:04d}", "other_image"),
        meta=Path("data", "divided", f"{1:04d}", "meta"),
        struct=Path("data", "divided", f"{1:04d}", "structured"),
        logs=Path("data", "divided", f"{1:04d}", "logs"),
        thumbnail=Path(),
        invoice=Path("data", "divided", f"{1:04d}", "invoice"),
        invoice_org=Path("data", "temp", "invoice_org.json"),
        invoice_schema_json=Path(ivnoice_schema_json),
    )

    expected_filename1 = "test_child1.txt"
    expected_filename2 = "test_child2.txt"

    mock_datasets_process_function = mocker.Mock()

    # テスト対象の処理を実行
    for idx in range(2):
        if idx == 0:
            resource_paths = resource_paths1
            expected_filename = expected_filename1
            invoice = Path("data", "invoice", "invoice.json")
        else:
            resource_paths = resource_paths2
            expected_filename = expected_filename2
            invoice = Path("data", "divided", f"{1:04d}", "invoice", "invoice.json")

        config = Config(extendeds_mode="multifile", save_raw=True, magic_variable=True, save_thumbnail_image=True)
        multifile_mode_process(srcpaths, resource_paths, mock_datasets_process_function, config=config)

        # 関数が呼び出されたかどうかをチェック
        mock_datasets_process_function.assert_called_with(srcpaths, resource_paths)

        # invoiceのバックアップが実行されたかチェック
        # descriptionがバックアップ後に実行されるため内容が一致しない。
        with open(os.path.join("data", "temp", "invoice_org.json"), encoding="utf-8") as f:
            contents_backup = json.load(f)
        with open(os.path.join("data", "invoice", "invoice.json"), encoding="utf-8") as f:
            contents_origin = json.load(f)
        assert contents_backup != contents_origin

        # rawfileのバックアップが実行されたかチェック
        for file in resource_paths.rawfiles:
            assert os.path.exists(file)

        with open(invoice, encoding="utf-8") as f:
            content = json.load(f)
        # ${filename}の書き換えの実行
        assert content["basic"]["dataName"] == expected_filename


def test_rdeformat_mode_process_alls_functions(
    mocker,
    inputfile_rdeformat,
    invoice_json_with_desc,
    tasksupport,
    metadata_def_json_with_feature,
    metadata_json,
    invoice_shcema_json_full,
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
    Path("data", "thumbnail").mkdir(parents=True, exist_ok=True)
    zip_path = Path("data", "inputdata") / Path(inputfile_rdeformat).name
    shutil.unpack_archive(zip_path, Path("data", "temp"))

    shutil.copy(
        Path("data", "invoice").joinpath("invoice.json"),
        Path("data", "temp", "invoice_org.json"),
    )
    Path("data/main_image/dummy_file.png").touch()
    expected_description = "特徴量1:test-value1\n特徴量2(V):test-value2\n特徴量3(V):test-value3"
    mock_datasets_process_function = mocker.Mock()

    raw_files = tuple(f for f in Path("data", "temp").rglob("*") if f.is_file())
    srcpaths = RdeInputDirPaths(
        inputdata=Path("data", "inputdata"),
        invoice=Path("data", "invoice"),
        tasksupport=Path("data", "tasksupport"),
    )
    resource_paths = RdeOutputResourcePath(
        rawfiles=raw_files,
        raw=Path("data", "raw"),
        main_image=Path("data", "main_image"),
        other_image=Path("data", "other_image"),
        meta=Path("data", "meta"),
        struct=Path("data", "structured"),
        logs=Path("data", "logs"),
        thumbnail=Path("data", "thumbnail"),
        invoice=Path("data", "invoice"),
        invoice_org=Path("data", "temp", "invoice_org.json"),
        invoice_schema_json=invoice_shcema_json_full,
    )
    config = Config(extendeds_mode="rdeformat", save_raw=True, magic_variable=False, save_thumbnail_image=True)
    # テスト対象の処理を実行
    rdeformat_mode_process(srcpaths, resource_paths, mock_datasets_process_function, config=config)

    # 関数が呼び出されたかどうかをチェック
    mock_datasets_process_function.assert_called_once_with(srcpaths, resource_paths)

    # descriptionのチェック
    with open(os.path.join("data", "invoice", "invoice.json"), encoding="utf-8") as f:
        content = json.load(f)
    assert content["basic"]["description"] == expected_description

    # rawフォルダにコピーされたかチェック
    assert len(list(Path("data", "raw").glob("*"))) == 1

    # thumbnailフォルダにコピーされたかチェック
    assert len(list(Path("data", "thumbnail").glob("*"))) == 1
