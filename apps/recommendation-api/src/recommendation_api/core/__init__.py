"""Core modules for the Recommendation API."""

from .app import create_app
from .logging import setup_logging
from .middleware import setup_middleware

__all__ = ["create_app", "setup_logging", "setup_middleware"]
