"""Logging configuration for BFF application."""

import logging
import sys
from typing import Dict, Any, Optional, Callable
from functools import wraps

from .app import Config


def configure_logging(
    config: Optional[Config] = None,
    log_level: Optional[str] = None,
    verbose: bool = False,
) -> Dict[str, Any]:
    """Configure logging for the BFF application.

    Args:
        config: Configuration instance (optional, will create if None)
        log_level: Override log level (optional)
        verbose: Enable verbose logging

    Returns:
        Dictionary with logging configuration details
    """
    if config is None:
        config = Config.get_instance()

    ***REMOVED*** Determine effective log level
    effective_level = log_level or config.log_level
    if verbose:
        effective_level = "DEBUG"

    ***REMOVED*** Configure root logger
    logging.basicConfig(
        level=getattr(logging, effective_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    ***REMOVED*** Configure specific loggers
    loggers_config = {
        "bff": effective_level,
        "uvicorn": "INFO" if not verbose else "DEBUG",
        "httpx": "WARNING" if not verbose else "DEBUG",
        "redis": "WARNING" if not verbose else "INFO",
    }

    for logger_name, level in loggers_config.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, level.upper()))

    ***REMOVED*** Suppress noisy loggers in production
    if config.is_production:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    return {
        "effective_level": effective_level,
        "verbose": verbose,
        "loggers": loggers_config,
        "environment": config.environment,
    }


def with_logging(
    log_level: Optional[str] = None,
    verbose: bool = False,
    config: Optional[Config] = None,
) -> Callable:
    """Decorator to automatically configure logging for a function.

    Args:
        log_level: Override log level
        verbose: Enable verbose logging
        config: Configuration instance

    Returns:
        Decorated function with logging configured
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            ***REMOVED*** Configure logging before function execution
            logging_config = configure_logging(
                config=config,
                log_level=log_level,
                verbose=verbose,
            )

            ***REMOVED*** Get logger for the decorated function
            logger = logging.getLogger(func.__module__)
            logger.info(
                f"Starting {func.__name__} with logging config: {logging_config}"
            )

            try:
                result = func(*args, **kwargs)
                logger.info(f"Completed {func.__name__} successfully")
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                raise

        return wrapper

    return decorator
