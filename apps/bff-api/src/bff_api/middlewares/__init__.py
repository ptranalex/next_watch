"""Middlewares package for BFF API application.

This package provides FastAPI middleware components that process HTTP requests
and responses, applying cross-cutting concerns across the entire API. These
middlewares handle authentication, logging, and other operational aspects of
the application.

Key components:
- LoggingMiddleware: Handles request/response logging and performance tracking
- AuthMiddleware: Manages authentication, token validation, and authorization

Middlewares are registered in the FastAPI application startup in main.py and
are executed in reverse order of registration (last registered is executed first).

See the README.md file in this directory for detailed documentation.
"""

from .logging import LoggingMiddleware
from .auth import AuthMiddleware

__all__ = ["LoggingMiddleware", "AuthMiddleware"]
