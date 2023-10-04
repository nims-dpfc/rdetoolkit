from pathlib import Path

from rdetoolkit.invoiceFile import backup_invoice_json_files
from rdetoolkit.models.rde2types import RdeFormatFlags


def test_backup_invoice_json_files_with_excel_invoice_file(
    inputfile_single_header_merge_excelinvoice,
    ivnoice_json_with_sample_info,
    tasksupport):
    """Excelinvoiceモードでのinvoice.jsonのバックアップ処理テスト

    引数(フィクスチャ):
    - inputfile_single_header_merge_excelinvoice: data/inputdata/test_excel_invoice.xlsxの作成と削除
    - ivnoice_json_with_sample_info: data/invoice/invoice.jsonの作成と削除
    - tasksupport: data/tasksupportの作成と削除
    上記のファイルはテストで実態として必要なためファイル内容はダミーデータ
    """
    Path("data","temp").mkdir(parents=True, exist_ok=True)
    fmt_flags = RdeFormatFlags()
    result = backup_invoice_json_files(inputfile_single_header_merge_excelinvoice, fmt_flags)

    assert result == Path("data","temp").joinpath('invoice_org.json')


def test_backup_invoice_json_files_with_rdeformat_enabled(
    inputfile_rdeformat,
    ivnoice_json_with_sample_info,
    ivnoice_schema_json):
    """RDEformatモードでのinvoice.jsonのバックアップ処理テスト

    引数(フィクスチャ):
    - inputfile_rdeformat: data/inputdata/rdeformat_pack.zipとtasksupport/rdeformat.txtの作成と削除
    - ivnoice_json_with_sample_info: data/invoice/invoice.jsonの作成と削除
    - ivnoice_schema_json: data/tasksupport/ivnoice_schema_json
    上記のファイルはテストで実態として必要なためファイル内容はダミーデータ
    """
    Path("data","temp").mkdir(parents=True, exist_ok=True)
    input_excel_invoice_path = None

    fmt_flags = RdeFormatFlags()
    result = backup_invoice_json_files(input_excel_invoice_path, fmt_flags)

    assert result == Path("data","temp").joinpath('invoice_org.json')


def test_backup_invoice_json_files_with_multifile_enabled(
    inputfile_multimode,
    ivnoice_json_with_sample_info,
    ivnoice_schema_json):
    """RDEformatモードでのinvoice.jsonのバックアップ処理テスト

    引数(フィクスチャ):
    - inputfile_multimode: tasksupport/rdeformat.txtの作成と削除
    - ivnoice_json_with_sample_info: data/invoice/invoice.jsonの作成と削除
    - ivnoice_schema_json: data/tasksupport/ivnoice_schema_json
    上記のファイルはテストで実態として必要なためファイル内容はダミーデータ
    """
    Path("data","temp").mkdir(parents=True, exist_ok=True)
    input_excel_invoice_path = None

    fmt_flags = RdeFormatFlags()
    result = backup_invoice_json_files(input_excel_invoice_path, fmt_flags)

    assert result == Path("data","temp").joinpath('invoice_org.json')


def test_backup_invoice_json_files_with_no_modes(
    inputfile_single,
    ivnoice_json_with_sample_info,
    ivnoice_schema_json):
    """RDEformatモードでのinvoice.jsonのバックアップ処理テスト

    引数(フィクスチャ):
    - inputfile_single: data/inputdata/test_single.txtの作成と削除
    - ivnoice_json_with_sample_info: data/invoice/invoice.jsonの作成と削除
    - ivnoice_schema_json: data/tasksupport/ivnoice_schema_json
    上記のファイルはテストで実態として必要なためファイル内容はダミーデータ
    """
    Path("data","temp").mkdir(parents=True, exist_ok=True)
    input_excel_invoice_path = None

    fmt_flags = RdeFormatFlags()
    result = backup_invoice_json_files(input_excel_invoice_path, fmt_flags)

    assert result == Path("data","invoice").joinpath('invoice.json')
