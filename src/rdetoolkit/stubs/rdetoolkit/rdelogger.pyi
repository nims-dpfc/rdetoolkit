import logging
from _typeshed import Incomplete
from logging import Logger
from rdetoolkit.rde2util import StorageDir as StorageDir
from typing import Optional

pp: Incomplete

def get_logger(name: str, *, file_path: Optional[str] = ...) -> logging.Logger: ...
def write_job_errorlog_file(code: int, message: str, *, filename: str = ...) -> None: ...

class CustomLog:
    logger: Incomplete
    def __init__(self, name: str = ...) -> None: ...
    def get_logger(self, needlogs: bool = ...) -> Logger: ...

def log_decorator(): ...