"""Unit tests for structured JSON logging utility."""

import json
import logging

from svearag.core.logging import JSONFormatter, setup_logger


def test_json_formatter_basic():
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test log message",
        args=(),
        exc_info=None,
    )
    formatted = formatter.format(record)
    parsed = json.loads(formatted)

    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "test_logger"
    assert parsed["message"] == "Test log message"
    assert "timestamp" in parsed


def test_json_formatter_with_exception():
    formatter = JSONFormatter()
    try:
        raise ValueError("Simulated failure")
    except ValueError:
        import sys

        exc_info = sys.exc_info()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=25,
            msg="Exception occurred",
            args=(),
            exc_info=exc_info,
        )
        formatted = formatter.format(record)
        parsed = json.loads(formatted)
        assert "exception" in parsed
        assert "Simulated failure" in parsed["exception"]


def test_structured_logger_methods():
    slogger = setup_logger("test_methods")
    # Exercise methods
    slogger.debug("Debug message", extra_data={"k": "v"})
    slogger.info("Info message", key="val")
    slogger.warning("Warn message")
    slogger.error("Error message", code=500)
    try:
        raise RuntimeError("Oops")
    except RuntimeError:
        slogger.exception("Caught runtime error", extra_data={"module": "test"})
