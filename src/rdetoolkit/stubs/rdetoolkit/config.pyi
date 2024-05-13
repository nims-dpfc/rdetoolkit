from _typeshed import Incomplete
from pydantic import BaseModel
from rdetoolkit.models.rde2types import RdeInputDirPaths as RdeInputDirPaths
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
def find_config_files(input_files: RdeInputDirPaths) -> list[str]: ...
