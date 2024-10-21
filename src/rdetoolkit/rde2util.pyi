import pathlib
from _typeshed import Incomplete
from rdetoolkit.errors import catch_exception_with_message as catch_exception_with_message
from rdetoolkit.exceptions import StructuredError as StructuredError
from rdetoolkit.models.rde2types import MetaItem as MetaItem, MetaType as MetaType, MetadataDefJson as MetadataDefJson, RdeFsPath as RdeFsPath, RepeatedMetaType as RepeatedMetaType, ValueUnitPair as ValueUnitPair
from typing import Any, Callable, Final, TypedDict

LANG_ENC_FLAG: Final[int]

class _ChardetType(TypedDict):
    encoding: str
    language: str
    confidence: float

def get_default_values(default_values_filepath: RdeFsPath) -> dict[str, Any]: ...

class CharDecEncoding:
    USUAL_ENCs: Incomplete
    @classmethod
    def detect_text_file_encoding(cls, text_filepath: RdeFsPath) -> str: ...

def unzip_japanese_zip(src_zipfilepath: str, dst_dirpath: str) -> None: ...
def read_from_json_file(invoice_file_path: RdeFsPath) -> dict[str, Any]: ...
def write_to_json_file(invoicefile_path: RdeFsPath, invoiceobj: dict[str, Any], enc: str = 'utf_8') -> None: ...

class StorageDir:
    @classmethod
    def get_datadir(cls, is_mkdir: bool, idx: int = 0) -> str: ...
    @classmethod
    def get_specific_outputdir(cls, is_mkdir: bool, dir_basename: str, idx: int = 0) -> pathlib.Path: ...

class Meta:
    metaConst: Incomplete
    metaVar: Incomplete
    actions: Incomplete
    referedmap: Incomplete
    metaDef: Incomplete
    def __init__(self, metadef_filepath: RdeFsPath, *, metafilepath: RdeFsPath | None = None) -> None: ...
    def assign_vals(self, entry_dict_meta: MetaType | RepeatedMetaType, *, ignore_empty_strvalue: bool = True) -> dict[str, set]: ...
    def writefile(self, meta_filepath: str, enc: str = 'utf_8') -> dict[str, Any]: ...

class ValueCaster:
    @staticmethod
    def trycast(valstr: str, tp: Callable[[str], Any]) -> Any: ...
    @staticmethod
    def convert_to_date_format(value: str, fmt: str) -> str: ...

def castval(valstr: Any, outtype: str | None, outfmt: str | None) -> bool | int | float | str: ...
def dict2meta(metadef_filepath: pathlib.Path, metaout_filepath: pathlib.Path, const_info: MetaType, val_info: MetaType) -> dict[str, set[Any]]: ...
