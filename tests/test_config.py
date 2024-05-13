import os
from pathlib import Path
import shutil

import pytest
import yaml
from rdetoolkit.config import Config, is_toml, is_yaml, parse_config_file, get_config
from tomlkit import document, table
from tomlkit.toml_file import TOMLFile


def test_is_toml():
    assert is_toml("config.toml") is True
    assert is_toml("config.yaml") is False
    assert is_toml("config.yml") is False
    assert is_toml("config.txt") is False


def test_is_yaml():
    assert is_yaml("config.toml") is False
    assert is_yaml("config.yaml") is True
    assert is_yaml("config.yml") is True
    assert is_yaml("config.txt") is False


@pytest.fixture()
def config_yaml():
    data = {
        "extendeds_mode": "rdeformat",
        "save_raw": True,
        "magic_variable": False,
        "save_thumbnail_image": True
    }
    test_yaml_path = "rdeconfig.yaml"
    with open(test_yaml_path, mode="w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    yield test_yaml_path

    if Path(test_yaml_path).exists():
        Path(test_yaml_path).unlink()


@pytest.fixture()
def dot_config_yaml():
    data = {
        "extendeds_mode": "rdeformat",
        "save_raw": True,
        "magic_variable": False,
        "save_thumbnail_image": True
    }
    test_yaml_path = ".rdeconfig.yaml"
    with open(test_yaml_path, mode="w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    yield test_yaml_path

    if Path(test_yaml_path).exists():
        Path(test_yaml_path).unlink()


@pytest.fixture()
def config_yml():
    dirname = Path("tasksupport")
    dirname.mkdir(exist_ok=True)
    data = {
        "extendeds_mode": "rdeformat",
        "save_raw": True,
        "magic_variable": False,
        "save_thumbnail_image": True
    }
    test_yaml_path = dirname.joinpath("rdeconfig.yml")
    with open(test_yaml_path, mode="w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    yield test_yaml_path

    if Path(test_yaml_path).exists():
        Path(test_yaml_path).unlink()
    if dirname.exists():
        dirname.rmdir()


@pytest.fixture()
def dot_config_yml():
    dirname = Path("tasksupport")
    dirname.mkdir(exist_ok=True)
    data = {
        "extendeds_mode": "rdeformat",
        "save_raw": True,
        "magic_variable": False,
        "save_thumbnail_image": True
    }
    test_yaml_path = dirname.joinpath(".rdeconfig.yml")
    with open(test_yaml_path, mode="w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    yield test_yaml_path

    if Path(test_yaml_path).exists():
        Path(test_yaml_path).unlink()
    if dirname.exists():
        dirname.rmdir()


@pytest.fixture()
def invalid_config_yaml():
    dirname = Path("tasksupport")
    dirname.mkdir(exist_ok=True)
    data = {
        "extendeds_mode": "rdeformat",
        "save_raw": True,
        "magic_variable": False,
        "save_thumbnail_image": True
    }
    test_yaml_path = dirname.joinpath("invalid_rdeconfig.yaml")
    with open(test_yaml_path, mode="w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    yield test_yaml_path

    if Path(test_yaml_path).exists():
        Path(test_yaml_path).unlink()
    if dirname.exists():
        dirname.rmdir()


@pytest.fixture
def test_pyproject_toml():
    test_file = os.path.join(os.path.dirname(__file__), "samplefile/pyproject.toml")
    toml = TOMLFile(test_file)
    doc = document()
    doc["tool"] = table()
    doc["tool"]["rdetoolkit"] = table()
    doc["tool"]["rdetoolkit"]["extendeds_mode"] = "rdeformat"
    doc["tool"]["rdetoolkit"]["save_raw"] = True
    doc["tool"]["rdetoolkit"]["magic_variable"] = False
    doc["tool"]["rdetoolkit"]["save_thumbnail_image"] = True
    toml.write(doc)
    yield test_file

    if Path(test_file).exists():
        Path(test_file).unlink()


@pytest.fixture
def test_cwd_pyproject_toml():
    test_file = "pyproject.toml"
    backup_path = Path(test_file).with_suffix(Path(test_file).suffix + ".bak")
    if Path(test_file).exists():
        # backup
        shutil.copy(Path(test_file), backup_path)
    doc = document()
    doc["tool"] = table()
    doc["tool"]["rdetoolkit"] = table()
    doc["tool"]["rdetoolkit"]["extendeds_mode"] = "multifile"
    doc["tool"]["rdetoolkit"]["save_raw"] = True
    doc["tool"]["rdetoolkit"]["magic_variable"] = False
    doc["tool"]["rdetoolkit"]["save_thumbnail_image"] = True
    toml = TOMLFile(test_file)
    toml.write(doc)
    yield test_file

    if Path(test_file).exists():
        Path(test_file).unlink()
    if Path(backup_path).exists():
        shutil.copy(backup_path, test_file)
        Path(backup_path).unlink()


def test_parse_config_file(config_yaml):
    config = parse_config_file(path=config_yaml)
    assert isinstance(config, Config)
    assert config.extendeds_mode == 'rdeformat'
    assert config.save_raw is True
    assert config.save_thumbnail_image is True
    assert config.magic_variable is False


def test_parse_config_file_specificaton_pyprojecttoml(test_pyproject_toml):
    config = parse_config_file(path=test_pyproject_toml)
    assert isinstance(config, Config)
    assert config.extendeds_mode == 'rdeformat'
    assert config.save_raw is True
    assert config.save_thumbnail_image is True
    assert config.magic_variable is False


def test_parse_config_file_current_project_pyprojecttoml(test_cwd_pyproject_toml):
    config = parse_config_file()
    assert isinstance(config, Config)
    assert config.extendeds_mode == 'multifile'
    assert config.save_raw is True
    assert config.save_thumbnail_image is True
    assert config.magic_variable is False


def test_sucess_get_config_yaml(config_yaml):
    expected_text = Config(extendeds_mode='rdeformat', save_raw=True, save_thumbnail_image=True, magic_variable=False)
    valid_dir = Path.cwd()
    config = get_config(valid_dir)
    assert config == expected_text


def test_sucess_get_config_dot_yaml(dot_config_yaml):
    expected_text = Config(extendeds_mode='rdeformat', save_raw=True, save_thumbnail_image=True, magic_variable=False)
    valid_dir = Path.cwd()
    config = get_config(valid_dir)
    assert config == expected_text


def test_sucess_get_config_yml(config_yml):
    expected_text = Config(extendeds_mode='rdeformat', save_raw=True, save_thumbnail_image=True, magic_variable=False)
    valid_dir = Path("tasksupport")
    config = get_config(valid_dir)
    assert config == expected_text


def test_sucess_get_config_dot_yml(dot_config_yml):
    expected_text = Config(extendeds_mode='rdeformat', save_raw=True, save_thumbnail_image=True, magic_variable=False)
    valid_dir = Path("tasksupport")
    config = get_config(valid_dir)
    assert config == expected_text


def test_invalid_get_config_yml(invalid_config_yaml):
    expected_text = Config(extendeds_mode=None, save_raw=True, save_thumbnail_image=False, magic_variable=False)
    valid_dir = Path("tasksupport")
    config = get_config(valid_dir)
    assert config == expected_text


def test_get_config_pyprojecttoml(test_cwd_pyproject_toml):
    expected_text = Config(extendeds_mode='multifile', save_raw=True, save_thumbnail_image=True, magic_variable=False)
    valid_dir = Path.cwd()
    config = get_config(valid_dir)
    assert config == expected_text
