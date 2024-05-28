import pathlib
from _typeshed import Incomplete as Incomplete
from rdetoolkit.models.rde2types import MetaType as MetaType, RdeFsPath as RdeFsPath, RepeatedMetaType as RepeatedMetaType
from typing import Any, Final, Optional, TypedDict, Union

LANG_ENC_FLAG: Final[int]

class _ChardetType(TypedDict):
    encoding: str
    language: str
    confidence: float

def get_default_values(default_values_filepath) -> None: ...

class CharDecEncoding:
    USUAL_ENCs: Incomplete
    @classmethod
    def detect_text_file_encoding(cls, text_filepath: RdeFsPath) -> str: ...

def unzip_japanese_zip(src_zipfilepath: str, dst_dirpath: str) -> None: ...
def read_from_json_file(invoice_file_path: RdeFsPath) -> dict[str, Any]: ...
def write_to_json_file(invoicefile_path: RdeFsPath, invoiceobj: dict[str, Any], enc: str = ...): ...

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
    def assign_vals(self, entry_dict_meta: Union[MetaType, RepeatedMetaType], *, ignore_empty_strvalue: bool = ...) -> dict[str, set]: ...
    def writefile(self, meta_filepath, enc: str = ...): ...

def castval(valstr: str, outtype: Optional[str], outfmt: Optional[str]) -> Union[bool, int, float, str]: ...
def dict2meta(metadef_filepath: pathlib.Path, metaout_filepath: pathlib.Path, const_info: MetaType, val_info: MetaType) -> dict[str, set[Any]]: ...
