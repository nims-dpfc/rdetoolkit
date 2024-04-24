from _typeshed import Incomplete
from pathlib import Path
from rdetoolkit.exceptions import InvoiceSchemaValidationError as InvoiceSchemaValidationError, MetadataDefValidationError as MetadataDefValidationError
from rdetoolkit.models.invoice_schema import InvoiceSchemaJson as InvoiceSchemaJson
from rdetoolkit.models.metadata import MetadataDefItem as MetadataDefItem
from rdetoolkit.rde2util import read_from_json_file as read_from_json_file
from typing import Any, Optional, Union

class MetadataDefValidator:
    schema: Incomplete
    def __init__(self) -> None: ...
    def validate(self, *, path: Optional[Union[str, Path]] = ..., json_obj: Optional[dict[str, Any]] = ...) -> dict[str, Any]: ...

def metadata_def_validate(path: Union[str, Path]): ...

class InvoiceValidator:
    pre_basic_info_schema: Incomplete
    schema_path: Incomplete
    schema: Incomplete
    def __init__(self, schema_path: Union[str, Path]) -> None: ...
    def validate(self, *, path: Optional[Union[str, Path]] = ..., obj: Optional[dict[str, Any]] = ...) -> dict[str, Any]: ...

def invoice_validate(path: Union[str, Path], schema: Union[str, Path]): ...
