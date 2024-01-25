from pathlib import Path
from typing import Optional

from rdetoolkit import img2thumb as img2thumb
from rdetoolkit.exceptions import StructuredError as StructuredError
from rdetoolkit.impl.input_controller import ExcelInvoiceChecker as ExcelInvoiceChecker
from rdetoolkit.impl.input_controller import InvoiceChechker as InvoiceChechker
from rdetoolkit.impl.input_controller import MultiFileChecker as MultiFileChecker
from rdetoolkit.impl.input_controller import RDEFormatChecker as RDEFormatChecker
from rdetoolkit.interfaces.filechecker import IInputFileChecker as IInputFileChecker
from rdetoolkit.invoiceFile import ExcelInvoiceFile as ExcelInvoiceFile
from rdetoolkit.invoiceFile import InvoiceFile as InvoiceFile
from rdetoolkit.invoiceFile import apply_default_filename_mapping_rule as apply_default_filename_mapping_rule
from rdetoolkit.invoiceFile import update_description_with_features as update_description_with_features
from rdetoolkit.models.rde2types import RdeFormatFlags as RdeFormatFlags
from rdetoolkit.models.rde2types import RdeInputDirPaths as RdeInputDirPaths
from rdetoolkit.models.rde2types import RdeOutputResourcePath as RdeOutputResourcePath
from rdetoolkit.rde2util import read_from_json_file as read_from_json_file

def rdeformat_mode_process(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath, datasets_process_function: Optional[_CallbackType] = ...): ...
def multifile_mode_process(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath, datasets_process_function: Optional[_CallbackType] = ...): ...
def excel_invoice_mode_process(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath, excel_invoice_file: Path, idx: int, datasets_process_function: Optional[_CallbackType] = ...): ...
def invoice_mode_process(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath, datasets_process_function: Optional[_CallbackType] = ...): ...
def copy_input_to_rawfile_for_rdeformat(resource_paths: RdeOutputResourcePath): ...
def copy_input_to_rawfile(raw_dir_path: Path, raw_files: tuple[Path, ...]): ...
def selected_input_checker(src_paths: RdeInputDirPaths, unpacked_dir_path: Path, fmtflags: RdeFormatFlags) -> IInputFileChecker: ...
