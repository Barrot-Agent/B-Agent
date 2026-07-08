"""
Tests for barrot_agent.logger module.
"""

import logging
import os
import tempfile

from barrot_agent.logger import JSONFormatter, get_logger, setup_logging


class TestJSONFormatter:
    def test_format_basic(self) -> None:
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="hello world",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)
        import json
        data = json.loads(output)
        assert data["message"] == "hello world"
        assert data["level"] == "INFO"
        assert data["logger"] == "test"

    def test_format_with_exception(self) -> None:
        formatter = JSONFormatter()
        try:
            raise ValueError("test error")
        except ValueError:
            import sys
            exc_info = sys.exc_info()
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=1,
                msg="error occurred",
                args=(),
                exc_info=exc_info,
            )
            output = formatter.format(record)
            import json
            data = json.loads(output)
            assert "exception" in data


class TestGetLogger:
    def test_returns_logger(self) -> None:
        logger = get_logger("test.module")
        assert isinstance(logger, logging.Logger)

    def test_logger_name(self) -> None:
        logger = get_logger("barrot_agent.test")
        assert logger.name == "barrot_agent.test"

    def test_debug_level(self) -> None:
        logger = get_logger("test.debug_level", level="DEBUG")
        assert logger.level == logging.DEBUG

    def test_json_format(self) -> None:
        logger = get_logger("test.json", json_format=True)
        assert logger is not None

    def test_file_handler(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            logger = get_logger("test.file_handler_unique", log_file=log_file)
            logger.info("test message")
            assert os.path.exists(log_file)

    def test_idempotent_on_second_call(self) -> None:
        logger1 = get_logger("test.idempotent_abc")
        handler_count = len(logger1.handlers)
        logger2 = get_logger("test.idempotent_abc")
        assert len(logger2.handlers) == handler_count


class TestSetupLogging:
    def test_setup_basic(self) -> None:
        setup_logging(level="WARNING")
        root = logging.getLogger()
        assert root.level == logging.WARNING

    def test_setup_json(self) -> None:
        setup_logging(level="INFO", json_format=True)
        root = logging.getLogger()
        assert root.level == logging.INFO

    def test_setup_with_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "app.log")
            setup_logging(level="DEBUG", log_file=log_file)
            logging.info("test entry")
            assert os.path.exists(log_file)
