from _typeshed import Incomplete as Incomplete
from pathlib import Path
from rdetoolkit.config import Config as Config
from rdetoolkit.models.rde2types import RawFiles as RawFiles, RdeInputDirPaths as RdeInputDirPaths, RdeOutputResourcePath as RdeOutputResourcePath
from rdetoolkit.modeproc import _CallbackType
from typing import Generator, Optional

logger: Incomplete

def check_files(srcpaths: RdeInputDirPaths, *, mode: Optional[str]) -> tuple[RawFiles, Optional[Path]]: ...
def generate_folder_paths_iterator(raw_files_group: RawFiles, invoice_org_filepath: Path, invoice_schema_filepath: Path) -> Generator[RdeOutputResourcePath, None, None]: ...
def run(*, custom_dataset_function: Optional[_CallbackType] = ..., config: Optional[Config] = ...): ...