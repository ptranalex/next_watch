"""
Backend API client for Recommendation service.

This module provides the main interface for communicating with the backend-api service.
The implementation follows the same proven patterns as BFF-API.

The backend client is organized as:
- BaseBackendClient: Core HTTP functionality with retry logic
- MoviesClient: Movie-related operations
- BackendClient: Unified facade (this file provides the public interface)

Usage:
    from recommendation_api.services.backend_client import BackendClient, BackendClientError

    client = BackendClient()
    movie = await client.get_movie(123)
"""

# Import all classes from the internal clients module
from recommendation_api.services.clients.backend_client import BackendClient
from recommendation_api.services.clients.base import BackendClientError

# Global backend client instance
_backend_client: BackendClient | None = None


def get_backend_client() -> BackendClient:
    """Get or create a global backend client instance.

    Returns:
        BackendClient instance
    """
    global _backend_client

    if _backend_client is None:
        _backend_client = BackendClient()

    return _backend_client


async def close_backend_client() -> None:
    """Close the global backend client."""
    global _backend_client

    if _backend_client is not None:
        await _backend_client.close()
        _backend_client = None


# Maintain clean public API
__all__ = ["BackendClient", "BackendClientError", "get_backend_client", "close_backend_client"]
