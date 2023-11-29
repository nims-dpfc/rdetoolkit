import json
import os
from pathlib import Path

import pytest
from rdetoolkit.exceptions import StructuredError
from rdetoolkit.invoiceFile import (
    ExcelInvoiceFile,
    InvoiceFile,
    update_description_with_features,
    readExcelInvoice,
)
from rdetoolkit.models.rde2types import RdeOutputResourcePath
import pandas as pd
from pandas.testing import assert_frame_equal


def test_invoicefile_read_method(ivnoice_json_none_sample_info):
    """テストケース: InvoiceFileのread"""
    invoice_file = InvoiceFile(ivnoice_json_none_sample_info)
    expect_data = {
        "datasetId": "e751fcc4-b926-4747-b236-cab40316fc49",
        "basic": {
            "dateSubmitted": "2023-03-14",
            "dataOwnerId": "f30812c3-14bc-4274-809f-afcfaa2e4047",
            "dataName": "test1",
            "experimentId": "test_230606_1",
            "description": "desc1",
        },
        "custom": {"key1": "test1", "key2": "test2"},
    }
    assert invoice_file.invoice_json == expect_data


def test_overwrite_method(ivnoice_json_none_sample_info):
    """テストケース: InvoiceFileのoverwrite"""
    dist_file_path = Path("tests/test_dist_invoice.json")
    invoice_file = InvoiceFile(ivnoice_json_none_sample_info)
    invoice_file.overwrite(dist_file_path)

    with open(ivnoice_json_none_sample_info, "rb") as src_file, open(
        dist_file_path, "rb"
    ) as dist_file:
        assert src_file.read() == dist_file.read()
    if os.path.exists(dist_file_path):
        os.remove(dist_file_path)


def test_read_valid_excel_invoice_file(inputfile_single_dummy_header_excelinvoice):
    """Excelinvoiceのheaderに適当な値が入力されても同じヘッダー情報へ変更して返すかテスト"""
    invoice_path = Path(inputfile_single_dummy_header_excelinvoice)
    excel_invoice_file = ExcelInvoiceFile(invoice_path)

    dfExcelInvoice, dfGeneral, dfSpecific = excel_invoice_file.read()

    assert dfExcelInvoice.columns[0] == "data_file_names/name"
    assert (dfGeneral.columns == ["term_id", "key_name"]).all()
    assert (dfSpecific.columns == ["sample_class_id", "term_id", "key_name"]).all()


def test_read_none_sample_excel_invoice_file(excelinvoice_non_sampleinfo):
    """Excelinvoiceのsample情報なしの時のreadテスト"""
    invoice_path = Path(excelinvoice_non_sampleinfo)
    excel_invoice_file = ExcelInvoiceFile(invoice_path)

    dfExcelInvoice, dfGeneral, dfSpecific = excel_invoice_file.read()

    assert dfExcelInvoice.columns[0] == "data_file_names/name"
    assert (dfGeneral.columns == ["term_id", "key_name"]).all()
    assert (dfSpecific.columns == ["sample_class_id", "term_id", "key_name"]).all()


def test_read_none_sample_excel_invoice_file(
    inputfile_single_excelinvoice_with_blankline,
):
    """Excelinvoiceの行間に空行がある場合のテスト
    想定としては、エクセルインボイスの5行目移行に空行がある場合エラーメッセージを出す
    """
    invoice_path = Path(inputfile_single_excelinvoice_with_blankline)

    with pytest.raises(StructuredError) as e:
        excel_invoice_file = ExcelInvoiceFile(invoice_path)
        dfExcelInvoice, dfGeneral, dfSpecific = excel_invoice_file.read()

    assert str(e.value) == "Error! Blank lines exist between lines"


def test_excelinvoice_overwrite(
    inputfile_multi_excelinvoice, ivnoice_json_with_sample_info, ivnoice_schema_json
):
    """試料情報ありの上書き処理
    上書き後のinvoice.jsonの内容を確認する
    上書き前のkey/value -> custom.key1: test1
    上書き前のkey/value -> custom.key2: test2
    """
    dist_path = Path("data", "invoice", "invoice.json")
    excel_invoice_path = Path(inputfile_multi_excelinvoice)

    excel_invoice_file = ExcelInvoiceFile(excel_invoice_path)
    excel_invoice_file.overwrite(
        ivnoice_json_with_sample_info, dist_path, ivnoice_schema_json, 0
    )

    with open(dist_path, mode="r", encoding="utf-8") as f:
        contents = json.load(f)

    assert contents["custom"]["key1"] == "AAA"
    assert contents["custom"]["key2"] == "CCC"


