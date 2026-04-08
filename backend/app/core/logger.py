"""
Logging configuration for RepoHealth backend.

Provides a centralized logging setup with configurable levels and output formats.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from app.core.config import get_settings


def setup_logger(name: str = "repohealth") -> logging.Logger:
    """
    Set up and configure a logger.

    Args:
        name: Logger name (default: "repohealth")

    Returns:
        Configured logger instance.
    """
    settings = get_settings()
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Set log level based on environment
    if settings.app_debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler (always)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler for production
    if settings.app_env == "production":
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"{name}.log"

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

    logger.debug("Logger '%s' configured successfully", name)
    return logger


# Global logger instance
_logger: Optional[logging.Logger] = None


def get_logger(name: str = "repohealth") -> logging.Logger:
    """
    Get or create the global logger instance.

    Args:
        name: Logger name (default: "repohealth")

    Returns:
        Logger instance.
    """
    global _logger
    if _logger is None or _logger.name != name:
        _logger = setup_logger(name)
    return _logger


# Convenience functions for common log levels
def log_debug(msg: str, *args, **kwargs) -> None:
    """Log debug message."""
    get_logger().debug(msg, *args, **kwargs)


def log_info(msg: str, *args, **kwargs) -> None:
    """Log info message."""
    get_logger().info(msg, *args, **kwargs)


def log_warning(msg: str, *args, **kwargs) -> None:
    """Log warning message."""
    get_logger().warning(msg, *args, **kwargs)


def log_error(msg: str, *args, **kwargs) -> None:
    """Log error message."""
    get_logger().error(msg, *args, **kwargs)


def log_critical(msg: str, *args, **kwargs) -> None:
    """Log critical message."""
    get_logger().critical(msg, *args, **kwargs)


def log_exception(msg: str, *args, **kwargs) -> None:
    """Log exception with traceback."""
    get_logger().exception(msg, *args, **kwargs)