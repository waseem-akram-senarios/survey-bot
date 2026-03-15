"""
Logging utilities for the demo bot.
Handles per-call logging and general logging setup.
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

from config.settings import LOG_DIR


_logger = logging.getLogger("demo-agent")
_logger.setLevel(logging.INFO)


def get_logger() -> logging.Logger:
    """Get the demo agent logger."""
    return _logger


def setup_survey_logging(room_name: str, caller_number: str) -> tuple[str, RotatingFileHandler]:
    """
    Set up a separate log file for this survey call.

    Returns:
        tuple: (log_filename, file_handler)
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    caller_clean = caller_number.replace("+", "").replace("-", "").replace(" ", "")
    log_filename = f"{LOG_DIR}/survey_{timestamp}_{caller_clean}_{room_name}.log"

    file_handler = RotatingFileHandler(
        log_filename,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    _logger.addHandler(file_handler)

    _logger.info(f"LOG FILE CREATED: {log_filename}")
    return log_filename, file_handler


def cleanup_survey_logging(handler: RotatingFileHandler) -> None:
    """Remove the survey-specific handler after the call ends."""
    _logger.removeHandler(handler)
    handler.close()
