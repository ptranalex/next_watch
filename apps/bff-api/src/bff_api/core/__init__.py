"""Core module for the BFF service.

This module contains the foundational components for the Next Watch BFF service,
implementing a clean Application Factory pattern.
"""

from .app import create_app
from .logging import setup_logging

__all__ = ["create_app", "setup_logging"]
