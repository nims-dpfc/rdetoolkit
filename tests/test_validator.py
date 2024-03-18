import json
import shutil
from pathlib import Path

import pytest
from pydantic import ValidationError

from rdetoolkit.models.metadata import MetadataDefItem
from rdetoolkit.validation import metadata_def_json_validator


@pytest.fixture
def json_file():
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
def invalid_json_file():
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


def test_metadata_def_json_validation(json_file):
    obj = metadata_def_json_validator(path=json_file)
    assert isinstance(obj, MetadataDefItem)


def test_invliad_metadata_def_json_validation(invalid_json_file):
    with pytest.raises(ValidationError):
        metadata_def_json_validator(path=invalid_json_file)


def test_none_argments_metadata_def_json_validation():
    with pytest.raises(ValueError) as e:
        metadata_def_json_validator()
    assert str(e.value) == "At least one of 'path' or 'json_obj' must be provided"


def test_two_argments_metadata_def_json_validation(invalid_json_file):
    data = {}
    with pytest.raises(ValueError) as e:
        metadata_def_json_validator(path=invalid_json_file, json_obj=data)
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

    if case == 'success':
        obj = metadata_def_json_validator(json_obj=json_data)
        assert isinstance(obj, MetadataDefItem)
    else:
        with pytest.raises(ValidationError) as e:
            metadata_def_json_validator(json_obj=json_data)
        assert e.value.errors()[0]["msg"] == "Value error, Value size exceeds 1024 bytes"


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(__file__))
    test_json = "metadata.json"
    metadata_def_json_validator(path=test_json)
