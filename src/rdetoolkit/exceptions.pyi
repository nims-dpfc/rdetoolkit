import traceback
from _typeshed import Incomplete as Incomplete
from typing import Any, Callable

class StructuredError(Exception):
    emsg: Incomplete
    ecode: Incomplete
    eobj: Incomplete
    traceback_info: Incomplete
    def __init__(self, emsg: str = '', ecode: int = 1, eobj: Any | None = None, traceback_info: str | None = None) -> None: ...

class InvoiceSchemaValidationError(Exception):
    message: Incomplete
    def __init__(self, message: str = 'Validation error') -> None: ...

class MetadataValidationError(Exception):
    message: Incomplete
    def __init__(self, message: str = 'Validation error') -> None: ...

def format_simplified_traceback(tb_list: list[traceback.FrameSummary]) -> str: ...
def handle_exception(e: Exception, error_message: str | None = None, error_code: int | None = None, eobj: Any | None = None, verbose: bool = False) -> StructuredError: ...
def catch_exception_with_message(*, error_message: str | None = None, error_code: int | None = None, eobj: Any | None = None, verbose: bool = False) -> Callable: ...
