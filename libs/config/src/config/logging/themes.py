"""Color theme presets for console logging output.

Provides various color schemes for different environments and preferences,
from vibrant modern themes to minimal production-friendly options.
"""

from typing import Dict

***REMOVED*** Color theme presets for different environments and preferences
COLOR_THEMES: Dict[str, Dict[str, str]] = {
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
