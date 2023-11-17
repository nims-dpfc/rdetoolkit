import os
from pathlib import Path
import shutil
import pytest
import json
from click.testing import CliRunner
import platform
from distutils.version import StrictVersion

from rdetoolkit.__main__ import make_main_py, make_requirements_txt, make_template_json, init, version


def test_make_main_py():
    test_path = Path("test_main.py")
    make_main_py(test_path)

    with open(test_path, 'r', encoding="utf-8") as f:
        content = f.read()

    expected_content = """import rdetoolkit

rdetoolkit.run()
"""
    assert content == expected_content
    test_path.unlink()

    if os.path.exists("container"):
        shutil.rmtree("container")


def test_make_requirements_txt():
    test_path = Path("test_requirements.txt")
    make_requirements_txt(test_path)

    with open(test_path, 'r', encoding="utf-8") as f:
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
"""
    assert content == expected_content
    test_path.unlink()

    if os.path.exists("container"):
        shutil.rmtree("container")


def test_make_template_json():
    test_path = Path("test_template.json")
    make_template_json(test_path)

    with open(test_path, 'r', encoding="utf-8") as f:
        content = json.load(f)

    assert content == {}
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
        Path('container/modules'),
        Path('container/data/inputdata'),
        Path('container/data/invoice'),
        Path('container/data/tasksupport')
    ]
    for dir in dirs:
        assert dir.exists()

    files = [
    Path('container/main.py'),
        Path('container/requirements.txt'),
        Path('container/data/invoice/invoice.json'),
        Path('container/data/tasksupport/invoice.schema.json'),
        Path('container/data/tasksupport/metadata-def.json')
    ]
    for file in files:
        assert file.exists()

    if os.path.exists("container"):
        shutil.rmtree("container")


def test_init_no_overwrite():
    """initを実行して既存のファイルが上書きされないことをテスト"""
    runner = CliRunner()

    with runner.isolated_filesystem():
        runner.invoke(init)

        with open(Path("container/main.py"), "a", encoding="utf-8") as f:
            f.write("# Sample test message")

        runner.invoke(init)

        with open(Path("container/main.py"), "r", encoding="utf-8") as f:
            content = f.read()
            assert "# Sample test message" in content

@pytest.fixture
def get_version_from_pyprojecttoml_py39_py310():
    import toml
    path = Path(os.path.dirname(os.path.dirname(__file__)), "pyproject.toml")
    with open(path, mode="r", encoding="utf-8") as f:
        parse_toml = toml.loads(f.read())
    return parse_toml['project']['version']

@pytest.fixture
def get_version_from_pyprojecttoml_py311():
    py_version = platform.python_version_tuple()
    if StrictVersion(f"{py_version[0]}.{py_version[1]}") >= StrictVersion("3.11"):
        import tomllib
        path = Path(os.path.dirname(os.path.dirname(__file__)), "pyproject.toml")
        with open(path, mode="r", encoding="utf-8") as f:
            parse_toml = tomllib.loads(f.read())
        return parse_toml['project']['version']
    return ""

def test_version(get_version_from_pyprojecttoml_py39_py310, get_version_from_pyprojecttoml_py311):
    py_version = platform.python_version_tuple()
    if StrictVersion(f"{py_version[0]}.{py_version[1]}") >= StrictVersion("3.11"):
        v = get_version_from_pyprojecttoml_py311 + '\n'
    else:
        v = get_version_from_pyprojecttoml_py39_py310 + '\n'

    runner = CliRunner()

    result = runner.invoke(version)

    assert v == result.output
