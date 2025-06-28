"""Centralized logging configuration for NextWatch services with structlog."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import structlog

from config.logging.themes import COLOR_THEMES


def configure_logging(
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    verbose: bool = False,
    quiet: bool = False,
    use_coloredlogs: bool = True,
    logger_name: str = "nextwatch",
    color_theme: str = "modern",
    http_verbose: bool = False,
    component_levels: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Configure comprehensive logging for NextWatch services.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR).
        log_dir: Directory to store log files. If None, only console logging.
        verbose: Whether to show verbose output in console.
        quiet: Whether to suppress all console output except errors.
        use_coloredlogs: Whether to use colored console output.
        logger_name: Name of the root logger.
        color_theme: Color theme preset (modern, classic, minimal, solarized).
        http_verbose: Whether to show HTTP request/response logs (overrides verbose for HTTP).
        component_levels: Per-component log level overrides (e.g., {"health": "DEBUG", "db": "INFO"}).

    Returns:
        Dictionary containing logging configuration details including log_level,
        verbose settings, log file path, and active handlers.

    Example:
        >>> from pathlib import Path
        >>> config = configure_logging(
        ...     log_level="DEBUG",
        ...     log_dir=Path("./logs"),
        ...     verbose=True,
        ...     http_verbose=False,  ***REMOVED*** Suppress HTTP noise
        ...     component_levels={"health": "INFO", "db": "DEBUG"},
        ...     color_theme="solarized"
        ... )
        >>> logger = get_logger("nextwatch.service")
        >>> logger.info("Application started", service="backend-api")
    """

    log_level = log_level.upper()
    ***REMOVED*** Convert string log level to logging constant (e.g., "INFO" -> logging.INFO)
    level = getattr(logging, log_level, logging.INFO)

    ***REMOVED*** Set up root logger - this is the base logger for all Python logging
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()  ***REMOVED*** Remove any existing handlers to avoid conflicts

    ***REMOVED*** Track configuration details for debugging and monitoring
    config_info: Dict[str, Any] = {
        "log_level": log_level,
        "verbose": verbose,
        "quiet": quiet,
        "http_verbose": http_verbose,
        "component_levels": component_levels or {},
        "log_file": None,
        "handlers": [],
    }

    ***REMOVED*** Simple formatter for handlers - structlog will format the actual messages
    plain_formatter = logging.Formatter("%(message)s")

    ***REMOVED*** File handler (structured JSON) with error handling
    if log_dir:
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"{logger_name}_{datetime.now():%Y%m%d_%H%M%S}.json"
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(plain_formatter)
            root_logger.addHandler(file_handler)
            config_info["log_file"] = str(log_file)
            config_info["handlers"].append("file")
        except (PermissionError, OSError) as e:
            ***REMOVED*** Fall back to console-only logging if file logging fails
            print(f"Warning: Could not create log file at {log_dir}: {e}")
            print("Falling back to console-only logging.")
            config_info["log_file"] = None
            config_info["file_handler_error"] = str(e)

    ***REMOVED*** Console handler (human readable)
    renderer: Any = None
    if not quiet:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        ***REMOVED*** Choose how to format console output
        if use_coloredlogs:
            from structlog.dev import ConsoleRenderer

            ***REMOVED*** Custom color theme for enhanced readability
            selected_theme = COLOR_THEMES.get(color_theme, COLOR_THEMES["modern"])
            renderer = ConsoleRenderer(
                colors=True,
                ***REMOVED*** Apply selected color theme
                level_styles=selected_theme,
                ***REMOVED*** Pad event field for better alignment - makes logs more readable
                pad_event=35,
            )
        else:
            from structlog.processors import LogfmtRenderer

            ***REMOVED*** Standard logfmt format for production - perfect for Grafana parsing
            renderer = LogfmtRenderer(
                key_order=["timestamp", "level", "logger", "event"],
                drop_missing=True,
                sort_keys=False,
            )

        console_handler.setFormatter(plain_formatter)
        root_logger.addHandler(console_handler)
        config_info["handlers"].append("console")

    ***REMOVED*** Error to stderr
    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(plain_formatter)
    root_logger.addHandler(error_handler)
    config_info["handlers"].append("stderr")

    ***REMOVED*** Enhanced HTTP noise suppression - more comprehensive list
    http_loggers = [
        "fastapi",
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
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
        "httptools",
    ]

    ***REMOVED*** Set HTTP logger levels based on http_verbose flag
    http_level = logging.DEBUG if http_verbose else logging.WARNING
    for http_logger in http_loggers:
        logging.getLogger(http_logger).setLevel(http_level)
        ***REMOVED*** Block noisy access logs completely unless explicitly requested
        if http_logger in ["uvicorn.access"] and not http_verbose:
            logging.getLogger(http_logger).propagate = False

    ***REMOVED*** Apply component-specific log levels
    if component_levels:
        for component, component_level in component_levels.items():
            component_level_int = getattr(logging, component_level.upper(), logging.INFO)
            component_logger_name = f"{logger_name}.{component}"
            logging.getLogger(component_logger_name).setLevel(component_level_int)
            config_info["component_levels"][component] = component_level.upper()

    ***REMOVED*** Additional fine-tuning for non-verbose mode
    if not verbose:
        ***REMOVED*** Suppress other noisy third-party loggers
        for noisy in [
            "redis",
            "urllib3",
            "urllib3.connectionpool",
            "requests",
            "requests.packages.urllib3",
            "botocore",
            "boto3",
            "aiobotocore",
        ]:
            logging.getLogger(noisy).setLevel(logging.WARNING)

    ***REMOVED*** Choose structlog renderer - use console renderer for better formatting
    if renderer:
        structlog_renderer = renderer
    else:
        from structlog.dev import ConsoleRenderer

        structlog_renderer = ConsoleRenderer(colors=use_coloredlogs)

    ***REMOVED*** Structlog configuration
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,  ***REMOVED*** Add logger name to log records
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.format_exc_info,
            structlog_renderer,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=True,
    )

    structlog.get_logger(logger_name).debug("Structlog configured", **config_info)
    return config_info


def get_logger(name: str = "nextwatch") -> Any:
    """Get a structlog logger instance.

    Args:
        name: Logger name, typically __name__ or service name.

    Returns:
        Configured structlog BoundLogger instance for structured logging.

    Example:
        >>> logger = get_logger("nextwatch.backend")
        >>> logger.info("Request processed", user_id=123, status_code=200)
    """
    return structlog.get_logger(name)
