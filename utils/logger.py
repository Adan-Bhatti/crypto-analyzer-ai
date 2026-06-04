"""
Structured Logging Module
==========================
Provides a centralized logging configuration using Python's built-in logging module.
All modules should use ``get_logger(__name__)`` instead of bare ``print()`` statements.
Logs are written to both console (stdout) and a rotating log file.
"""
from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from utils.config import LOGS_DIR


def _ensure_log_dir() -> None:
    """Create the logs directory if it does not exist."""
    Path(LOGS_DIR).mkdir(parents=True, exist_ok=True)


def get_logger(name: str, level: str | None = None) -> logging.Logger:
    """
    Return a configured logger instance for the given module name.

    Args:
        name: The module name (typically ``__name__``).
        level: Optional override for log level. Reads from ``LOG_LEVEL``
               environment variable if not provided. Defaults to ``INFO``.

    Returns:
        A ``logging.Logger`` instance with console and file handlers attached.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if the logger already exists
    if logger.handlers:
        return logger

    # Determine log level from argument, env var, or default
    log_level_str = level or os.getenv("LOG_LEVEL", "INFO")
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Shared formatter for all handlers
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # --- Console handler (stdout) ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # --- Rotating file handler ---
    _ensure_log_dir()
    log_file = Path(LOGS_DIR) / "crypto_analyzer.log"
    file_handler = RotatingFileHandler(
        filename=str(log_file),
        maxBytes=5 * 1024 * 1024,  # 5 MB per file
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
