import pathlib
from _typeshed import Incomplete
from rdetoolkit.exceptions import StructuredError as StructuredError, catch_exception_with_message as catch_exception_with_message
from rdetoolkit.models.rde2types import MetaItem as MetaItem, MetaType as MetaType, MetadataDefJson as MetadataDefJson, RdeFsPath as RdeFsPath, RepeatedMetaType as RepeatedMetaType, ValueUnitPair as ValueUnitPair
from typing import Any, Optional, TypedDict, Union

class _ChardetType(TypedDict):
    encoding: str
    language: str
    confidence: float

def get_default_values(defaultValsFilePath): ...

class CharDecEncoding:
    USUAL_ENCs: Incomplete
    @classmethod
    def detect_text_file_encoding(cls, text_filepath: RdeFsPath) -> str: ...

def unzip_japanese_zip(src_zipfilepath: str, dst_dirpath: str) -> None: ...
def read_from_json_file(invoice_file_path: RdeFsPath) -> dict[str, Any]: ...
def write_to_json_file(invoicefile_path: RdeFsPath, invoiceObj: dict[str, Any], enc: str = ...): ...

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
