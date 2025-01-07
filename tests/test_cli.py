import json
import os
import platform
import shutil
from distutils.version import StrictVersion
from pathlib import Path
from unittest.mock import patch


import pytest
from click.testing import CliRunner
from rdetoolkit.cli import (
    init,
    version,
    make_excelinvoice,
)
from rdetoolkit.cmd.command import (
    DockerfileGenerator,
    MainScriptGenerator,
    RequirementsTxtGenerator,
    InvoiceJsonGenerator,
    InvoiceSchemaJsonGenerator,
    MetadataDefJsonGenerator,
)


def test_make_main_py():
    test_path = Path("test_main.py")
    gen = MainScriptGenerator(test_path)
    gen.generate()

    with open(test_path, encoding="utf-8") as f:
        content = f.read()

    expected_content = """# The following script is a template for the source code.

import rdetoolkit

rdetoolkit.workflows.run()
"""
    assert content == expected_content
    test_path.unlink()

    if os.path.exists("container"):
        shutil.rmtree("container")


def test_make_dockerfile():
    test_path = Path("Dockerfile")
    gen = DockerfileGenerator(test_path)
    gen.generate()

    with open(test_path, encoding="utf-8") as f:
        content = f.read()

    expected_content = """FROM python:3.11.9

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY main.py /app
COPY modules/ /app/modules/
"""
    assert content == expected_content
    test_path.unlink()

    if os.path.exists("container"):
        shutil.rmtree("container")


def test_make_requirements_txt():
    test_path = Path("test_requirements.txt")
    gen = RequirementsTxtGenerator(test_path)
    gen.generate()

    with open(test_path, encoding="utf-8") as f:
        content = f.read()

    expected_content = """# ----------------------------------------------------
# Please add the desired packages and install the libraries after that.
# Then, run
#
# pip install -r requirements.txt
#
# on the terminal to install the required packages.
# ----------------------------------------------------
# ex.
# pandas==2.0.3
# numpy
rdetoolkit==1.1.0
"""
    assert content == expected_content
    test_path.unlink()

    if os.path.exists("container"):
        shutil.rmtree("container")

    if os.path.exists("test_requirements.txt"):
        os.remove("test_requirements.txt")


def test_make_template_json():
    test_path = Path("test_template.json")
    gen = InvoiceJsonGenerator(test_path)
    gen.generate()

    assert test_path.exists()
    test_path.unlink()

    if os.path.exists("container"):
        shutil.rmtree("container")


def test_make_schema_json():
    test_path = Path("test_template.json")
    gen = InvoiceSchemaJsonGenerator(test_path)
    gen.generate()

    assert test_path.exists()
    test_path.unlink()

    if os.path.exists("container"):
        shutil.rmtree("container")


def test_make_metadata_def_json():
    test_path = Path("test_template.json")
    gen = MetadataDefJsonGenerator(test_path)
    gen.generate()

    with open(test_path, encoding="utf-8") as f:
        contents = json.load(f)

    assert contents == {}
    assert test_path.exists()
    test_path.unlink()

    if os.path.exists("container"):
        shutil.rmtree("container")


def test_init_creation():
    runner = CliRunner()

    result = runner.invoke(init)

    # 出力メッセージのテスト
    assert "Ready to develop a structured program for RDE." in result.output
    assert "Done!" in result.output

    dirs = [
        Path("container/modules"),
        Path("container/data/inputdata"),
        Path("container/data/invoice"),
        Path("container/data/tasksupport"),
        Path("input/invoice"),
        Path("input/inputdata"),
        Path("templates/tasksupport"),
    ]
    for d in dirs:
        assert d.exists()

    files = [
        Path("container/main.py"),
        Path("container/requirements.txt"),
        Path("container/data/invoice/invoice.json"),
        Path("container/data/tasksupport/invoice.schema.json"),
        Path("container/data/tasksupport/metadata-def.json"),
        Path("input/invoice/invoice.json"),
        Path("templates/tasksupport/invoice.schema.json"),
        Path("templates/tasksupport/metadata-def.json"),
    ]
    for file in files:
        assert file.exists()

    # Test for files not created
    assert not Path("container/modules/modules.py").exists()

    if os.path.exists("container"):
        shutil.rmtree("container")

    if os.path.exists("input"):
        shutil.rmtree("input")

    if os.path.exists("templates"):
        shutil.rmtree("templates")


def test_init_no_overwrite():
    """initを実行して既存のファイルが上書きされないことをテスト"""
    runner = CliRunner()

    with runner.isolated_filesystem():
        runner.invoke(init)

        with open(Path("container/main.py"), "a", encoding="utf-8") as f:
            f.write("# Sample test message")

        runner.invoke(init)

        with open(Path("container/main.py"), encoding="utf-8") as f:
            content = f.read()
            assert "# Sample test message" in content


