from _typeshed import Incomplete
from typing import Any, Callable

class StructuredError(Exception):
    emsg: Incomplete
    ecode: Incomplete
    eobj: Incomplete
    def __init__(self, emsg: str = ..., ecode: int = ..., eobj: Any | None = ...) -> None: ...

class InvoiceSchemaValidationError(Exception):
    message: Incomplete
    def __init__(self, message: str = ...) -> None: ...

class MetadataValidationError(Exception):
    message: Incomplete
    def __init__(self, message: str = ...) -> None: ...

def catch_exception_with_message(*, error_message: str | None = ..., error_code: int | None = ...) -> Callable: ...
