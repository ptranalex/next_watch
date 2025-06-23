"""Core module for the Backend API application.

This module contains the fast-core application factory and related utilities
for the Next Watch Backend API service.
"""

from .app_fast_core import create_backend_app, get_backend_app

__all__ = [
    "create_backend_app",
    "get_backend_app",
]
