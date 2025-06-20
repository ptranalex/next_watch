"""Backend API clients for Recommendation API service.

This package provides HTTP clients for communicating with the backend-api service.
The architecture is adapted from BFF-API's proven patterns.

Key components:
- BaseBackendClient: Core HTTP functionality with retry logic
- MoviesClient: Movie-related operations
- BackendClient: Unified facade
"""

from recommendation_api.services.clients.backend_client import BackendClient
from recommendation_api.services.clients.base import BackendClientError

__all__ = ["BackendClient", "BackendClientError"]
