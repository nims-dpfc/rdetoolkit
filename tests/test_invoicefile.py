import json
import os
from pathlib import Path

import pytest
from src.rdetoolkit.exceptions import StructuredError
from src.rdetoolkit.invoiceFile import (ExcelInvoiceFile, InvoiceFile,
                                        update_description_with_features)
from src.rdetoolkit.models.rde2types import RdeOutputResourcePath


def test_invoicefile_read_method(ivnoice_json_none_sample_info):
    """テストケース: InvoiceFileのread"""
    invoice_file = InvoiceFile(ivnoice_json_none_sample_info)
    expect_data = {
        'datasetId': 'e751fcc4-b926-4747-b236-cab40316fc49',
        'basic': {
            'dateSubmitted': '2023-03-14',
            'dataOwnerId': 'f30812c3-14bc-4274-809f-afcfaa2e4047',
            'dataName': 'test1',
            'experimentId': 'test_230606_1',
            'description': 'desc1'
            },
        'custom': {
            'key1': 'test1',
            'key2': 'test2'
        }
    }
    assert invoice_file.invoice_json == expect_data

def test_overwrite_method(ivnoice_json_none_sample_info):
    """テストケース: InvoiceFileのoverwrite"""
    dist_file_path = Path("tests/test_dist_invoice.json")
    invoice_file = InvoiceFile(ivnoice_json_none_sample_info)
    invoice_file.overwrite(dist_file_path)

    with open(ivnoice_json_none_sample_info, 'rb') as src_file, open(dist_file_path, 'rb') as dist_file:
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
        invoice_org=Path("data/invoice/invoice.json")
    )
    yield rde_resource

def test_update_description_with_features(
    rde_resource,
    ivnoice_schema_json,
    metadata_def_json_with_feature,
    ivnoice_json_none_sample_info,
    metadata_json
):
    """テストケース: descriptionへの書き出しがパスするかテスト"""
    expect_message = "desc1\n特徴量1:test-value1\n特徴量2(V):test-value2\n特徴量3(V):test-value3\n"

    # 検証
    update_description_with_features(rde_resource, ivnoice_json_none_sample_info, metadata_def_json_with_feature)

    # 書き込み結果を比較
    with open(ivnoice_json_none_sample_info, mode="r", encoding="utf-8") as f:
        result_contents = json.load(f)

    assert result_contents["basic"]["description"] == expect_message


