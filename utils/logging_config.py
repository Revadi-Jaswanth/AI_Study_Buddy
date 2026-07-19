"""Application logging helpers."""

import logging
from logging.handlers import RotatingFileHandler

from config import LOGGING_CONFIG


_CONFIGURED = False


def setup_logging() -> None:
    """Configure rotating file logging for the application."""
    global _CONFIGURED

    if _CONFIGURED:
        return

    LOGGING_CONFIG.log_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger = logging.getLogger()
    logger.setLevel(
        getattr(logging, LOGGING_CONFIG.level.upper(), logging.INFO)
    )

    handler = RotatingFileHandler(
        LOGGING_CONFIG.log_file,
        maxBytes=LOGGING_CONFIG.max_bytes,
        backupCount=LOGGING_CONFIG.backup_count,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
    )

    logger.addHandler(handler)
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger for a module."""
    setup_logging()
    return logging.getLogger(name)
