"""Core module for the Backend API application.

This module contains the core application factory, middleware setup,
and logging configuration for the Next Watch Backend API service.
"""

from .app import create_app

***REMOVED*** Logging setup - use shared config library directly:
***REMOVED*** from config.logging import configure_logging
from .request_context import (
    RequestContext,
    clear_request_context,
    get_request_context,
    get_request_context_dict,
    increment_query_count,
    set_request_context,
)

__all__ = [
    "create_app",
    ***REMOVED*** "setup_logging",  ***REMOVED*** Use config.logging.configure_logging directly
    "RequestContext",
    "clear_request_context",
    "get_request_context",
    "get_request_context_dict",
    "increment_query_count",
    "set_request_context",
]
