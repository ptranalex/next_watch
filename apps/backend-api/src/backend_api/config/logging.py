"""Centralized logging configuration for the Backend API with structlog."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import structlog


def configure_logging(
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    verbose: bool = False,
    quiet: bool = False,
    use_coloredlogs: bool = True,
    logger_name: str = "backend_api",
    color_theme: str = "modern",
    http_verbose: bool = False,
    component_levels: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Configure comprehensive logging for Backend API.

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
        >>> logger = get_logger("backend_api")
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
            from structlog.processors import KeyValueRenderer

            ***REMOVED*** Plain key=value format for production
            renderer = KeyValueRenderer(
                key_order=["timestamp", "level", "event", "logger"],
                drop_missing=True,
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
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.format_exc_info,
            structlog_renderer,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=True,
    )

    structlog.get_logger(logger_name).debug("Structlog configured", config=config_info)
    return config_info


def get_logger(name: str = "backend_api") -> Any:
    """Get a structlog logger instance.

    Args:
        name: Logger name, typically __name__ or service name.

    Returns:
        Configured structlog BoundLogger instance for structured logging.

    Example:
        >>> logger = get_logger("backend_api.routes")
        >>> logger.info("Request processed", user_id=123, status_code=200)
    """
    return structlog.get_logger(name)


***REMOVED*** Color theme presets for different environments and preferences
COLOR_THEMES = {
    "modern": {
        "critical": "\033[1;97;41m",  ***REMOVED*** Bold white on red background
        "exception": "\033[1;97;41m",  ***REMOVED*** Bold white on red background
        "error": "\033[1;31m",  ***REMOVED*** Bold red
        "warn": "\033[1;33m",  ***REMOVED*** Bold yellow
        "warning": "\033[1;33m",  ***REMOVED*** Bold yellow
        "info": "\033[1;36m",  ***REMOVED*** Bold cyan
        "debug": "\033[1;35m",  ***REMOVED*** Bold magenta
        "notset": "\033[37m",  ***REMOVED*** Light gray
    },
    "classic": {
        "critical": "\033[1;31m",  ***REMOVED*** Bold red
        "exception": "\033[1;31m",  ***REMOVED*** Bold red
        "error": "\033[31m",  ***REMOVED*** Red
        "warn": "\033[33m",  ***REMOVED*** Yellow
        "warning": "\033[33m",  ***REMOVED*** Yellow
        "info": "\033[32m",  ***REMOVED*** Green
        "debug": "\033[36m",  ***REMOVED*** Cyan
        "notset": "\033[37m",  ***REMOVED*** White
    },
    "minimal": {
        "critical": "\033[1m",  ***REMOVED*** Bold only
        "exception": "\033[1m",  ***REMOVED*** Bold only
        "error": "\033[1m",  ***REMOVED*** Bold only
        "warn": "\033[2m",  ***REMOVED*** Dim
        "warning": "\033[2m",  ***REMOVED*** Dim
        "info": "",  ***REMOVED*** No styling
        "debug": "\033[2m",  ***REMOVED*** Dim
        "notset": "\033[2m",  ***REMOVED*** Dim
    },
    "solarized": {
        "critical": "\033[1;38;5;160m",  ***REMOVED*** Bright red
        "exception": "\033[1;38;5;160m",  ***REMOVED*** Bright red
        "error": "\033[38;5;160m",  ***REMOVED*** Red
        "warn": "\033[38;5;214m",  ***REMOVED*** Orange
        "warning": "\033[38;5;214m",  ***REMOVED*** Orange
        "info": "\033[38;5;33m",  ***REMOVED*** Blue
        "debug": "\033[38;5;125m",  ***REMOVED*** Magenta
        "notset": "\033[38;5;244m",  ***REMOVED*** Gray
    },
}
