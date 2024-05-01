import pandas as pd
from _typeshed import Incomplete
from pathlib import Path
from rdetoolkit.exceptions import StructuredError as StructuredError
from rdetoolkit.interfaces.filechecker import ICompressedFileStructParser as ICompressedFileStructParser
from rdetoolkit.invoicefile import checkExistRawFiles as checkExistRawFiles
from typing import List, Tuple, Union

class CompressedFlatFileParser(ICompressedFileStructParser):
    xlsx_invoice: Incomplete
    def __init__(self, xlsx_invoice: pd.DataFrame) -> None: ...
    def read(self, zipfile: Path, target_path: Path) -> List[Tuple[Path, ...]]: ...

class CompressedFolderParser(ICompressedFileStructParser):
    xlsx_invoice: Incomplete
    def __init__(self, xlsx_invoice: pd.DataFrame) -> None: ...
    def read(self, zipfile: Path, target_path: Path) -> List[Tuple[Path, ...]]: ...
    def validation_uniq_fspath(self, target_path: Union[str, Path], exclude_names: list[str]) -> dict[str, list[Path]]: ...

def parse_compressedfile_mode(xlsx_invoice: pd.DataFrame) -> ICompressedFileStructParser: ...
