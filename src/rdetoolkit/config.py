import os
from pathlib import Path
from typing import Any, Final, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field
from tomlkit.toml_file import TOMLFile

from rdetoolkit.models.rde2types import RdeInputDirPaths

CONFIG_FILE: Final = ["rdeconfig.yaml", ".rdeconfig.yaml", "rdeconfig.yml", ".rdeconfig.yaml"]
PYPROJECT_CONFIG_FILES: Final = ["pyproject.toml"]
CONFIG_FILES = CONFIG_FILE + PYPROJECT_CONFIG_FILES


class Config(BaseModel):
    """The configuration class used in RDEToolKit.

    Attributes:
        extendeds_mode (Optional[str]): The mode to run the RDEToolKit in. It can be either 'rdeformat' or 'multifile'. If not specified, it defaults to None.
        save_raw (bool): A boolean flag that indicates whether to automatically save raw data to the raw directory. It defaults to True.
        save_thumbnail_image (bool): A boolean flag that indicates whether to automatically save the main image to the thumbnail directory. It defaults to False.
        magic_variable (bool): A boolean flag that indicates whether to use the feature where specifying '${filename}' as the data name results in the filename being transcribed as the data name. It defaults to False.
    """

    model_config = ConfigDict(extra="allow")

    extendeds_mode: Optional[str] = Field(default=None, description="The mode to run the RDEtoolkit in. select: rdeformat, multifile")
    save_raw: bool = Field(default=True, description="Auto Save raw data to the raw directory")
    save_thumbnail_image: bool = Field(default=False, description="Auto Save main image to the thumbnail directory")
    magic_variable: bool = Field(default=False, description="The feature where specifying '${filename}' as the data name results in the filename being transcribed as the data name.")


def parse_config_file(*, path: Optional[str] = None) -> Config:
    """Parse the configuration file and return a Config object.

    Args:
        path (str, optional): The path to the configuration file. If not provided, the function will attempt to find and parse the default configuration file.

    Returns:
        Config: The parsed configuration object.

    Raises:
        FileNotFoundError: If the specified configuration file does not exist.

    File Loading Priority:
        1. If `path` is provided and the file extension is ".toml", the function will attempt to read the file as a TOML file.
        2. If `path` is provided and the file extension is ".yaml" or ".yml", the function will attempt to read the file as a YAML file.
        3. If `path` is not provided, the function will attempt to find and parse the default configuration file named "pyproject.toml" in the current working directory.

    Accepted Config Files:
        - "rdeconfig.yaml"
        - ".rdeconfig.yaml"
        - "rdeconfig.yml"
        - ".rdeconfig.yaml"
        - "pyproject.toml"

    Note:
        - If the specified configuration file does not exist or is not in the correct format, an empty Config object will be returned.

    Example:
        parse_config_file(path="config.yaml")

    """
    config_data: dict[str, Any] = {}
    if path is not None and Path(path).name not in CONFIG_FILES:
        return Config()

    if path is not None and is_toml(path):
        config_data = __read_pyproject_toml(path)
    elif path is not None and is_yaml(path):
        with open(path, encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
    elif path is None:
        project_path = Path.cwd()
        pyproject_toml = project_path.joinpath(PYPROJECT_CONFIG_FILES[0])
        config_data = __read_pyproject_toml(str(pyproject_toml))
    else:
        return Config()
    return Config(**config_data)


def __read_pyproject_toml(path: str) -> dict[str, Any]:
    """Read the pyproject.toml file and return the contents as a dictionary.

    Returns:
        dict[str, Any]: The contents of the pyproject.toml file.
    """
    toml = TOMLFile(path)
    obj = toml.read()
    return obj.get("tool", {}).get("rdetoolkit", {})


def is_toml(filename: str) -> bool:
    """Check if the given filename has a .toml extension.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the filename has a .toml extension, False otherwise.
    """
    return filename.lower().endswith(".toml")


def is_yaml(filename: str) -> bool:
    """Check if the given filename has a YAML file extension.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the filename has a YAML file extension, False otherwise.
    """
    return filename.lower().endswith(".yaml") or filename.lower().endswith(".yml")


def find_config_files(input_files: RdeInputDirPaths) -> list[str]:
    """Find and return a list of configuration files in the given input directory.

    Args:
        input_files (RdeInputDirPaths): An object containing the paths to the input directories.

    Returns:
        list[str]: A list of configuration file paths.

    """
    files: list[str] = []
    tasksupport_dir = input_files.tasksupport
    if not tasksupport_dir:
        return files
    existing_files = os.listdir(tasksupport_dir)
    for config_file in CONFIG_FILES:
        if config_file in existing_files:
            files.append(str(tasksupport_dir.joinpath(config_file)))
    files = sorted(files, key=lambda x: (is_toml(x), is_yaml(x)))
    return files
