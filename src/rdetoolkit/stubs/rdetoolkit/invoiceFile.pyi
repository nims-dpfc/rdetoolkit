from pathlib import Path
from typing import Any, Optional, Union

import pandas as pd
from _typeshed import Incomplete
from rdetoolkit import rde2util as rde2util
from rdetoolkit.exceptions import StructuredError as StructuredError
from rdetoolkit.models.rde2types import RdeFormatFlags as RdeFormatFlags
from rdetoolkit.models.rde2types import RdeOutputResourcePath as RdeOutputResourcePath
from rdetoolkit.rde2util import StorageDir as StorageDir

def readExcelInvoice(excelInvoiceFilePath): ...
def checkExistRawFiles(dfExcelInvoice: pd.DataFrame, excelRawFiles: list[Path]) -> list[Path]: ...
def overwriteInvoiceFileforDPFTerm(invoiceObj, invoiceDstFilePath, invoiceSchemaFilePath, invoiceInfo) -> None: ...
def checkExistRawFiles_for_folder(dfExcelInvoice, rawFilesTpl): ...

class InvoiceFile:
    invoice_path: Incomplete
    invoice_obj: Incomplete
    def __init__(self, invoice_path: Path) -> None: ...
    invoice_json: Incomplete
    def read(self, *, target_path: Optional[Path] = ...) -> dict: ...
    def overwrite(self, dist_file_path: Path, *, src_file_path: Optional[Path] = ...): ...

class ExcelInvoiceFile:
    invoice_path: Incomplete
    def __init__(self, invoice_path: Path) -> None: ...
    def read(self, *, target_path: Optional[Path] = ...) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: ...
    def overwrite(self, invoice_org: Path, dist_path: Path, invoice_schema_path: Path, idx: int) -> None: ...

def backup_invoice_json_files(excel_invoice_file: Optional[Path], fmt_flags: RdeFormatFlags) -> Path: ...
def update_description_with_features(rde_resource: RdeOutputResourcePath, dst_invoice_json: Path, metadata_def_json: Path): ...

class RuleBasedReplacer:
    rules: Incomplete
    last_apply_result: Incomplete
    def __init__(self, *, rule_file_path: Optional[Union[str, Path]] = ...) -> None: ...
    def load_rules(self, filepath: Union[str, Path]) -> None: ...
    def get_apply_rules_obj(self, replacements: dict[str, Any], source_json_obj: Optional[dict[str, Any]], *, mapping_rules: Optional[dict[str, str]] = ...) -> dict[str, Any]: ...
    def set_rule(self, path: str, variable: str) -> None: ...
    def write_rule(self, replacements_rule: dict[str, Any], save_file_path: Union[str, Path]) -> str: ...

def apply_default_filename_mapping_rule(replacement_rule: dict[str, Any], save_file_path: Union[str, Path]) -> dict[str, Any]: ...
