import logging
import logging.handlers
import os
import pathlib
import shutil
from unittest import mock

from rdetoolkit.rdelogger import get_logger, CustomLog, log_decorator


def test_custom_log():
    custom_log = CustomLog('test')

    logger = custom_log.get_logger()

    # # Confirm that the logger was correctly obtained
    assert logger is not None
    # Confirm that the logger name is correct
    assert logger.name == 'test'
    # Confirm that the logger has a handler
    assert len(logger.handlers) > 0


def test_log_decorator(caplog):
    logger_mock = mock.Mock(spec=CustomLog)
    logger_mock.get_logger.return_value = mock.Mock()

    # ロガーのモックをパッチ
    with mock.patch('rdetoolkit.rdelogger.CustomLog', return_value=logger_mock):
        @log_decorator()
        def test_func():
            return "Hello, World!"

        result = test_func()

        assert result == "Hello, World!"

        # ロガーが正しく呼び出されたことを確認
        calls = [
            mock.call.info('test_func       --> Start'),
            mock.call.info('test_func       <-- End')
        ]
        logger_mock.get_logger.return_value.assert_has_calls(calls)


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