def test_excelinvoice_overwrite_none_sample(
    excelinvoice_non_sampleinfo, ivnoice_json_none_sample_info, ivnoice_schema_json
):
    """試料情報なしの上書き処理
    上書き後のinvoice.jsonの内容を確認する
    上書き前のkey/value -> custom.key1: test1
    上書き前のkey/value -> custom.key2: test2
    """
    dist_path = Path("data", "invoice", "invoice.json")
    excel_invoice_path = Path(excelinvoice_non_sampleinfo)

    excel_invoice_file = ExcelInvoiceFile(excel_invoice_path)
    excel_invoice_file.overwrite(
        ivnoice_json_none_sample_info, dist_path, ivnoice_schema_json, 0
    )

    with open(dist_path, mode="r", encoding="utf-8") as f:
        contents = json.load(f)

    assert contents["custom"]["key1"] == "AAA"
    assert contents["custom"]["key2"] == "CCC"


def test_read_invalid_excel_invoice_file():
    invoice_path = Path("dummy/file.xlsx")
    with pytest.raises(StructuredError) as e:
        ExcelInvoiceFile(invoice_path)
    assert str(e.value) == "ERROR: excelinvoice not found dummy/file.xlsx"


def test_read_no_first_sheet_excel_invoice_file(inputfile_empty_excelinvoice):
    invoice_path = Path(inputfile_empty_excelinvoice)
    with pytest.raises(StructuredError) as e:
        ExcelInvoiceFile(invoice_path)
    assert str(e.value) == "ERROR: no sheet in invoiceList files"


@pytest.fixture
def rde_resource():
    rde_resource = RdeOutputResourcePath(
        raw=Path("dummy"),
        rawfiles=tuple(["dummy1", "dummy2"]),
        struct=Path("dummmy"),
        main_image=Path("dummmy"),
        other_image=Path("dummmy"),
        thumbnail=Path("dummmy"),
        meta=Path("data/meta"),
        logs=Path("dummmy"),
        invoice=Path("data/invoice"),
        invoice_schema_json=Path("data/tasksupport/invoice.schema.json"),
        invoice_org=Path("data/invoice/invoice.json"),
    )
    yield rde_resource


def test_update_description_with_features(
    rde_resource,
    ivnoice_schema_json,
    metadata_def_json_with_feature,
    ivnoice_json_none_sample_info,
    metadata_json,
):
    """テストケース: descriptionへの書き出しがパスするかテスト"""
    expect_message = "desc1\n特徴量1:test-value1\n特徴量2(V):test-value2\n特徴量3(V):test-value3"

    # 検証
    update_description_with_features(
        rde_resource, ivnoice_json_none_sample_info, metadata_def_json_with_feature
    )

    # 書き込み結果を比較
    with open(ivnoice_json_none_sample_info, mode="r", encoding="utf-8") as f:
        result_contents = json.load(f)

    assert result_contents["basic"]["description"] == expect_message


def test_update_description_with_features_missing_target_key(
    rde_resource,
    ivnoice_schema_json,
    metadata_def_json_with_feature,
    ivnoice_json_none_sample_info,
    metadata_json_missing_value,
):
    """テストケース:
    descriptionへの書き出すはずのメタデータのvalueが存在しないとき、descriptionが記述できるかどうかテスト
    想定としては、書き出す対象のメタデータのvalueがなくても記述できることを想定している。
    """
    expect_message = "desc1\n特徴量1:test-value1\n特徴量3(V):test-value3"

    # 検証
    update_description_with_features(
        rde_resource, ivnoice_json_none_sample_info, metadata_def_json_with_feature
    )

    # 書き込み結果を比較
    with open(ivnoice_json_none_sample_info, mode="r", encoding="utf-8") as f:
        result_contents = json.load(f)

    assert result_contents["basic"]["description"] == expect_message


def test_update_description_with_features_missing_target_key(
    rde_resource,
    ivnoice_schema_json,
    metadata_def_json_with_feature,
    ivnoice_json_none_sample_info,
    metadata_json_missing_value,
):
    """テストケース:
    metadata.jsonにconstant, variableがない場合でも、descriptionの処理を正しく実行できるか確認。
    constant, variableがない場合、descriptionにコメントを追加せずに処理をパスする。
    """
    expect_message = "desc1\n特徴量1:test-value1\n特徴量3(V):test-value3"

    # 検証
    update_description_with_features(
        rde_resource, ivnoice_json_none_sample_info, metadata_def_json_with_feature
    )

    # 書き込み結果を比較
    with open(ivnoice_json_none_sample_info, mode="r", encoding="utf-8") as f:
        result_contents = json.load(f)

    assert result_contents["basic"]["description"] == expect_message


