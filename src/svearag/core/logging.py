"""Structured logging configuration for SveaRAG."""

import json
import logging
import sys
from typing import Any

RESERVED_ATTRS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "message",
    "asctime",
}


class JSONFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include custom extra fields if present
        for key, value in record.__dict__.items():
            if key not in RESERVED_ATTRS:
                log_payload[key] = value

        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_payload, default=str)


def _sanitize_extra(extra_dict: dict[str, Any]) -> dict[str, Any]:
    """Ensures keys do not collide with Python's reserved LogRecord attributes."""
    safe_dict = {}
    for k, v in extra_dict.items():
        key = f"custom_{k}" if k in RESERVED_ATTRS else k
        safe_dict[key] = v
    return safe_dict


class StructuredLogger:
    """Wrapper around standard Logger supporting arbitrary keyword arguments and extra_data."""

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def _log(
        self, level: int, msg: str, extra_data: dict[str, Any] | None = None, **kwargs: Any
    ) -> None:
        merged = dict(kwargs)
        if extra_data:
            merged.update(extra_data)
        safe_extra = _sanitize_extra(merged)
        self._logger.log(level, msg, extra=safe_extra)

    def debug(self, msg: str, extra_data: dict[str, Any] | None = None, **kwargs: Any) -> None:
        self._log(logging.DEBUG, msg, extra_data, **kwargs)

    def info(self, msg: str, extra_data: dict[str, Any] | None = None, **kwargs: Any) -> None:
        self._log(logging.INFO, msg, extra_data, **kwargs)

    def warning(self, msg: str, extra_data: dict[str, Any] | None = None, **kwargs: Any) -> None:
        self._log(logging.WARNING, msg, extra_data, **kwargs)

    def error(self, msg: str, extra_data: dict[str, Any] | None = None, **kwargs: Any) -> None:
        self._log(logging.ERROR, msg, extra_data, **kwargs)

    def exception(self, msg: str, extra_data: dict[str, Any] | None = None, **kwargs: Any) -> None:
        merged = dict(kwargs)
        if extra_data:
            merged.update(extra_data)
        safe_extra = _sanitize_extra(merged)
        self._logger.exception(msg, extra=safe_extra)


def setup_logger(name: str = "svearag", level: int = logging.INFO) -> StructuredLogger:
    """Configures and returns a structured JSON logger."""
    base_logger = logging.getLogger(name)
    base_logger.setLevel(level)

    if not base_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        base_logger.addHandler(handler)

    return StructuredLogger(base_logger)


logger = setup_logger()
