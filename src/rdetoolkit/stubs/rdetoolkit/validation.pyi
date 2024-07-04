from _typeshed import Incomplete
from pathlib import Path
from rdetoolkit.exceptions import InvoiceSchemaValidationError as InvoiceSchemaValidationError, MetadataValidationError as MetadataValidationError
from rdetoolkit.models.invoice_schema import InvoiceSchemaJson as InvoiceSchemaJson
from rdetoolkit.models.metadata import MetadataItem as MetadataItem
from rdetoolkit.rde2util import read_from_json_file as read_from_json_file
from typing import Any

class MetadataValidator:
    schema: Incomplete
    def __init__(self) -> None: ...
    def validate(self, *, path: str | Path | None = ..., json_obj: dict[str, Any] | None = ...) -> dict[str, Any]: ...

def metadata_validate(path: str | Path) -> None: ...

class InvoiceValidator:
    pre_basic_info_schema: Incomplete
    schema_path: Incomplete
    schema: Incomplete
    def __init__(self, schema_path: str | Path) -> None: ...
    def validate(self, *, path: str | Path | None = ..., obj: dict[str, Any] | None = ...) -> dict[str, Any]: ...

def invoice_validate(path: str | Path, schema: str | Path) -> None: ...
