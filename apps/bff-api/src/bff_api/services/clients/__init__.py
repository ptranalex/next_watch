"""Backend API clients for BFF service."""

from .base import BaseBackendClient
from .content_discovery import ContentDiscoveryClient
from .facade import BackendClient
from .movies import MoviesClient
from .recommendation import RecommendationClient
from .user_interactions import UserInteractionsClient

__all__ = [
    "BackendClient",
    "BaseBackendClient",
    "MoviesClient",
    "RecommendationClient",
    "UserInteractionsClient",
    "ContentDiscoveryClient",
]
