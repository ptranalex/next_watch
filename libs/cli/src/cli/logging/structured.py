"""Structured logging utilities for CLI applications.

Provides CLI-specific logging patterns and decorators for automatic
logging setup, following enterprise patterns from BFF API.
"""

import functools
from typing import Optional, Any, Callable, Dict
from pathlib import Path

from .setup import configure_cli_logging, get_logger


class CLILogger:
    """Enhanced logger for CLI operations with automatic context."""

    def __init__(
        self,
        name: str,
        service_name: str = "cli",
        command_name: Optional[str] = None,
        verbose: bool = False,
    ):
        """Initialize CLI logger.

        Args:
            name: Logger name
            service_name: Name of the service
            command_name: Current command name
            verbose: Whether verbose logging is enabled
        """
        self.name = name
        self.service_name = service_name
        self.command_name = command_name
        self.verbose = verbose
        self._logger = get_logger(name)

    def _add_context(self, **kwargs: Any) -> Dict[str, Any]:
        """Add standard CLI context to log entries."""
        context = {
            "service": self.service_name,
            "component": "cli",
        }
        if self.command_name:
            context["command"] = self.command_name
        context.update(kwargs)
        return context

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message with CLI context."""
        if self.verbose:
            self._logger.debug(message, **self._add_context(**kwargs))

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message with CLI context."""
        self._logger.info(message, **self._add_context(**kwargs))

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with CLI context."""
        self._logger.warning(message, **self._add_context(**kwargs))

    def error(
        self, message: str, error: Optional[Exception] = None, **kwargs: Any
    ) -> None:
        """Log error message with CLI context.

        Args:
            message: Error message
            error: Optional exception object
            **kwargs: Additional context
        """
        context = self._add_context(**kwargs)
        if error:
            context.update(
                {
                    "error": str(error),
                    "error_type": type(error).__name__,
                }
            )
        self._logger.error(message, **context)

    def operation(self, message: str, **kwargs: Any) -> None:
        """Log operational information (only in verbose mode).

        Args:
            message: Operation message
            **kwargs: Additional context
        """
        if self.verbose:
            self._logger.info(f"[OPERATION] {message}", **self._add_context(**kwargs))

    def bind(self, **kwargs: Any) -> "CLILogger":
        """Create a new logger with additional bound context.

        Args:
            **kwargs: Context to bind

        Returns:
            New logger instance with bound context
        """
        new_logger = CLILogger(
            name=self.name,
            service_name=self.service_name,
            command_name=self.command_name,
            verbose=self.verbose,
        )
        new_logger._logger = self._logger.bind(**kwargs)
        return new_logger


def with_logging(
    log_level: Optional[str] = None,
    verbose: bool = False,
    quiet: bool = False,
    log_dir: Optional[Path] = None,
    service_name: str = "cli",
) -> Callable[..., Any]:
    """Decorator to automatically configure logging for CLI commands.

    Args:
        log_level: Override log level
        verbose: Enable verbose logging
        quiet: Enable quiet mode
        log_dir: Optional log directory
        service_name: Service name for context

    Returns:
        Decorator function

    Example:
        >>> @with_logging(verbose=True, service_name="my-service")
        ... def my_command():
        ...     logger = get_logger("my-command")
        ...     logger.info("Command started")
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            ***REMOVED*** Extract command name from function name
            command_name = func.__name__.replace("_", "-")

            ***REMOVED*** Configure logging
            configure_cli_logging(
                verbose=verbose,
                quiet=quiet,
                command_name=command_name,
                log_level=log_level,
                log_dir=log_dir,
            )

            ***REMOVED*** Create logger for the command
            logger = CLILogger(
                name=f"{service_name}.{command_name}",
                service_name=service_name,
                command_name=command_name,
                verbose=verbose,
            )

            try:
                logger.operation("Command started", function=func.__name__)
                result = func(*args, **kwargs)
                logger.operation("Command completed successfully")
                return result
            except Exception as e:
                logger.error("Command failed", error=e, function=func.__name__)
                raise

        return wrapper

    return decorator


def get_cli_logger(
    name: str,
    service_name: str = "cli",
    command_name: Optional[str] = None,
    verbose: bool = False,
) -> CLILogger:
    """Get a CLI logger instance.

    Args:
        name: Logger name
        service_name: Service name for context
        command_name: Command name for context
        verbose: Whether verbose logging is enabled

    Returns:
        CLILogger instance

    Example:
        >>> logger = get_cli_logger("cache", service_name="backend-api", verbose=True)
        >>> logger.info("Cache operation started", pattern="movie:*")
    """
    return CLILogger(
        name=name,
        service_name=service_name,
        command_name=command_name,
        verbose=verbose,
    )
