"""CLI-specific logging configuration and utilities.

This module provides clean separation between:
- User-facing CLI output (Rich console)
- Operational logging (Structlog, when needed)
"""

import os
import sys
from typing import Optional, Any
from pathlib import Path

from rich.console import Console
from bff_api.config.logging import configure_logging, get_logger


def configure_cli_logging(
    verbose: bool = False, quiet: bool = False, command_name: Optional[str] = None
) -> None:
    """Configure logging for CLI operations.

    Args:
        verbose: Enable verbose logging output
        quiet: Suppress all output except critical errors
        command_name: Optional command name for context
    """
    if quiet:
        ***REMOVED*** Only critical errors to stderr
        configure_logging(
            log_level="CRITICAL",
            log_dir=None,  ***REMOVED*** No file logging for CLI
            verbose=False,
            quiet=True,
            use_coloredlogs=False,
            logger_name=f"bff_api.cli.{command_name}" if command_name else "bff_api.cli",
        )
    elif verbose:
        ***REMOVED*** Full structured logging to stderr for debugging
        configure_logging(
            log_level="DEBUG",
            log_dir=None,  ***REMOVED*** No file logging for CLI unless explicitly needed
            verbose=True,
            quiet=False,
            use_coloredlogs=True,
            color_theme="classic",  ***REMOVED*** More subdued for CLI
            logger_name=f"bff_api.cli.{command_name}" if command_name else "bff_api.cli",
        )
    else:
        ***REMOVED*** Silent mode - no operational logging, only user output
        configure_logging(
            log_level="ERROR",  ***REMOVED*** Only errors
            log_dir=None,
            verbose=False,
            quiet=True,
            use_coloredlogs=False,
            logger_name=f"bff_api.cli.{command_name}" if command_name else "bff_api.cli",
        )


class CLIOutput:
    """Unified CLI output handler for clean user experience."""

    def __init__(self, command_name: str, verbose: bool = False, quiet: bool = False):
        """Initialize CLI output handler.

        Args:
            command_name: Name of the CLI command
            verbose: Enable verbose mode
            quiet: Enable quiet mode
        """
        self.command_name = command_name
        self.verbose = verbose
        self.quiet = quiet

        ***REMOVED*** Configure logging based on mode
        configure_cli_logging(verbose=verbose, quiet=quiet, command_name=command_name)

        ***REMOVED*** Rich console for user output
        self.console = Console(
            stderr=False,  ***REMOVED*** User output goes to stdout
            highlight=False,  ***REMOVED*** Disable auto-highlighting for cleaner output
            force_terminal=None,  ***REMOVED*** Auto-detect terminal capabilities
        )

        ***REMOVED*** Error console for error messages
        self.error_console = Console(file=sys.stderr, style="red", highlight=False)

        ***REMOVED*** Operational logger (only used in verbose mode)
        self.logger = get_logger(f"bff_api.cli.{command_name}")

    def info(self, message: str, **rich_kwargs: Any) -> None:
        """Display informational message to user.

        Args:
            message: Message to display
            **rich_kwargs: Additional Rich formatting options
        """
        if not self.quiet:
            self.console.print(message, **rich_kwargs)

    def success(self, message: str, **rich_kwargs: Any) -> None:
        """Display success message to user.

        Args:
            message: Success message
            **rich_kwargs: Additional Rich formatting options
        """
        if not self.quiet:
            self.console.print(f"✅ {message}", style="green", **rich_kwargs)

    def warning(self, message: str, **rich_kwargs: Any) -> None:
        """Display warning message to user.

        Args:
            message: Warning message
            **rich_kwargs: Additional Rich formatting options
        """
        if not self.quiet:
            self.console.print(f"⚠️  {message}", style="yellow", **rich_kwargs)

    def error(self, message: str, **rich_kwargs: Any) -> None:
        """Display error message to user.

        Args:
            message: Error message
            **rich_kwargs: Additional Rich formatting options
        """
        self.error_console.print(f"❌ {message}", **rich_kwargs)

    def debug(self, message: str, **context: Any) -> None:
        """Log debug information (only in verbose mode).

        Args:
            message: Debug message
            **context: Additional context for structured logging
        """
        if self.verbose:
            self.logger.debug(
                message, service="bff", component="cli", command=self.command_name, **context
            )

    def log_operation(self, message: str, **context: Any) -> None:
        """Log operational information (only in verbose mode).

        Args:
            message: Operation message
            **context: Additional context for structured logging
        """
        if self.verbose:
            self.logger.info(
                message, service="bff", component="cli", command=self.command_name, **context
            )

    def log_error(self, message: str, error: Exception, **context: Any) -> None:
        """Log error with context (always logged).

        Args:
            message: Error message
            error: Exception that occurred
            **context: Additional context for structured logging
        """
        self.logger.error(
            message,
            error=str(error),
            error_type=type(error).__name__,
            service="bff",
            component="cli",
            command=self.command_name,
            **context,
        )


def get_cli_output(command_name: str, verbose: bool = False, quiet: bool = False) -> CLIOutput:
    """Get CLI output handler for a command.

    Args:
        command_name: Name of the CLI command
        verbose: Enable verbose mode
        quiet: Enable quiet mode

    Returns:
        CLIOutput instance configured for the command
    """
    return CLIOutput(command_name, verbose=verbose, quiet=quiet)
