import logging
from _typeshed import Incomplete
from logging import Logger
from rdetoolkit.models.rde2types import RdeFsPath as RdeFsPath
from rdetoolkit.rde2util import StorageDir as StorageDir
from typing import Callable

def get_logger(name: str, *, file_path: RdeFsPath | None = None) -> logging.Logger: ...

class CustomLog:
    logger: Incomplete
    def __init__(self, name: str = 'rdeuser') -> None: ...
    def get_logger(self, needlogs: bool = True) -> Logger: ...

def log_decorator() -> Callable: ...
