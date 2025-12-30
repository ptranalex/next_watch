"""CLI-specific formatters and color themes.

Provides Rich-compatible formatters and color themes for structured logging
in CLI applications, based on enterprise patterns from BFF API.
"""

from typing import Any

import structlog

# Color theme presets for different environments and preferences
COLOR_THEMES = {
    "modern": {
        "critical": "\033[1;97;41m",  # Bold white on red background
        "exception": "\033[1;97;41m",  # Bold white on red background
        "error": "\033[1;31m",  # Bold red
        "warn": "\033[1;33m",  # Bold yellow
        "warning": "\033[1;33m",  # Bold yellow
        "info": "\033[1;36m",  # Bold cyan
        "debug": "\033[1;35m",  # Bold magenta
        "notset": "\033[37m",  # Light gray
    },
    "classic": {
        "critical": "\033[1;31m",  # Bold red
        "exception": "\033[1;31m",  # Bold red
        "error": "\033[31m",  # Red
        "warn": "\033[33m",  # Yellow
        "warning": "\033[33m",  # Yellow
        "info": "\033[32m",  # Green
        "debug": "\033[36m",  # Cyan
        "notset": "\033[37m",  # White
    },
    "minimal": {
        "critical": "\033[31m",  # Red
        "exception": "\033[31m",  # Red
        "error": "\033[31m",  # Red
        "warn": "\033[33m",  # Yellow
        "warning": "\033[33m",  # Yellow
        "info": "",  # No color
        "debug": "\033[37m",  # Gray
        "notset": "\033[37m",  # Gray
    },
    "solarized": {
        "critical": "\033[1;31m",  # Bold red
        "exception": "\033[1;31m",  # Bold red
        "error": "\033[31m",  # Red
        "warn": "\033[93m",  # Bright yellow
        "warning": "\033[93m",  # Bright yellow
        "info": "\033[94m",  # Bright blue
        "debug": "\033[92m",  # Bright green
        "notset": "\033[90m",  # Dark gray
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
        >>> # Use in structlog configuration
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
        >>> # Use for file handlers
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
        # Add CLI context
        event_dict.setdefault("service", self.service_name)
        if self.command_name:
            event_dict.setdefault("command", self.command_name)
        event_dict.setdefault("component", "cli")

        # Use appropriate renderer
        renderer = get_cli_renderer(colors=self.colors, theme=self.theme, pad_event=30)

        return renderer(logger, method_name, event_dict)
