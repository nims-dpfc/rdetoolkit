from pathlib import Path
from typing import Optional, TypedDict, Union

ZipFilesPathList = list[Path]
unZipFilesPathList = list[Path]
ExcelInvoicePathList = list[Path]
OtherFilesPathList = list[Path]
PathTuple = tuple[Path, ...]
InputFilesGroup = tuple[ZipFilesPathList, ExcelInvoicePathList, OtherFilesPathList]
RawFiles = list[PathTuple]
MetaType = dict[str, Union[str, int, float, list]]
RepeatedMetaType = dict[str, list[Union[str, int, float]]]
MetaItem = dict[str, Union[str, int, float, bool]]
RdeFsPath = Union[str, Path]

class RdeFormatFlags:
    def __post_init__(self) -> None: ...
    @property
    def is_rdeformat_enabled(self): ...
    @property
    def is_multifile_enabled(self): ...
    def __init__(self, _is_rdeformat_enabled, _is_multifile_enabled) -> None: ...

class RdeInputDirPaths:
    inputdata: Path
    invoice: Path
    tasksupport: Path
    @property
    def default_csv(self) -> Path: ...
    def __init__(self, inputdata, invoice, tasksupport) -> None: ...

class RdeOutputResourcePath:
    raw: Path
    rawfiles: tuple[Path, ...]
    struct: Path
    main_image: Path
    other_image: Path
    meta: Path
    thumbnail: Path
    logs: Path
    invoice: Path
    invoice_schema_json: Path
    invoice_org: Path
    temp: Optional[Path]
    invoice_patch: Optional[Path]
    attachment: Optional[Path]
    nonshared_raw: Optional[Path]
    def __init__(self, raw, rawfiles, struct, main_image, other_image, meta, thumbnail, logs, invoice, invoice_schema_json, invoice_org, temp, invoice_patch, attachment, nonshared_raw) -> None: ...

class Name(TypedDict):
    ja: str
    en: str

class Schema(TypedDict, total=False):
    type: str
    format: str

class MetadataDefJson(TypedDict):
    name: Name
    schema: Schema
    unit: str
    description: str
    uri: str
    originalName: str
    originalType: str
    mode: str
    order: str
    valiable: int
    action: str

class ValueUnitPair:
    value: str
    unit: str
    def __init__(self, value, unit) -> None: ...
