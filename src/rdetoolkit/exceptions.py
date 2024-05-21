from functools import wraps
from typing import Optional


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

    def __init__(self, emsg: str = "", ecode=1, eobj=None):
        super().__init__(emsg)
        self.emsg = emsg
        self.ecode = ecode
        self.eobj = eobj


class InvoiceSchemaValidationError(Exception):
    """Raised when a validation error occurs."""

    def __init__(self, message="Validation error"):
        self.message = message
        super().__init__(self.message)


class MetadataDefValidationError(Exception):
    """Raised when a validation error occurs."""

    def __init__(self, message="Validation error"):
        self.message = message
        super().__init__(self.message)


def catch_exception_with_message(*, error_message: Optional[str] = None, error_code: Optional[int] = None):
    """A decorator that catches exceptions and re-raises a StructuredError with a customized message and error code.

    This decorator catches StructuredError thrown within the function and re-raises it with a specified error message
    and error code. If a StructuredError is not raised, it still re-raises other exceptions as a standard Exception.

    Args:
        error_message (Optional[str]): Customized message to be used in case of an error.
        error_code (Optional[int]): Error code to be used in case of an error. Defaults to None.

    Returns:
        A function decorator that provides customized error handling on exception occurrence.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except StructuredError as e:
                if error_message is not None:
                    msg = error_message
                else:
                    msg = str(e)

                if error_code is not None:
                    ecode = error_code
                else:
                    ecode = 1

                raise StructuredError(msg, ecode=ecode, eobj=e)

            except Exception as e:
                if error_message is not None:
                    msg = error_message
                else:
                    msg = str(e)
                raise Exception(msg)

        return wrapper

    return decorator