def test_update_description_with_features_none_variable(
    rde_resource,
    ivnoice_schema_json,
    metadata_def_json_with_feature,
    ivnoice_json_none_sample_info,
    metadata_json_non_variable,
):
    """テストケース: metadata.jsonのconstantに全て特徴量の情報が記述されており、
    descriptionへの書き出しがパスするかテスト
    """
    expect_message = "desc1\n特徴量1:test-value1\n特徴量2(V):test-value2\n特徴量3(V):test-value3"

    # 検証
    update_description_with_features(
        rde_resource, ivnoice_json_none_sample_info, metadata_def_json_with_feature
    )

    # 書き込み結果を比較
    with open(ivnoice_json_none_sample_info, mode="r", encoding="utf-8") as f:
        result_contents = json.load(f)

    assert result_contents["basic"]["description"] == expect_message


def test_update_description_with_features_none_constant(
    rde_resource,
    ivnoice_schema_json,
    metadata_def_json_with_feature,
    ivnoice_json_none_sample_info,
    metadata_json_non_constat,
):
    """テストケース: metadata.jsonのconstantに全て特徴量の情報が記述されており、
    descriptionへの書き出しがパスするかテスト
    """
    expect_message = "desc1\n特徴量1:test-value1\n特徴量2(V):test-value2\n特徴量3(V):test-value3"

    # 検証
    update_description_with_features(
        rde_resource, ivnoice_json_none_sample_info, metadata_def_json_with_feature
    )

    # 書き込み結果を比較
    with open(ivnoice_json_none_sample_info, mode="r", encoding="utf-8") as f:
        result_contents = json.load(f)

    assert result_contents["basic"]["description"] == expect_message


def test_update_description_none_features_none_variable(
    rde_resource,
    ivnoice_schema_json,
    metadata_def_json_none_feature,
    ivnoice_json_none_sample_info,
    metadata_json_non_variable,
):
    """テストケース:
    metadata.jsonのconstantにメタデータの記載はあるが、featureがないmetadata.josnを正しくPassできるかテスト
    """
    expect_message = "desc1"

    # 検証
    update_description_with_features(
        rde_resource, ivnoice_json_none_sample_info, metadata_def_json_none_feature
    )
    # 書き込み結果を比較
    with open(ivnoice_json_none_sample_info, mode="r", encoding="utf-8") as f:
        result_contents = json.load(f)

    assert result_contents["basic"]["description"] == expect_message


def test_readExcelInvoice(inputfile_single_excelinvoice):
    """readExcelInvoiceのテスト
    dfExcelInvoice, dfGeneral, dfSpecificが正しい値で返ってくるかテスト
    """
    expect_sheet1 = [
        [
            "test_child1.txt",
            "N_TEST_1",
            "test_user",
            "f30812c3-14bc-4274-809f-afcfaa2e4047",
            "test1",
            "test_230606_1",
            "desc1",
            "sample1",
            "cbf194ea-813f-4e05-b288",
            "1111",
            "sample1",
            "test_ref",
            "desc3",
            "testname",
            "Fe",
            "magnet",
            "7439-89-6",
            "AAA",
            "CCC",
        ],
    ]
    df1 = pd.DataFrame(
        expect_sheet1,
        columns=[
            "data_file_names/name",
            "dataset_title",
            "dataOwner",
            "basic/dataOwnerId",
            "basic/dataName",
            "basic/experimentId",
            "basic/referenceUrl",
            "sample/description",
            "sample/names",
            "sample/sampleId",
            "sample/ownerId",
            "sample/composition",
            "sample/description",
            "sample.general/general-name",
            "sample.general/chemical-composition",
            "sample.general/sample-type",
            "sample.general/cas-number",
            "custom/key1",
            "custom/key2",
        ],
    )

    dfExcelInvoice, dfGeneral, dfSpecific = readExcelInvoice(
        inputfile_single_excelinvoice
    )

    assert_frame_equal(dfExcelInvoice, df1)
    assert isinstance(dfGeneral, pd.DataFrame)
    assert dfGeneral.columns.to_list() == ["term_id", "key_name"]
    assert isinstance(dfSpecific, pd.DataFrame)
    assert dfSpecific.columns.to_list() == ["sample_class_id", "term_id", "key_name"]


def test_empty_excelinvoice_readExcelInvoice(empty_inputfile_excelinvoice):
    """空のエクセルインボイスを入れた時に例外をキャッチできるかテスト"""
    with pytest.raises(StructuredError) as e:
        _, _, _ = readExcelInvoice(empty_inputfile_excelinvoice)
    assert str(e.value) == "ERROR: no sheet in invoiceList files"


def test_invalid_excelinvoice_readExcelInvoice(
    inputfile_invalid_samesheet_excelinvoice,
):
    """sheet1の内容が複数あるエクセルインボイスを入れた時に例外をキャッチできるかテスト"""
    with pytest.raises(StructuredError) as e:
        _, _, _ = readExcelInvoice(inputfile_invalid_samesheet_excelinvoice)
    assert str(e.value) == "ERROR: multiple sheet in invoiceList files"
