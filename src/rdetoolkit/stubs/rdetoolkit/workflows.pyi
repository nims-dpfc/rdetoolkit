from collections.abc import Generator
from pathlib import Path
from rdetoolkit.config import Config as Config, load_config as load_config
from rdetoolkit.exceptions import StructuredError as StructuredError, handle_exception as handle_exception
from rdetoolkit.invoicefile import backup_invoice_json_files as backup_invoice_json_files
from rdetoolkit.models.rde2types import RawFiles as RawFiles, RdeInputDirPaths as RdeInputDirPaths, RdeOutputResourcePath as RdeOutputResourcePath
from rdetoolkit.modeproc import _CallbackType, excel_invoice_mode_process as excel_invoice_mode_process, invoice_mode_process as invoice_mode_process, multifile_mode_process as multifile_mode_process, rdeformat_mode_process as rdeformat_mode_process, selected_input_checker as selected_input_checker
from rdetoolkit.rde2util import StorageDir as StorageDir
from rdetoolkit.rdelogger import get_logger as get_logger, write_job_errorlog_file as write_job_errorlog_file

def check_files(srcpaths: RdeInputDirPaths, *, mode: str | None) -> tuple[RawFiles, Path | None]: ...
def generate_folder_paths_iterator(raw_files_group: RawFiles, invoice_org_filepath: Path, invoice_schema_filepath: Path) -> Generator[RdeOutputResourcePath, None, None]: ...
def run(*, custom_dataset_function: _CallbackType | None = ..., config: Config | None = ...) -> None: ...
