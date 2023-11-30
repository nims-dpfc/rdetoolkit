import json
from pathlib import Path
import pytest

from rdetoolkit.invoiceFile import apply_default_filename_mapping_rule


@pytest.fixture
def invoice_file_with_magic_variable():
    contents = {"basic": {"dataName": "${filename}", "dateSubmitted": "2023-11-30", "dataOwnerId": "3"}}

    test_invoice_path = Path("tests/invoice.json")
    with open(test_invoice_path, mode="w", encoding="utf-8") as f:
        json.dump(contents, f)

    yield test_invoice_path

    if test_invoice_path.exists():
        test_invoice_path.unlink()


def test_apply_default_filename_mapping_rule(invoice_file_with_magic_variable):
    test_overwrite_contents = {"${filename}": "test_input_filename.txt"}

    apply_default_filename_mapping_rule(
        test_overwrite_contents, invoice_file_with_magic_variable
    )

    with open(invoice_file_with_magic_variable, mode="r", encoding="utf-8") as f:
        contents = json.load(f)

    result_key_word = contents.get("basic", {}).get("dataName")
    assert result_key_word == "test_input_filename.txt"
    other_key_word = contents.get("basic", {}).get("dataOwnerId")
    assert other_key_word == "3"
