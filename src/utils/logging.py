"""Logging utilities."""

import logging
from config.settings import get_settings


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    settings = get_settings()
    logger = logging.getLogger(name)
    logger.setLevel(settings.log_level)
    return logger
