import json
import os
import tempfile

import pytest
from rdetoolkit.rde2util import (
    Meta,
    _split_value_unit,
    CharDecEncoding,
    read_from_json_file,
    write_to_json_file,
)


def test_split_value_unit():
    # テストケース1: 値と単位が両方存在する場合
    result = _split_value_unit("10.5 kg")
    assert result.value == "10.5"
    assert result.unit == "kg"

    # テストケース2: 値のみ存在する場合
    result = _split_value_unit("25")
    assert result.value == "25"
    assert result.unit == ""

    # テストケース3: 単位のみ存在する場合
    result = _split_value_unit("m/s")
    assert result.value == ""
    assert result.unit == "m/s"

    # テストケース4: 値と単位が空の場合
    result = _split_value_unit("")
    assert result.value == ""
    assert result.unit == ""

    # テストケース5: 値と単位が空白文字のみの場合
    result = _split_value_unit("   ")
    assert result.value == ""
    assert result.unit == ""


@pytest.fixture
def meta_const_instance():
    meta_dict = {
        "common.data_origin": {
            "name": {"ja": "データの起源", "en": "Data Origin"},
            "schema": {"type": "string"},
        },
        "common.technical_category": {
            "name": {"ja": "技術カテゴリー", "en": "Technical Category"},
            "schema": {"type": "string"},
        },
        "date": {
            "name": {"ja": "日時", "en": "date"},
            "schema": {"type": "string"},
        },
        "reference": {
            "name": {"ja": "参考文献", "en": "Reference"},
            "schema": {"type": "string"},
        },
    }

    with open("tests/metadata-def.json", mode="w", encoding="utf-8") as f:
        json.dump(meta_dict, f, ensure_ascii=False)
    metadef_filepath = "tests/metadata-def.json"  # Replace with the actual file path
    yield Meta(metadef_filepath=metadef_filepath)
    if os.path.exists("tests/metadata-def.json"):
        os.remove("tests/metadata-def.json")
    if os.path.exists("tests/metadata.json"):
        os.remove("tests/metadata.json")


def test_read_metadef_file(meta_const_instance):
    metadef_filepath = "tests/metadata-def.json"  # Replace with the actual file path
    result = meta_const_instance._read_metadef_file(metadef_filepath)
    assert isinstance(result, dict)


def test_assignVals_unknown_key(meta_const_instance):
    entry_dict_meta = {"key1": "value1", "key2": "value2"}
    result = meta_const_instance.assignVals(entry_dict_meta)
    print(result)
    assert result["unknown"] == {"key1", "key2"}
    assert result["assigned"] == set()


def test_assignVals_exsit_key(meta_const_instance):
    entry_dict_meta = {"date": "2022-01-01", "reference": "sample.com"}
    result = meta_const_instance.assignVals(entry_dict_meta)
    assert result["unknown"] == set()
    assert result["assigned"] == {"reference", "date"}


def test_empty_writeFile(meta_const_instance):
    """metadata.json is empty"""
    metafilepath = "tests/metadata.json"  # Replace with the actual file path
    result = meta_const_instance.writeFile(metafilepath)
    assert os.path.exists("tests/metadata.json")
    assert result["assigned"] == set()


def test_has_contents_writeFile(meta_const_instance):
    """Write the metadata to metadata.json"""
    metafilepath = "tests/metadata.json"
    entry_dict_meta = {"date": "2022-01-01", "reference": "sample.com"}
    meta_const_instance.assignVals(entry_dict_meta)
    meta_const_instance.writeFile(metafilepath)
    assert os.path.exists("tests/metadata.json")

    with open(metafilepath, encoding="utf-8") as f:
        content = json.load(f)
        assert content["constant"]["date"]["value"] == "2022-01-01"
        assert content["constant"]["reference"]["value"] == "sample.com"


@pytest.fixture
def meta_variable_instance():
    meta_dict = {
        "common.data_origin": {
            "name": {"ja": "データの起源", "en": "Data Origin"},
            "schema": {"type": "string"},
        },
        "common.technical_category": {
            "name": {"ja": "技術カテゴリー", "en": "Technical Category"},
            "schema": {"type": "string"},
        },
        "date": {
            "name": {"ja": "日時", "en": "date"},
            "schema": {"type": "string"},
            "variable": 1,
        },
        "reference": {
            "name": {"ja": "参考文献", "en": "Reference"},
            "schema": {"type": "string"},
            "variable": 1,
        },
        "custom.user": {
            "name": {"ja": "ユーザー", "en": "User"},
            "schema": {"type": "string"},
            "variable": 1,
        },
    }

    with open("tests/metadata-def.json", mode="w", encoding="utf-8") as f:
        json.dump(meta_dict, f, ensure_ascii=False)
    metadef_filepath = "tests/metadata-def.json"  # Replace with the actual file path
    yield Meta(metadef_filepath=metadef_filepath)
    if os.path.exists("tests/metadata-def.json"):
        os.remove("tests/metadata-def.json")
    if os.path.exists("tests/metadata.json"):
        os.remove("tests/metadata.json")


