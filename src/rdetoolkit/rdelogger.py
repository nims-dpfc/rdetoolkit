import logging
import os
from typing import Optional

from src.rdetoolkit.rde2util import StorageDir


def get_logger(name: str, *, file_path: Optional[str] = None) -> logging.Logger:
    """Pythonのloggingモジュールを使用してロガーを作成します。ロガーはログメッセージを生成し、処理を追跡し、デバッグを行うためのツールです。

    Args:
        name (str): Identifier's name. Usually the module name is specified (__name__)
        file_path (Optional[str], optional): Path of the log file. If this parameter is
        specified, the log messages will be written to this file. If not specified,
        the log messages will be sent to the standard output. Defaults to None.

    Returns:
        logging.Logger: Configured logger object

    Exsample:
        from src.rdetoolkit import rdelogger

        logger = rdelogger.get_logger(__name__, data/log/rdesys.log)

        # If you want to output a debug message, add the following code
        logger.debug('This is an debug message.')
        >>> 2023-01-01 00:00:00,111 - [src.rdetoolkit.rde2util](DEBUG) - This is an debug message.
    """

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - [%(name)s](%(levelname)s) - %(message)s")

    # handler = logging.FileHandler(file_path)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if file_path is None:
        return logger

    # add a file handler
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file_handler = logging.FileHandler(file_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def write_job_errorlog_file(code: int, message: str, *, filename: str = "job.failed") -> None:
    """
    Write the error log to a file.

    This function writes the given error code and message to a specified file.
    The file will be saved in a directory determined by `StorageDir.get_datadir(False)`.

    Args:
        code (int): The error code to be written to the log file.
        message (str): The error message to be written to the log file.
        filename (str, optional): The name of the file to which the error log will be written.
            Defaults to "job.failed".

    Example:
        >>> write_job_errorlog_file(404, 'Not Found', filename='error.log')
    """
    with open(
        os.path.join(StorageDir.get_datadir(False), filename),
        "w",
        encoding="utf_8",
    ) as f:
        f.write(f"ErrorCode={code}\n")
        f.write(f"ErrorMessage={message}\n")
