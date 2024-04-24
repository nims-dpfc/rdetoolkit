from _typeshed import Incomplete as Incomplete
from typing import Optional

class StructuredError(Exception):
    eMsg: Incomplete
    eCode: Incomplete
    eObj: Incomplete
    def __init__(self, eMsg: str = ..., eCode: int = ..., eObj: Incomplete | None = ...) -> None: ...

class InvoiceSchemaValidationError(Exception):
    message: Incomplete
    def __init__(self, message: str = ...) -> None: ...

class MetadataDefValidationError(Exception):
    message: Incomplete
    def __init__(self, message: str = ...) -> None: ...

def catch_exception_with_message(*, error_message: Optional[str] = ..., error_code: Optional[int] = ...): ...
