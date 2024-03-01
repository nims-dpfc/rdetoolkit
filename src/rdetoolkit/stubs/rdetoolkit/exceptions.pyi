from typing import Optional

from _typeshed import Incomplete

class StructuredError(Exception):
    eMsg: Incomplete
    eCode: Incomplete
    eObj: Incomplete
    def __init__(self, eMsg: str = ..., eCode: int = ..., eObj: Incomplete | None = ...) -> None: ...

def catch_exception_with_message(*, error_message: Optional[str] = ..., error_code: Optional[int] = ...): ...
