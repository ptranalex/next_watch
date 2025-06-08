"""Core module for the Backend API application.

This module contains the core application factory, middleware setup,
and logging configuration for the Next Watch Backend API service.
"""

from .app import create_app
from .logging import setup_logging

__all__ = ["create_app", "setup_logging"]
