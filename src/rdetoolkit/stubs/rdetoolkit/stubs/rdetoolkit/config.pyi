from _typeshed import Incomplete as Incomplete
from pathlib import Path
from pydantic import BaseModel
from rdetoolkit.models.rde2types import RdeFsPath as RdeFsPath
from typing import Final, Optional

CONFIG_FILE: Final[Incomplete]
PYPROJECT_CONFIG_FILES: Final[Incomplete]
CONFIG_FILES: Incomplete

class Config(BaseModel):
    model_config: Incomplete
    extended_mode: Optional[str]
    save_raw: bool
    save_thumbnail_image: bool
    magic_variable: bool

def parse_config_file(*, path: Optional[str] = ...) -> Config: ...
def is_toml(filename: str) -> bool: ...
def is_yaml(filename: str) -> bool: ...
def find_config_files(target_dir_path: RdeFsPath) -> list[str]: ...
def get_pyproject_toml() -> Optional[Path]: ...
def get_config(target_dir_path: RdeFsPath): ...
def load_config(tasksupport_path: RdeFsPath, *, config: Optional[Config] = ...): ...
