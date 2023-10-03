import logging
import os
import pathlib
import shutil

import pytest
from src.rdetoolkit.rdelogger import get_logger


def test_get_logger_without_filepath(tmpdir):
    """テストケース: StreamHandlerのログテスト"""
    name = "test_logger"
    logger = get_logger(name)
    assert logger.name == name
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)


def test_get_logger_with_filepath():
    """FileStreamHandlerとStreamHandlerのロギングが正しく動作するかテスト"""
    name = "test_logger_with_file"
    test_dir = os.path.join(os.getcwd(), "tests", "logs")
    filepath = os.path.join(test_dir, "test.log")
    logger = get_logger(name, file_path=filepath)
    assert logger.name == name
    assert len(logger.handlers) == 2
    assert isinstance(logger.handlers[0], logging.StreamHandler)
    assert isinstance(logger.handlers[1], logging.FileHandler)
    assert pathlib.Path(logger.handlers[1].baseFilename) == pathlib.Path(filepath)

    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
