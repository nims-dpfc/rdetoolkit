import logging
import traceback
from collections.abc import Generator
from rdetoolkit.exceptions import StructuredError as StructuredError
from typing import Any, Callable

def catch_exception_with_message(*, error_message: str | None = None, error_code: int | None = None, eobj: Any | None = None, verbose: bool = False) -> Callable: ...
def skip_exception_context(exception_type: type[Exception], logger: logging.Logger | None = None, enabled: bool = False) -> Generator[dict[str, str | None], None, None]: ...
def format_simplified_traceback(tb_list: list[traceback.FrameSummary]) -> str: ...
def handle_exception(e: Exception, error_message: str | None = None, error_code: int | None = None, eobj: Any | None = None, verbose: bool = False) -> StructuredError: ...
def handle_and_exit_on_structured_error(e: StructuredError, logger: logging.Logger) -> None: ...
def handle_generic_error(e: Exception, logger: logging.Logger) -> None: ...
def write_job_errorlog_file(code: int, message: str, *, filename: str = 'job.failed') -> None: ...
