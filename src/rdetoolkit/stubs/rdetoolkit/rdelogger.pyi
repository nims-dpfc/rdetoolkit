import logging
from typing import Optional

from rdetoolkit.rde2util import StorageDir as StorageDir

def get_logger(name: str, *, file_path: Optional[str] = ...) -> logging.Logger: ...
def write_job_errorlog_file(code: int, message: str, *, filename: str = ...) -> None: ...
