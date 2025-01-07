from _typeshed import Incomplete
from typing import Any

class StructuredError(Exception):
    emsg: Incomplete
    ecode: Incomplete
    eobj: Incomplete
    traceback_info: Incomplete
    def __init__(self, emsg: str = '', ecode: int = 1, eobj: Any | None = None, traceback_info: str | None = None) -> None: ...

class InvoiceModeError(Exception):
    emsg: Incomplete
    ecode: Incomplete
    eobj: Incomplete
    traceback_info: Incomplete
    def __init__(self, emsg: str = '', ecode: int = 100, eobj: Any | None = None, traceback_info: str | None = None) -> None: ...

class ExcelInvoiceModeError(Exception):
    emsg: Incomplete
    ecode: Incomplete
    eobj: Incomplete
    traceback_info: Incomplete
    def __init__(self, emsg: str = '', ecode: int = 101, eobj: Any | None = None, traceback_info: str | None = None) -> None: ...

class MultiDataTileModeError(Exception):
    emsg: Incomplete
    ecode: Incomplete
    eobj: Incomplete
    traceback_info: Incomplete
    def __init__(self, emsg: str = '', ecode: int = 102, eobj: Any | None = None, traceback_info: str | None = None) -> None: ...

class RdeFormatModeError(Exception):
    emsg: Incomplete
    ecode: Incomplete
    eobj: Incomplete
    traceback_info: Incomplete
    def __init__(self, emsg: str = '', ecode: int = 103, eobj: Any | None = None, traceback_info: str | None = None) -> None: ...

class InvoiceSchemaValidationError(Exception):
    message: Incomplete
    def __init__(self, message: str = 'Validation error') -> None: ...

class MetadataValidationError(Exception):
    message: Incomplete
    def __init__(self, message: str = 'Validation error') -> None: ...
