from __future__ import annotations

import logging
import os
from logging import DEBUG, INFO, FileHandler, Formatter, Handler, Logger, NullHandler, StreamHandler, getLogger
from pathlib import Path
from typing import Callable

from rdetoolkit.models.rde2types import RdeFsPath


class LazyFileHandler(logging.Handler):
    """A logging handler that lazily creates the actual FileHandler when needed.

    This handler delays the creation of the log file until the first log message is emitted.
    This helps prevent unnecessary file creation when logging is configured but not used.

    Args:
        filename: The path to the log file.
        mode: The file opening mode. Defaults to 'a' (append).
        encoding: The encoding to use for the file. Defaults to None.

    Attributes:
        filename: The path where the log file will be created.
        mode: The file opening mode.
        encoding: The file encoding.
        _handler: The underlying FileHandler instance, created on first use.
    """

    def __init__(self, filename: str, mode: str = "a", encoding: str = 'utf-8') -> None:
        super().__init__()
        self.filename = filename
        self.mode = mode
        self.encoding = encoding
        self._handler: logging.FileHandler | None = None

    def _ensure_handler(self) -> None:
        """Creates the actual FileHandler if it hasn't been created yet.

        This method handles the lazy initialization of the FileHandler,
        creating necessary directories and configuring the handler with
        the formatter and level settings from the parent handler.
        """
        if self._handler is None:
            if not os.path.exists(os.path.dirname(self.filename)):
                os.makedirs(os.path.dirname(self.filename), exist_ok=True)
            self._handler = logging.FileHandler(self.filename, mode=self.mode, encoding=self.encoding)
            self._handler.setFormatter(self.formatter)
            self._handler.setLevel(self.level)

    def emit(self, record: logging.LogRecord) -> None:
        """Lazily creates the actual FileHandler and delegates the emission of the log record.

        Args:
            record: The LogRecord instance containing all the information of the logging event.
        """
        self._ensure_handler()
        if self._handler is not None:
            self._handler.emit(record)


def get_logger(name: str, *, file_path: RdeFsPath | None = None, level: int = logging.DEBUG) -> logging.Logger:
    """Creates and configures a logger using Python's built-in logging module.

    This function creates a logger identified by `name`, sets its logging level, and, if a file
    path is provided, adds a lazy file handler to output log messages to that file. The default
    logging level is DEBUG, but it can be modified via the `level` parameter.

    Args:
        name (str): The name of the logger (typically the module name, e.g. __name__).
        file_path (Optional[RdeFsPath], optional): The file path where log messages will be written.
            If not provided, log output will be directed to the standard output. Defaults to None.
        level (int, optional): The logging level to set for the logger and its handlers, such as
            logging.DEBUG or logging.INFO. Defaults to logging.DEBUG.

    Returns:
        logging.Logger: A configured logger instance.

    Example:
        ```python
        from rdetoolkit import rdelogger
        import logging

        # Create a logger with the default DEBUG level.
        logger = rdelogger.get_logger(__name__, "data/logs/rdesys.log")
        logger.debug('This is a debug message.')

        # Create a logger with a custom logging level (INFO).
        logger_info = rdelogger.get_logger(__name__, "data/logs/rdesys.log", level=logging.INFO)
        logger_info.info('This is an info message.')
        ```
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter("%(asctime)s - [%(name)s](%(levelname)s) - %(message)s")

    if file_path is None:
        return logger

    file_handler = LazyFileHandler(str(file_path))
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


class CustomLog:
    """The CustomLog class is a class for writing custom logs to a user's log file.

    To create an instance of this class, call `CustomLog` with the module name as an argument.
    Then, by calling the `get_log` method, you can get a logger for writing logs.

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

    def get_logger(self, needlogs: bool = True) -> Logger:
        """Retrieves the logger instance.

        Args:
            needlogs (bool, optional): Indicates whether logs are needed. Defaults to True.

        Returns:
            Logger: The logger instance.

        """
        logger = self.logger
        if not logger.hasHandlers():
            logdir = Path("data/logs")
            logdir.mkdir(parents=True, exist_ok=True)
            logfile = logdir / "rdeuser.log"
            if needlogs:
                self._set_handler(StreamHandler(), True)
                self._set_handler(FileHandler(logfile), True)
            else:
                self._set_handler(NullHandler(), False)
        self.logger = logger

        return self.logger

    def _set_handler(self, handler: Handler, verbose: bool) -> None:
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


def log_decorator() -> Callable:
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

    def _log_decorator(func: Callable) -> Callable:
        def wrapper(*args, **kargs) -> Callable:
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
