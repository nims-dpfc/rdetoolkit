from pathlib import Path
from typing import Optional

from _typeshed import Incomplete
from rdetoolkit.exceptions import StructuredError as StructuredError
from rdetoolkit.impl import compressed_controller as compressed_controller
from rdetoolkit.interfaces.filechecker import IInputFileChecker as IInputFileChecker
from rdetoolkit.invoiceFile import readExcelInvoice as readExcelInvoice
from rdetoolkit.models.rde2types import ExcelInvoicePathList as ExcelInvoicePathList
from rdetoolkit.models.rde2types import InputFilesGroup as InputFilesGroup
from rdetoolkit.models.rde2types import OtherFilesPathList as OtherFilesPathList
from rdetoolkit.models.rde2types import RawFiles as RawFiles
from rdetoolkit.models.rde2types import ZipFilesPathList as ZipFilesPathList

class InvoiceChecke(IInputFileChecker):
    out_dir_temp: Incomplete
    def __init__(self, unpacked_dir_basename: Path) -> None: ...
    def parse(self, src_dir_input: Path) -> tuple[RawFiles, Optional[Path]]: ...

class ExcelInvoiceChecker(IInputFileChecker):
    out_dir_temp: Incomplete
    def __init__(self, unpacked_dir_basename: Path) -> None: ...
    def parse(self, src_dir_input: Path) -> tuple[RawFiles, Optional[Path]]: ...
    def get_index(self, paths, sort_items): ...

class RDEFormatChecker(IInputFileChecker):
    out_dir_temp: Incomplete
    def __init__(self, unpacked_dir_basename: Path) -> None: ...
    def parse(self, src_dir_input: Path) -> tuple[RawFiles, Optional[Path]]: ...

class MultiFileChecker(IInputFileChecker):
    out_dir_temp: Incomplete
    def __init__(self, unpacked_dir_basename: Path) -> None: ...
    def parse(self, src_dir_input: Path) -> tuple[RawFiles, Optional[Path]]: ...
