"""Color theme presets for console logging output.

Provides various color schemes for different environments and preferences,
from vibrant modern themes to minimal production-friendly options.
"""

# Color theme presets for different environments and preferences
COLOR_THEMES: dict[str, dict[str, str]] = {
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
        "critical": "\033[1m",  # Bold only
        "exception": "\033[1m",  # Bold only
        "error": "\033[1m",  # Bold only
        "warn": "\033[2m",  # Dim
        "warning": "\033[2m",  # Dim
        "info": "",  # No styling
        "debug": "\033[2m",  # Dim
        "notset": "\033[2m",  # Dim
    },
    "solarized": {
        "critical": "\033[1;38;5;160m",  # Bright red
        "exception": "\033[1;38;5;160m",  # Bright red
        "error": "\033[38;5;160m",  # Red
        "warn": "\033[38;5;214m",  # Orange
        "warning": "\033[38;5;214m",  # Orange
        "info": "\033[38;5;33m",  # Blue
        "debug": "\033[38;5;125m",  # Magenta
        "notset": "\033[38;5;244m",  # Gray
    },
}
