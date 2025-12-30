"""CLI logging configuration and setup.

Provides clean separation between:
- User-facing CLI output (Rich console)
- Operational logging (Structlog, when needed)

Based on proven patterns from BFF API CLI.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog


def configure_cli_logging(
    verbose: bool = False,
    quiet: bool = False,
    command_name: str | None = None,
    log_level: str | None = None,
    log_dir: Path | None = None,
    http_verbose: bool = False,
) -> dict[str, Any]:
    """Configure logging for CLI operations.

    Args:
        verbose: Enable verbose logging output
        quiet: Suppress all output except critical errors
        command_name: Optional command name for context
        log_level: Override log level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Optional directory for log files
        http_verbose: Whether to show HTTP request/response logs (overrides verbose for HTTP)

    Returns:
        Dictionary containing logging configuration details

    Example:
        >>> configure_cli_logging(verbose=True, http_verbose=False, command_name="cache-clear")
        >>> logger = get_logger("my-cli")
        >>> logger.info("Operation started", user_id=123)
    """
    # Determine log level based on mode
    if log_level:
        level_str = log_level.upper()
    elif quiet:
        level_str = "CRITICAL"
    elif verbose:
        level_str = "DEBUG"
    else:
        level_str = "ERROR"  # Silent mode - only errors

    level = getattr(logging, level_str, logging.INFO)

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    # Track configuration
    config_info: dict[str, Any] = {
        "log_level": level_str,
        "verbose": verbose,
        "quiet": quiet,
        "http_verbose": http_verbose,
        "command_name": command_name,
        "log_file": None,
        "handlers": [],
    }

    # Simple formatter for handlers - structlog will format the actual messages
    plain_formatter = logging.Formatter("%(message)s")

    # File handler (structured JSON) if log_dir provided
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"cli_{command_name}_{timestamp}.json"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(plain_formatter)
        root_logger.addHandler(file_handler)
        config_info["log_file"] = str(log_file)
        config_info["handlers"].append("file")

    # Console handler (only in verbose mode for operational logging)
    # User output goes through Rich console separately
    if verbose and not quiet:
        console_handler = logging.StreamHandler(sys.stderr)  # Operational logs to stderr
        console_handler.setLevel(level)
        console_handler.setFormatter(plain_formatter)
        root_logger.addHandler(console_handler)
        config_info["handlers"].append("console")

    # Error handler (always enabled)
    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(plain_formatter)
    root_logger.addHandler(error_handler)
    config_info["handlers"].append("stderr")

    # Enhanced HTTP noise suppression - comprehensive control
    http_loggers = [
        "httpx",
        "httpcore",
        "httpcore.connection",
        "httpcore.http11",
        "httpcore.http2",
        "hpack",
        "h11",
        "h2",
        "asyncio",
        "anyio",
        "redis",
        "urllib3",
        "urllib3.connectionpool",
        "requests",
        "requests.packages.urllib3",
    ]

    # Set HTTP logger levels - more granular control
    if http_verbose:
        # Show HTTP logs when explicitly requested
        http_level = logging.DEBUG if verbose else logging.INFO
    else:
        # Suppress HTTP noise unless critical
        http_level = logging.WARNING

    for http_logger in http_loggers:
        logging.getLogger(http_logger).setLevel(http_level)
        # Completely silence connection pools unless http_verbose
        if http_logger in ["urllib3.connectionpool", "httpcore.connection"] and not http_verbose:
            logging.getLogger(http_logger).propagate = False

    # Configure structlog
    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.format_exc_info,
    ]

    # Choose renderer based on mode
    if verbose:
        from .formatters import get_cli_renderer

        processors.append(get_cli_renderer(colors=True))
    else:
        # Minimal renderer for errors
        from structlog.processors import KeyValueRenderer

        processors.append(
            KeyValueRenderer(
                key_order=["timestamp", "level", "event", "command"],
                drop_missing=True,
            )
        )

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=True,
    )

    # Log configuration if verbose
    if verbose:
        logger = get_logger("cli.logging")
        logger.debug("CLI logging configured", **config_info)

    return config_info


def get_logger(name: str = "cli") -> Any:
    """Get a structlog logger instance.

    Args:
        name: Logger name, typically command name or module name

    Returns:
        Configured structlog BoundLogger instance

    Example:
        >>> logger = get_logger("my-cli.cache")
        >>> logger.info("Cache cleared", pattern="movie:*", count=42)
    """
    return structlog.get_logger(name)


def reset_logging() -> None:
    """Reset logging configuration.

    Useful for testing or when switching between commands.
    """
    logging.getLogger().handlers.clear()
    structlog.reset_defaults()
