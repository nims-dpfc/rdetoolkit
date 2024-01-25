import pathlib
from typing import Any, Optional, TypedDict, Union

from _typeshed import Incomplete
from rdetoolkit.exceptions import StructuredError as StructuredError
from rdetoolkit.exceptions import catch_exception_with_message as catch_exception_with_message
from rdetoolkit.models.rde2types import MetadataDefJson as MetadataDefJson
from rdetoolkit.models.rde2types import MetaItem as MetaItem
from rdetoolkit.models.rde2types import MetaType as MetaType
from rdetoolkit.models.rde2types import RdeFsPath as RdeFsPath
from rdetoolkit.models.rde2types import RepeatedMetaType as RepeatedMetaType
from rdetoolkit.models.rde2types import ValueUnitPair as ValueUnitPair

class _ChardetType(TypedDict):
    encoding: str
    language: str
    confidence: float

def get_default_values(defaultValsFilePath): ...
def detect_text_file_encoding(text_filepath: RdeFsPath) -> str: ...
def unzip_japanese_zip(src_zipfilepath: str, dst_dirpath: str) -> None: ...
def read_from_json_file(invoice_file_path: RdeFsPath) -> dict[str, Any]: ...
def write_to_json_file(invoiceFilePath: RdeFsPath, invoiceObj: dict[str, Any], enc: str = ...): ...

class StorageDir:
    @classmethod
    def get_datadir(cls, is_mkdir: bool, idx: int = ...): ...
    @classmethod
    def get_specific_outputdir(cls, is_mkdir: bool, dir_basename: str, idx: int = ...): ...

class Meta:
    metaConst: Incomplete
    metaVar: Incomplete
    actions: Incomplete
    referedmap: Incomplete
    metaDef: Incomplete
    def __init__(self, metadef_filepath: RdeFsPath, *, metafilepath: Optional[RdeFsPath] = ...) -> None: ...
    def assignVals(self, entry_dict_meta: Union[MetaType, RepeatedMetaType], *, ignoreEmptyStrValue: bool = ...) -> dict[str, set]: ...
    def writeFile(self, metaFilePath, enc: str = ...): ...

def castVal(valStr: str, outType: Optional[str], outFmt: Optional[str]) -> Union[bool, int, float, str]: ...
def dict2meta(metadef_filepath: pathlib.Path, metaout_filepath: pathlib.Path, const_info: MetaType, val_info: MetaType) -> dict[str, set[Any]]: ...
