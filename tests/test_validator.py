import json
import shutil
from pathlib import Path

import pytest
from pydantic import ValidationError
from rdetoolkit.exceptions import (
    InvoiceSchemaValidationError,
    MetadataDefValidationError,
)
from rdetoolkit.validation import (
    InvoiceValidator,
    MetadataDefValidator,
    invoice_validate,
    metadata_def_validate,
)


@pytest.fixture
def metadata_def_json_file():
    Path("temp").mkdir(parents=True, exist_ok=True)
    json_path = Path("temp").joinpath("test_metadata_def.json")
    json_data = {
        "constant": {
            "test_meta1": {
                "value": "value"
            },
            "test_meta2": {
                "value": 100
            },
            "test_meta3": {
                "value": True
            }
        },
        "variable": [
            {
                "test_meta1": {
                    "value": "v1"
                },
                "test_meta2": {
                    "value": 200,
                    "unit": "m"
                },
                "test_meta3": {
                    "value": False
                }
            },
            {
                "test_meta1": {
                    "value": "v1"
                },
                "test_meta2": {
                    "value": 200,
                    "unit": "m"
                },
                "test_meta3": {
                    "value": False
                }
            },
        ]
    }
    with open(json_path, mode="w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)

    yield json_path

    if json_path.exists():
        json_path.unlink()
    if Path("temp").exists():
        shutil.rmtree("temp")


@pytest.fixture
def invalid_metadata_def_json_file():
    Path("temp").mkdir(parents=True, exist_ok=True)
    json_path = Path("temp").joinpath("test_metadata_def.json")
    json_data = {
        "dummy1": {
            "test_meta1": "value",
            "test_meta2": 100,
            "test_meta3": True
        },
        "variable": [
            "test_meta1", "test_meta2", "test_meta3"
        ]
    }
    with open(json_path, mode="w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)

    yield json_path

    if json_path.exists():
        json_path.unlink()
    if Path("temp").exists():
        shutil.rmtree("temp")


def test_metadata_def_json_validation(metadata_def_json_file):
    instance = MetadataDefValidator()
    obj = instance.validate(path=metadata_def_json_file)
    assert isinstance(obj, dict)


def test_metadata_def_empty_json_validation():
    instance = MetadataDefValidator()
    obj = instance.validate(json_obj={})
    assert isinstance(obj, dict)


def test_invliad_metadata_def_json_validation(invalid_metadata_def_json_file):
    with pytest.raises(ValidationError):
        instance = MetadataDefValidator()
        _ = instance.validate(path=invalid_metadata_def_json_file)


def test_none_argments_metadata_def_json_validation():
    with pytest.raises(ValueError) as e:
        instance = MetadataDefValidator()
        _ = instance.validate()
    assert str(e.value) == "At least one of 'path' or 'json_obj' must be provided"


def test_two_argments_metadata_def_json_validation(invalid_metadata_def_json_file):
    data = {}
    with pytest.raises(ValueError) as e:
        instance = MetadataDefValidator()
        _ = instance.validate(path=invalid_metadata_def_json_file, json_obj=data)
    assert str(e.value) == "Both 'path' and 'json_obj' cannot be provided at the same time"


@pytest.mark.parametrize(
    "case, longchar", [
        ('success', 'a' * 1024),
        ('faild', 'a' * 1025)
    ]
)
def test_char_too_long_metadata_def_json_validation(case, longchar):
    json_data = {
        "constant": {
            "test_meta1": {
                "value": longchar
            },
            "test_meta2": {
                "value": 100
            },
            "test_meta3": {
                "value": True
            }
        },
        "variable": [
            {
                "test_meta1": {
                    "value": "v1"
                },
                "test_meta2": {
                    "value": 200,
                    "unit": "m"
                },
                "test_meta3": {
                    "value": False
                }
            },
            {
                "test_meta1": {
                    "value": "v1"
                },
                "test_meta2": {
                    "value": 200,
                    "unit": "m"
                },
                "test_meta3": {
                    "value": False
                }
            },
        ]
    }

    instance = MetadataDefValidator()
    if case == 'success':
        obj = instance.validate(json_obj=json_data)
        assert isinstance(obj, dict)
    else:
        with pytest.raises(ValueError) as e:
            obj = instance.validate(json_obj=json_data)
        assert "Value error, Value size exceeds 1024 bytes" in str(e.value)


@pytest.fixture
def validator_instance():
    schema_path = Path(__file__).parent.joinpath("samplefile", "invoice.schema.json")
    yield InvoiceValidator(schema_path)


def test_validate_none_path_obj():
    schema_path = Path(__file__).parent.joinpath("samplefile", "invoice.schema.json")
    iv = InvoiceValidator(schema_path)

    with pytest.raises(ValueError) as e:
        iv.validate()
    assert str(e.value) == "At least one of 'path' or 'obj' must be provided"


def test_validate_both_path_obj():
    schema_path = Path(__file__).parent.joinpath("samplefile", "invoice.schema.json")
    iv = InvoiceValidator(schema_path)

    with pytest.raises(ValueError) as e:
        iv.validate(obj={}, path="dummy")
    assert str(e.value) == "Both 'path' and 'obj' cannot be provided at the same time"


def test_validate_json(validator_instance):
    invoice_path = Path(__file__).parent.joinpath("samplefile", "invoice.json")
    obj = validator_instance.validate(path=invoice_path)
    assert isinstance(obj, dict)


def test_metadata_def_validate(metadata_def_json_file):
    metadata_def_validate(metadata_def_json_file)


def test_invalid_metadata_def_validate(invalid_metadata_def_json_file):
    with pytest.raises(MetadataDefValidationError) as e:
        metadata_def_validate(invalid_metadata_def_json_file)
    assert "Error in validating metadata_def.json" in str(e.value)


def test_invoice_path_metadata_def_validate():
    path = "dummy.metadata-def.json"
    with pytest.raises(FileNotFoundError) as e:
        metadata_def_validate(path)
    assert "The schema and path do not exist" in str(e.value)


def test_invoice_validate():
    invoice_path = Path(__file__).parent.joinpath("samplefile", "invoice.json")
    schema_path = Path(__file__).parent.joinpath("samplefile", "invoice.schema.json")
    invoice_validate(invoice_path, schema_path)


def test_invalid_invoice_validate():
    """input file: invoice_invalid.json
        "custom": {
            "sample1": null,
            "sample2": null,
            ....
        }
    """
    invoice_path = Path(__file__).parent.joinpath("samplefile", "invoice_invalid.json")
    schema_path = Path(__file__).parent.joinpath("samplefile", "invoice.schema.json")
    expected_value = "Error in validating invoice.schema.json:\nNone is not of type 'string'\n{'label': {'ja': 'サンプル１', 'en': 'sample1'}, 'type': 'string', 'format': 'date', 'options': {'unit': 'A'}}"
    with pytest.raises(InvoiceSchemaValidationError) as e:
        invoice_validate(invoice_path, schema_path)
    assert expected_value == str(e.value)


def test_invalid_basic_info_invoice_validate():
    invoice_path = Path(__file__).parent.joinpath("samplefile", "invoice_invalid_none_basic.json")
    schema_path = Path(__file__).parent.joinpath("samplefile", "invoice.schema.json")
    with pytest.raises(InvoiceSchemaValidationError) as e:
        invoice_validate(invoice_path, schema_path)
    assert "Error in validating system standard item in invoice.schema.json" in str(e.value)


def test_invalid_filepath_invoice_json():
    invoice_path = Path(__file__).parent.joinpath("samplefile", "invoice_invalid_none_basic.json")
    schema_path = "dummy_invoice.schema.json"
    with pytest.raises(FileNotFoundError) as e:
        invoice_validate(invoice_path, schema_path)
    assert "The schema and path do not exist" in str(e.value)

    invoice_path = "dummy_invoice.json"
    schema_path = Path(__file__).parent.joinpath("samplefile", "invoice.schema.json")
    with pytest.raises(FileNotFoundError) as e:
        invoice_validate(invoice_path, schema_path)
    assert "The schema and path do not exist" in str(e.value)
