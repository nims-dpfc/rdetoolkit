from pathlib import Path
from typing import Generator, Optional

from _typeshed import Incomplete
from rdetoolkit.exceptions import StructuredError as StructuredError
from rdetoolkit.invoiceFile import backup_invoice_json_files as backup_invoice_json_files
from rdetoolkit.models.rde2types import RdeFormatFlags as RdeFormatFlags
from rdetoolkit.models.rde2types import RdeInputDirPaths as RdeInputDirPaths
from rdetoolkit.models.rde2types import RdeOutputResourcePath as RdeOutputResourcePath
from rdetoolkit.modeproc import _CallbackType
from rdetoolkit.modeproc import excel_invoice_mode_process as excel_invoice_mode_process
from rdetoolkit.modeproc import invoice_mode_process as invoice_mode_process
from rdetoolkit.modeproc import multifile_mode_process as multifile_mode_process
from rdetoolkit.modeproc import rdeformat_mode_process as rdeformat_mode_process
from rdetoolkit.modeproc import selected_input_checker as selected_input_checker
from rdetoolkit.rde2util import StorageDir as StorageDir
from rdetoolkit.rdelogger import get_logger as get_logger
from rdetoolkit.rdelogger import write_job_errorlog_file as write_job_errorlog_file

logger: Incomplete

def check_files(srcpaths: RdeInputDirPaths, *, fmt_flags: RdeFormatFlags) -> tuple[list[tuple[Path, ...]], Optional[Path]]: ...
def generate_folder_paths_iterator(raw_files_group: list[tuple[Path, ...]], invoice_org_filepath: Path, invoice_schema_filepath: Path) -> Generator[RdeOutputResourcePath, None, None]: ...
def run(*, custom_dataset_function: Optional[_CallbackType] = ...): ...
