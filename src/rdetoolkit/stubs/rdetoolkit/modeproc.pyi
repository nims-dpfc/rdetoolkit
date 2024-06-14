from pathlib import Path
from rdetoolkit import img2thumb as img2thumb
from rdetoolkit.config import Config as Config
from rdetoolkit.exceptions import StructuredError as StructuredError
from rdetoolkit.impl.input_controller import (
    ExcelInvoiceChecker as ExcelInvoiceChecker,
    InvoiceChecker as InvoiceChecker,
    MultiFileChecker as MultiFileChecker,
    RDEFormatChecker as RDEFormatChecker,
)
from rdetoolkit.interfaces.filechecker import IInputFileChecker as IInputFileChecker
from rdetoolkit.invoicefile import (
    ExcelInvoiceFile as ExcelInvoiceFile,
    InvoiceFile as InvoiceFile,
    apply_magic_variable as apply_magic_variable,
    update_description_with_features as update_description_with_features,
)
from rdetoolkit.models.rde2types import RdeInputDirPaths as RdeInputDirPaths, RdeOutputResourcePath as RdeOutputResourcePath
from rdetoolkit.validation import invoice_validate as invoice_validate, metadata_validate as metadata_validate

def rdeformat_mode_process(
    srcpaths: RdeInputDirPaths,
    resource_paths: RdeOutputResourcePath,
    datasets_process_function: _CallbackType | None = ...,
    config: Config | None = ...,
) -> None: ...
def multifile_mode_process(
    srcpaths: RdeInputDirPaths,
    resource_paths: RdeOutputResourcePath,
    datasets_process_function: _CallbackType | None = ...,
    config: Config | None = ...,
) -> None: ...
def excel_invoice_mode_process(
    srcpaths: RdeInputDirPaths,
    resource_paths: RdeOutputResourcePath,
    excel_invoice_file: Path,
    idx: int,
    datasets_process_function: _CallbackType | None = ...,
    config: Config | None = ...,
) -> None: ...
def invoice_mode_process(
    srcpaths: RdeInputDirPaths,
    resource_paths: RdeOutputResourcePath,
    datasets_process_function: _CallbackType | None = ...,
    config: Config | None = ...,
) -> None: ...
def copy_input_to_rawfile_for_rdeformat(resource_paths: RdeOutputResourcePath) -> None: ...
def copy_input_to_rawfile(raw_dir_path: Path, raw_files: tuple[Path, ...]) -> None: ...
def selected_input_checker(src_paths: RdeInputDirPaths, unpacked_dir_path: Path, mode: str | None) -> IInputFileChecker: ...
