"""HTTP service clients for FastAPI applications.

This module provides utilities for making HTTP requests to external services
with consistent configuration, versioning, and error handling.
"""

from .service_client import ServiceClient, ServiceConfig

__all__ = [
    "ServiceClient",
    "ServiceConfig",
]
