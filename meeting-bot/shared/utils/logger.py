"""
Shared Logger
Vocaply AI Meeting Intelligence - Day 15

Structured logging setup shared across bot-service and platform bots.
Outputs JSON in production and pretty coloured text in development.
"""

import logging
import sys
import os
from typing import Optional


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Return a configured logger.

    Environment variables:
        LOG_LEVEL  – DEBUG | INFO | WARNING | ERROR  (default: INFO)
        LOG_FORMAT – json | pretty                   (default: pretty)
    """
    log_level  = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    log_format = os.getenv("LOG_FORMAT", "pretty").lower()

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    if logger.handlers:
        return logger  # already configured

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level, logging.INFO))

    if log_format == "json":
        try:
            import json_log_formatter  # type: ignore
            formatter = json_log_formatter.JSONFormatter()
        except ImportError:
            formatter = _pretty_formatter()
    else:
        formatter = _pretty_formatter()

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def _pretty_formatter() -> logging.Formatter:
    return logging.Formatter(
        fmt="%(asctime)s  %(levelname)-8s  [%(name)s]  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# Convenience: module-level logger for shared utilities
logger = get_logger("bot-shared")
