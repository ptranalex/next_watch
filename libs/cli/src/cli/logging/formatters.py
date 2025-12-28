"""CLI-specific formatters and color themes.

Provides Rich-compatible formatters and color themes for structured logging
in CLI applications, based on enterprise patterns from BFF API.
"""

from typing import Any

import structlog

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
        "critical": "\033[31m",  ***REMOVED*** Red
        "exception": "\033[31m",  ***REMOVED*** Red
        "error": "\033[31m",  ***REMOVED*** Red
        "warn": "\033[33m",  ***REMOVED*** Yellow
        "warning": "\033[33m",  ***REMOVED*** Yellow
        "info": "",  ***REMOVED*** No color
        "debug": "\033[37m",  ***REMOVED*** Gray
        "notset": "\033[37m",  ***REMOVED*** Gray
    },
    "solarized": {
        "critical": "\033[1;31m",  ***REMOVED*** Bold red
        "exception": "\033[1;31m",  ***REMOVED*** Bold red
        "error": "\033[31m",  ***REMOVED*** Red
        "warn": "\033[93m",  ***REMOVED*** Bright yellow
        "warning": "\033[93m",  ***REMOVED*** Bright yellow
        "info": "\033[94m",  ***REMOVED*** Bright blue
        "debug": "\033[92m",  ***REMOVED*** Bright green
        "notset": "\033[90m",  ***REMOVED*** Dark gray
    },
}


def get_cli_renderer(colors: bool = True, theme: str = "modern", pad_event: int = 30) -> Any:
    """Get a CLI-optimized structlog renderer.

    Args:
        colors: Whether to use colored output
        theme: Color theme name (modern, classic, minimal, solarized)
        pad_event: Width for event field padding

    Returns:
        Configured structlog renderer

    Example:
        >>> renderer = get_cli_renderer(colors=True, theme="solarized")
        >>> ***REMOVED*** Use in structlog configuration
    """
    if colors:
        selected_theme = COLOR_THEMES.get(theme, COLOR_THEMES["modern"])
        return structlog.dev.ConsoleRenderer(
            colors=True,
            level_styles=selected_theme,
            pad_event=pad_event,
        )
    else:
        return structlog.processors.KeyValueRenderer(
            key_order=["timestamp", "level", "event", "command", "service"],
            drop_missing=True,
        )


def get_json_renderer() -> Any:
    """Get a JSON renderer for file logging.

    Returns:
        JSON renderer for structured file logs

    Example:
        >>> renderer = get_json_renderer()
        >>> ***REMOVED*** Use for file handlers
    """
    return structlog.processors.JSONRenderer()


class CLIFormatter:
    """Enhanced formatter for CLI logging with context awareness."""

    def __init__(
        self,
        service_name: str,
        command_name: str | None = None,
        colors: bool = True,
        theme: str = "modern",
    ):
        """Initialize CLI formatter.

        Args:
            service_name: Name of the service
            command_name: Name of the current command
            colors: Whether to use colored output
            theme: Color theme to use
        """
        self.service_name = service_name
        self.command_name = command_name
        self.colors = colors
        self.theme = theme

    def __call__(self, logger: Any, method_name: str, event_dict: dict[str, Any]) -> Any:
        """Format log record with CLI context.

        Args:
            logger: Logger instance
            method_name: Log method name
            event_dict: Event dictionary

        Returns:
            Formatted log message
        """
        ***REMOVED*** Add CLI context
        event_dict.setdefault("service", self.service_name)
        if self.command_name:
            event_dict.setdefault("command", self.command_name)
        event_dict.setdefault("component", "cli")

        ***REMOVED*** Use appropriate renderer
        renderer = get_cli_renderer(colors=self.colors, theme=self.theme, pad_event=30)

        return renderer(logger, method_name, event_dict)
