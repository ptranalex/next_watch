"""
Backend API client for BFF service.

This module provides backward compatibility by importing the refactored client components.
The original large BackendClient class has been split into focused, specialized clients:

- BaseBackendClient: Core HTTP functionality
- MoviesClient: Movie operations (get_movie, search_movies, etc.)
- UserInteractionsClient: User interaction operations (watchlist, liked, watched)
- ContentDiscoveryClient: Content discovery (genres, actors)
- BackendClient: Unified facade combining all specialized clients

The public API remains exactly the same for backward compatibility.
"""

***REMOVED*** Import all classes from the refactored clients module
from .clients import (
    BackendClient,
    BackendClientError,
    BaseBackendClient,
    MoviesClient,
    UserInteractionsClient,
    ContentDiscoveryClient,
)

***REMOVED*** Maintain backward compatibility - export the main client and error class
__all__ = ["BackendClient", "BackendClientError"]
