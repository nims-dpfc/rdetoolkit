import logging
from _typeshed import Incomplete as Incomplete
from logging import Logger
from rdetoolkit.models.rde2types import RdeFsPath as RdeFsPath
from typing import Callable

class LazyFileHandler(logging.Handler):
    filename: Incomplete
    mode: Incomplete
    encoding: Incomplete
    def __init__(self, filename: str, mode: str = 'a', encoding: str = 'utf-8') -> None: ...
    def emit(self, record: logging.LogRecord) -> None: ...

def get_logger(name: str, *, file_path: RdeFsPath | None = None) -> logging.Logger: ...

class CustomLog:
    logger: Incomplete
    def __init__(self, name: str = 'rdeuser') -> None: ...
    def get_logger(self, needlogs: bool = True) -> Logger: ...

def log_decorator() -> Callable: ...
