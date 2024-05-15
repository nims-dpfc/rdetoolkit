import json
from pathlib import Path
import shutil
import pytest

from rdetoolkit.workflows import run
from rdetoolkit.config import Config


@pytest.fixture
def metadata_def_json_file():
    Path("data/tasksupport").mkdir(parents=True, exist_ok=True)
    json_path = Path("data/tasksupport").joinpath("metadata-def.json")
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


def test_run_config_not_none(inputfile_single, tasksupport, metadata_def_json_file):
    """configがNOneでないことを確認する"""
    tasksupport_path = Path("data/tasksupport")
    invoice_path = Path("data/invoice")
    invoice_path.mkdir(parents=True, exist_ok=True)
    invoice_filepath = Path(__file__).parent.joinpath("samplefile", "invoice.json")
    schema_filepath = Path(__file__).parent.joinpath("samplefile", "invoice.schema.json")
    shutil.copy2(invoice_filepath, invoice_path.joinpath("invoice.json"))
    shutil.copy2(schema_filepath, tasksupport_path.joinpath("invoice.schema.json"))

    config = Config()
    run(config=config)
    assert config is not None
