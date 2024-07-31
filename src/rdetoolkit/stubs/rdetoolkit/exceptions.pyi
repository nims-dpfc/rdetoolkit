import traceback
from _typeshed import Incomplete
from typing import Any, Callable

class StructuredError(Exception):
    emsg: Incomplete
    ecode: Incomplete
    eobj: Incomplete
    traceback_info: Incomplete
    def __init__(self, emsg: str = ..., ecode: int = ..., eobj: Any | None = ..., traceback_info: str | None = ...) -> None: ...

class InvoiceSchemaValidationError(Exception):
    message: Incomplete
    def __init__(self, message: str = ...) -> None: ...

class MetadataValidationError(Exception):
    message: Incomplete
    def __init__(self, message: str = ...) -> None: ...

def format_simplified_traceback(tb_list: list[traceback.FrameSummary]) -> str: ...
def handle_exception(e: Exception, error_message: str | None = ..., error_code: int | None = ..., eobj: Any | None = ..., verbose: bool = ...) -> StructuredError: ...
def catch_exception_with_message(*, error_message: str | None = ..., error_code: int | None = ..., eobj: Any | None = ..., verbose: bool = ...) -> Callable: ...
