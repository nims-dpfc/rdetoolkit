import pytest
from pathlib import Path
import json

from pydantic import ValidationError

from rdetoolkit.models.invoice_schema import Options
from rdetoolkit.models.invoice_schema import InvoiceSchemaJson, MetaProperty, LangLabels, Properties


@pytest.fixture
def invoice_schema_json_full():
    parent_path = Path(__file__).parent
    test_invoice_schema_json = Path(parent_path, "samplefile", "invoice.schema.full.json")
    with open(test_invoice_schema_json) as f:
        data = json.load(f)
    yield data


@pytest.fixture
def invoice_schema_json_none_sample():
    parent_path = Path(__file__).parent
    test_invoice_schema_json = Path(parent_path, "samplefile", "invoice.schema_none_sample.json")
    with open(test_invoice_schema_json) as f:
        data = json.load(f)
    yield data


@pytest.fixture
def invoice_schema_json_none_custom():
    parent_path = Path(__file__).parent
    test_invoice_schema_json = Path(parent_path, "samplefile", "invoice.schema_none_custom.json")
    with open(test_invoice_schema_json) as f:
        data = json.load(f)
    yield data


@pytest.fixture
def invoice_schema_json_none_generalAttributes():
    parent_path = Path(__file__).parent
    test_invoice_schema_json = Path(parent_path, "samplefile", "invoice.schema_none_generalAttributes.json")
    with open(test_invoice_schema_json) as f:
        data = json.load(f)
    yield data


@pytest.fixture
def invoice_schema_json_none_specificAttributes():
    parent_path = Path(__file__).parent
    test_invoice_schema_json = Path(parent_path, "samplefile", "invoice.schema_none_specificAttributes.json")
    with open(test_invoice_schema_json) as f:
        data = json.load(f)
    yield data


def test_invoice_scheam_json_full(invoice_schema_json_full):
    """Test case when all fields are specified in 'required'."""
    obj = InvoiceSchemaJson(**invoice_schema_json_full)
    assert isinstance(obj, InvoiceSchemaJson)


def test_invoice_scheam_json_none_sample(invoice_schema_json_none_sample):
    """Test case when 'sample' is specified in 'required', but the 'sample' field does not exist."""
    with pytest.raises(ValidationError) as e:
        _ = InvoiceSchemaJson(**invoice_schema_json_none_sample)
    assert "Value error, sample is required but is None" in str(e.value)


def test_invoice_scheam_json_none_custom(invoice_schema_json_none_custom):
    """Test case for creating an InvoiceSchemaJson object with None custom fields."""
    obj = InvoiceSchemaJson(**invoice_schema_json_none_custom)
    assert isinstance(obj, InvoiceSchemaJson)


def test_invoice_scheam_json_none_generalAttributes(invoice_schema_json_none_generalAttributes):
    """Test case for creating an InvoiceSchemaJson object with None generalAttributes."""
    obj = InvoiceSchemaJson(**invoice_schema_json_none_generalAttributes)
    assert isinstance(obj, InvoiceSchemaJson)


def test_invoice_scheam_json_none_specificAttributes(invoice_schema_json_none_specificAttributes):
    """Test case for creating an InvoiceSchemaJson object with None specificAttributes."""
    obj = InvoiceSchemaJson(**invoice_schema_json_none_specificAttributes)
    assert isinstance(obj, InvoiceSchemaJson)


def test_oprions_textare_row():
    with pytest.raises(ValueError) as e:
        _ = Options(widget='textarea')
    assert 'Value error, rows must be set when widget is "textarea"' in str(e.value)


def test_metaproperty_const_validation():
    # Test that a ValueError is raised when const is a different type than value_type
    with pytest.raises(ValueError) as e:
        MetaProperty(label=LangLabels(ja="Test", en="Test"), type="string", const=123)
    assert "Custom Validation: The two objects are of different types." in str(e.value)


def test_metaproperty_maximum_validation():
    # Test that a ValueError is raised when maximum is set but value_type is not integer or number
    with pytest.raises(ValueError) as e:
        MetaProperty(label=LangLabels(ja="Test", en="Test"), type="string", maximum=123)
    assert "Custom Validation: The field must be of type integer or number." in str(e.value)


def test_metaproperty_minlength_validation():
    # Test that a ValueError is raised when minLength is set but value_type is not string
    with pytest.raises(ValueError) as e:
        MetaProperty(label=LangLabels(ja="Test", en="Test"), type="integer", minLength=1)
    assert "Custom Validation: The field must be of type string." in str(e.value)


def test_create_invoice_schema_json():
    obj = InvoiceSchemaJson(
        version="https://json-schema.org/draft/2020-12/schema",
        schema_id="https://rde.nims.go.jp/rde/dataset-templates/dataset_template_custom_sample/invoice.schema.json",
        description="RDEデータセットテンプレートテスト用ファイル",
        type="object",
        properties=Properties()
    )
    assert isinstance(obj.model_dump_json(), str)
