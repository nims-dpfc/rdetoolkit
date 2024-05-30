from __future__ import annotations

from functools import wraps
from typing import Any, Callable


class StructuredError(Exception):
    """A custom exception class providing structured error information.

    This class extends the standard Exception class to include additional information
    such as an error message, an error code, and an error object. This allows for a
    more detailed representation of errors.

    Args:
        emsg (str): The error message.
        ecode (int): The error code. Defaults to 1.
        eobj (any): An additional error object. This can be an object of any type to
                    provide more context to the error.
    """

    def __init__(self, emsg: str = "", ecode: int = 1, eobj: Any | None = None):
        super().__init__(emsg)
        self.emsg = emsg
        self.ecode = ecode
        self.eobj = eobj


class InvoiceSchemaValidationError(Exception):
    """Raised when a validation error occurs."""

    def __init__(self, message: str = "Validation error") -> None:
        self.message = message
        super().__init__(self.message)


class MetadataDefValidationError(Exception):
    """Raised when a validation error occurs."""

    def __init__(self, message: str = "Validation error") -> None:
        self.message = message
        super().__init__(self.message)


def catch_exception_with_message(*, error_message: str | None = None, error_code: int | None = None) -> Callable:
    """A decorator that catches exceptions and re-raises a StructuredError with a customized message and error code.

    This decorator catches StructuredError thrown within the function and re-raises it with a specified error message
    and error code. If a StructuredError is not raised, it still re-raises other exceptions as a standard Exception.

    Args:
        error_message (Optional[str]): Customized message to be used in case of an error.
        error_code (Optional[int]): Error code to be used in case of an error. Defaults to None.

    Returns:
        A function decorator that provides customized error handling on exception occurrence.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> None:
            try:
                return func(*args, **kwargs)
            except StructuredError as e:
                msg = error_message if error_message is not None else str(e)
                ecode = error_code if error_code is not None else 1
                raise StructuredError(msg, ecode=ecode, eobj=e) from e
            except Exception as e:
                msg = error_message if error_message is not None else str(e)
                raise Exception(msg) from e

        return wrapper

    return decorator