def test_assignVals_variable_exsit_key(meta_variable_instance):
    entry_dict_meta = {
        "date": ["2022-01-01", "2022-01-02", "2022-01-03"],
        "reference": ["sample.com", "experiments.app", "myDocuments.go.jp"],
        "custom.user": ["A", "B", "C"],
    }
    result = meta_variable_instance.assignVals(entry_dict_meta)
    assert result["unknown"] == set()
    assert result["assigned"] == {"reference", "date", "custom.user"}


def test_has_variable_writeFile(meta_variable_instance):
    """Write the metadata to metadata.json"""
    metafilepath = "tests/metadata.json"
    entry_dict_meta = {
        "date": ["2022-01-01", "2022-01-02", "2022-01-03"],
        "reference": ["sample.com", "experiments.app", "myDocuments.go.jp"],
        "custom.user": ["A", "B", "C"],
    }
    meta_variable_instance.assignVals(entry_dict_meta)
    meta_variable_instance.writeFile(metafilepath)
    assert os.path.exists("tests/metadata.json")

    with open(metafilepath, encoding="utf-8") as f:
        content = json.load(f)
        assert content["variable"][0]["date"]["value"] == "2022-01-01"
        assert content["variable"][0]["reference"]["value"] == "sample.com"
        assert content["variable"][0]["custom.user"]["value"] == "A"
        assert content["variable"][1]["date"]["value"] == "2022-01-02"
        assert content["variable"][1]["reference"]["value"] == "experiments.app"
        assert content["variable"][1]["custom.user"]["value"] == "B"
        assert content["variable"][2]["date"]["value"] == "2022-01-03"
        assert content["variable"][2]["reference"]["value"] == "myDocuments.go.jp"
        assert content["variable"][2]["custom.user"]["value"] == "C"


# detect_text_file_encodingに関するテスト
@pytest.fixture
def utf_8_file():
    # テスト用の"utf_8"エンコーディングのファイルを作成する
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf_8", delete=False) as f:
        f.write("テストファイル（UTF-8）")
        file_path = f.name
    yield file_path
    os.remove(file_path)


@pytest.fixture
def shift_jis_file():
    # テスト用の"shift_jis"エンコーディングのファイルを作成する
    with tempfile.NamedTemporaryFile(mode="w", encoding="shift_jis", delete=False) as f:
        f.write("テストファイル（Shift-JIS）")
        file_path = f.name
    yield file_path
    os.remove(file_path)


@pytest.fixture
def utf_8_sig_file():
    # テスト用の"utf_8_sig"エンコーディングのファイルを作成する
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf_8_sig", delete=False) as f:
        f.write("テストファイル（UTF-8 with BOM）")
        file_path = f.name
    yield file_path
    os.remove(file_path)


def test_detect_text_file_encoding(utf_8_file):
    assert CharDecEncoding.detect_text_file_encoding(utf_8_file) == "utf_8"


def test_detect_text_file_encoding_shift_jis(shift_jis_file):
    assert CharDecEncoding.detect_text_file_encoding(shift_jis_file) == "cp932"


def test_detect_text_file_encoding_utf_8_sig(utf_8_sig_file):
    assert CharDecEncoding.detect_text_file_encoding(utf_8_sig_file) == "utf_8_sig"


# read_invoice_json_fileのテスト
def test_read_from_json_file_valid_json_file(ivnoice_json_none_sample_info):
    expect_json = {
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
    # JSONファイルを読み込む関数を呼び出し
    result = read_from_json_file(ivnoice_json_none_sample_info)

    assert result == expect_json


@pytest.fixture
def sample_invoice():
    return {
        "invoice_id": "12345",
        "items": [
            {"product": "apple", "quantity": 3, "price": 0.5},
            {"product": "orange", "quantity": 1, "price": 0.8},
        ],
    }


def test_write_to_json_file(tmp_path, sample_invoice):
    # tmp_path is a pytest fixture that provides a temporary directory unique to the test invocation
    file_path = tmp_path / "invoice.json"
    write_to_json_file(file_path, sample_invoice)

    # Check if the file exists
    assert file_path.exists()

    # Read the file and check its content
    with open(file_path, encoding="utf_8") as f:
        data = json.load(f)

    assert data == sample_invoice