@pytest.fixture
def get_version_from_pyprojecttoml_py39_py310():
    import toml

    path = Path(os.path.dirname(os.path.dirname(__file__)), "pyproject.toml")
    with open(path, encoding="utf-8") as f:
        parse_toml = toml.loads(f.read())
    return parse_toml["project"]["version"]


@pytest.fixture
def get_version_from_pyprojecttoml_py311():
    py_version = platform.python_version_tuple()
    if StrictVersion(f"{py_version[0]}.{py_version[1]}") >= StrictVersion("3.11"):
        import tomllib

        path = Path(os.path.dirname(os.path.dirname(__file__)), "pyproject.toml")
        with open(path, encoding="utf-8") as f:
            parse_toml = tomllib.loads(f.read())
        return parse_toml["project"]["version"]
    return ""


def test_version(get_version_from_pyprojecttoml_py39_py310, get_version_from_pyprojecttoml_py311):
    py_version = platform.python_version_tuple()
    if StrictVersion(f"{py_version[0]}.{py_version[1]}") >= StrictVersion("3.11"):
        v = get_version_from_pyprojecttoml_py311 + "\n"
    else:
        v = get_version_from_pyprojecttoml_py39_py310 + "\n"

    runner = CliRunner()

    result = runner.invoke(version)

    assert v == result.output


@pytest.fixture
def temp_output_path(tmp_path):
    yield tmp_path / "output.xlsx"


@pytest.fixture
def temp_output_folder(tmp_path):
    output_folder = tmp_path / "invoices"
    yield output_folder


def test_make_excelinvoice_file_mode_success(ivnoice_schema_json_with_full_sample_info, temp_output_path):
    """'file' モードでの正常な実行をテスト"""
    runner = CliRunner()
    result = runner.invoke(
        make_excelinvoice,
        [
            str(ivnoice_schema_json_with_full_sample_info),
            '-o',
            str(temp_output_path)
        ],
    )

    assert result.exit_code == 0
    assert temp_output_path.exists()
    assert "📄 Generating ExcelInvoice template..." in result.output
    assert f"- Schema: {Path(ivnoice_schema_json_with_full_sample_info).resolve()}" in result.output
    assert f"- Output: {temp_output_path}" in result.output
    assert "- Mode: file" in result.output
    assert f"✨ ExcelInvoice template generated successfully! : {temp_output_path}" in result.output


def test_make_excelinvoice_folder_mode_success(ivnoice_schema_json_with_full_sample_info, temp_output_path):
    """'file' モードでの正常な実行をテスト"""
    runner = CliRunner()
    result = runner.invoke(
        make_excelinvoice,
        [
            str(ivnoice_schema_json_with_full_sample_info),
            '-o',
            str(temp_output_path),
            "-m",
            "folder",
        ],
    )

    assert result.exit_code == 0
    assert temp_output_path.exists()
    assert "📄 Generating ExcelInvoice template..." in result.output
    assert f"- Schema: {Path(ivnoice_schema_json_with_full_sample_info).resolve()}" in result.output
    assert f"- Output: {temp_output_path}" in result.output
    assert "- Mode: folder" in result.output
    assert f"✨ ExcelInvoice template generated successfully! : {temp_output_path}" in result.output


def test_generate_excelinvoice_command_schema_error(invalid_ivnoice_schema_json, temp_output_path):
    """スキーマエラーテスト"""
    runner = CliRunner()
    result = runner.invoke(
        make_excelinvoice,
        [
            str(invalid_ivnoice_schema_json),
            '-o',
            str(temp_output_path),
        ],
    )

    assert "📄 Generating ExcelInvoice template..." in result.output
    assert f"- Schema: {Path(invalid_ivnoice_schema_json).resolve()}" in result.output
    assert f"- Output: {temp_output_path}" in result.output
    assert "- Mode: file" in result.output
    assert "🔥 Schema Error" in result.output


def test_generate_excelinvoice_command_unexpected_error(ivnoice_schema_json_with_full_sample_info, temp_output_path):
    """エラーテスト"""
    with patch('rdetoolkit.invoicefile.ExcelInvoiceFile.generate_template') as mock_generate:
        mock_generate.side_effect = Exception("Unexpected test error")
        runner = CliRunner()
        result = runner.invoke(
            make_excelinvoice,
            [
                str(ivnoice_schema_json_with_full_sample_info),
                '-o',
                str(temp_output_path),
            ],
        )

        assert "📄 Generating ExcelInvoice template..." in result.output
        assert f"- Schema: {Path(ivnoice_schema_json_with_full_sample_info).resolve()}" in result.output
        assert f"- Output: {temp_output_path}" in result.output
        assert "- Mode: file" in result.output
        assert "🔥 Error: An unexpected error occurred: Unexpected test error" in result.output
        assert result.exit_code != 0
