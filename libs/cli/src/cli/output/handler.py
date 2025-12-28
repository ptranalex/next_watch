"""CLI output handler for clean user experience.

Based on the sophisticated patterns from BFF API CLI, this module provides
unified CLI output handling with separation between user-facing output and
operational logging.
"""

import logging
import sys
from typing import Any

import structlog
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
)
from rich.prompt import Confirm


def configure_basic_cli_logging(
    verbose: bool = False, quiet: bool = False, command_name: str | None = None
) -> None:
    """Configure basic structured logging for CLI operations.

    This should be called at the CLI application entrypoint, not automatically.
    This is a simpler version compared to the comprehensive logging in logging.setup.

    Args:
        verbose: Enable verbose logging output
        quiet: Suppress logging output
        command_name: Name of the command for context
    """
    if quiet:
        level = "ERROR"
    elif verbose:
        level = "DEBUG"
    else:
        level = "INFO"

    ***REMOVED*** Configure structlog with proper logging levels
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            (structlog.dev.set_exc_info if verbose else structlog.processors.format_exc_info),
            (
                structlog.processors.JSONRenderer()
                if not verbose
                else structlog.dev.ConsoleRenderer()
            ),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, level, logging.INFO)),
        logger_factory=structlog.WriteLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )


class CLIOutput:
    """Unified CLI output handler for clean user experience.

    Provides separation between:
    - User-facing output (Rich console to stdout)
    - Operational logging (Structlog to stderr, verbose mode only)
    - Error output (Rich console to stderr)

    Based on the sophisticated patterns from BFF API CLI.
    """

    def __init__(self, command_name: str, verbose: bool = False, quiet: bool = False):
        """Initialize CLI output handler.

        Args:
            command_name: Name of the CLI command
            verbose: Enable verbose mode with operational logging
            quiet: Enable quiet mode (suppress most output)
        """
        self.command_name = command_name
        self.verbose = verbose
        self.quiet = quiet

        ***REMOVED*** Note: Structlog should be configured at the application level, not here

        ***REMOVED*** Rich console for user output (stdout)
        self.console = Console(
            stderr=False,  ***REMOVED*** User output goes to stdout
            highlight=False,  ***REMOVED*** Disable auto-highlighting for cleaner output
            force_terminal=None,  ***REMOVED*** Auto-detect terminal capabilities
        )

        ***REMOVED*** Error console for error messages (stderr)
        self.error_console = Console(file=sys.stderr, style="red", highlight=False)

        ***REMOVED*** Operational logger (only used in verbose mode)
        self.logger = structlog.get_logger("cli").bind(command=command_name, component="cli")

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
            self.logger.debug(message, **context)

    def log_operation(self, message: str, **context: Any) -> None:
        """Log operational information (only in verbose mode).

        Args:
            message: Operation message
            **context: Additional context for structured logging
        """
        if self.verbose:
            self.logger.info(message, **context)

    def log_error(self, message: str, error: Exception, **context: Any) -> None:
        """Log error with context (always logged).

        Args:
            message: Error message
            error: Exception that occurred
            **context: Additional context for structured logging
        """
        self.logger.error(message, error=str(error), error_type=type(error).__name__, **context)

    def progress(self, description: str, total: int | None = None) -> Progress:
        """Create a progress indicator.

        Args:
            description: Description of the operation
            total: Total number of items (None for indeterminate)

        Returns:
            Rich Progress instance
        """
        if self.quiet:
            ***REMOVED*** Return a dummy progress that does nothing
            return Progress(disable=True)

        if total is None:
            ***REMOVED*** Indeterminate progress with spinner
            return Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=True,
            )
        else:
            ***REMOVED*** Determinate progress with bar
            return Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                MofNCompleteColumn(),
                console=self.console,
                transient=True,
            )

    def confirm(self, question: str, default: bool = False) -> bool:
        """Ask for user confirmation.

        Args:
            question: Question to ask the user
            default: Default answer if user just presses Enter

        Returns:
            True if user confirmed, False otherwise
        """
        if self.quiet:
            ***REMOVED*** In quiet mode, use the default
            return default

        return Confirm.ask(question, console=self.console, default=default)


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
