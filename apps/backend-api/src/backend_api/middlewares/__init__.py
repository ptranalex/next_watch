"""
Middleware package for the backend API.

This package contains middlewares for request processing, error handling,
and other cross-cutting concerns.
"""

from backend_api.middlewares.error_handler import ErrorHandlerMiddleware

__all__ = ["ErrorHandlerMiddleware"]
