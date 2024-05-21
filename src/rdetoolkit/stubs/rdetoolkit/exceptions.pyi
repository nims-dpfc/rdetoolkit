from _typeshed import Incomplete
from typing import Optional

class StructuredError(Exception):
    emsg: Incomplete
    ecode: Incomplete
    eobj: Incomplete
    def __init__(self, emsg: str = ..., ecode: int = ..., eobj: Incomplete | None = ...) -> None: ...

class InvoiceSchemaValidationError(Exception):
    message: Incomplete
    def __init__(self, message: str = ...) -> None: ...

class MetadataDefValidationError(Exception):
    message: Incomplete
    def __init__(self, message: str = ...) -> None: ...

def catch_exception_with_message(*, error_message: Optional[str] = ..., error_code: Optional[int] = ...): ...
