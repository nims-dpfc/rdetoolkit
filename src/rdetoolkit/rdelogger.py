import logging
import os
from logging import DEBUG, INFO, FileHandler, Formatter, Logger, NullHandler, StreamHandler, getLogger
from typing import Optional

from rdetoolkit.rde2util import StorageDir


def get_logger(name: str, *, file_path: Optional[str] = None) -> logging.Logger:
    """Creates a logger using Python's logging module.

    The logger is a tool for generating log messages, tracking processes, and facilitating debugging.

    Args:
        name (str): The identifier's name, usually the module name is specified (__name__).
        file_path (Optional[str], optional): The path of the log file. If this parameter is
        specified, the log messages will be written to this file. If not specified,
        the log messages will be sent to the standard output. Defaults to None.

    Returns:
        logging.Logger: A configured logger object.

    Example:
        from rdetoolkit import rdelogger

        logger = rdelogger.get_logger(__name__, "data/log/rdesys.log")

        # If you want to output a debug message, add the following code
        logger.debug('This is a debug message.')
        >>> 2023-01-01 00:00:00,111 - [rdetoolkit.rde2util](DEBUG) - This is a debug message.
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
    """Write the error log to a file.

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


class CustomLog:
    """The CustomLog class is a class for writing custom logs to a user's log file.

    To create an instance of this class, call `CustomLog` with the module name as an argument.
    Then, by calling the `get_log` method, you can get a logger for writing logs.

    Returns:
        logger: A logger instance for writing logs. If `False` is passed to `get_log`, the logger will not write any logs.

    Example:
    ```python
    logger = CustomLog(__name__).get_log()

    # If you do not want to write a log, pass `False` as an argument to the `get_log` method.
    logger = CustomLog(__name__).get_log(False)

    #In the above code, a logger is generated, but no log is written.
    ```
    """

    def __init__(self, name: str = "rdeuser"):
        logger = getLogger(name)
        logger.propagate = False
        logger.setLevel(DEBUG)

        self.logger = logger

    def get_logger(self, needLogs: bool = True) -> Logger:
        """Retrieves the logger instance.

        Args:
            needLogs (bool, optional): Indicates whether logs are needed. Defaults to True.

        Returns:
            Logger: The logger instance.

        """
        logger = self.logger
        if not logger.hasHandlers():
            logDir = StorageDir.get_specific_outputdir(True, "logs")
            logFile = logDir / "rdeuser.log"
            if needLogs:
                self._set_handler(StreamHandler(), True)
                self._set_handler(FileHandler(logFile), True)
            else:
                self._set_handler(NullHandler(), False)
        self.logger = logger

        return self.logger

    def _set_handler(self, handler, verbose: bool):
        level = DEBUG if verbose else INFO
        handler.setLevel(level)
        formatter = Formatter(
            # fmt="%(asctime)s - [%(name)s](%(levelname)s)" +
            #       "%(funcName)-15s %(message)s",
            fmt="%(asctime)s (%(levelname)s) %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S %z",
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)


def log_decorator():
    """A decorator function that logs the start and end of a decorated function.

    Returns:
        function: The decorated function.

    Example:
        ```python
        @log_decorator()
        def my_function():
            print("Hello, World!")

        my_function()
        # Output:
        # my_function     --> Start
        # Hello, World!
        # my_function     <-- End
        ```
    """

    def _log_decorator(func):
        def wrapper(*args, **kargs):
            logger = CustomLog().get_logger()
            logger.info(f"{func.__name__:15} --> Start")
            try:
                return func(*args, **kargs)
            except Exception as e:
                logger.error(f"{func.__name__:15} !!! Error has occurred")
                raise e
            finally:
                logger.info(f"{func.__name__:15} <-- End")

        return wrapper

    return _log_decorator
