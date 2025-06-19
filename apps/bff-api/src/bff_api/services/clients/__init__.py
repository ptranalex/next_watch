"""Backend API clients for BFF service."""

from .base import BackendClientError, BaseBackendClient
from .content_discovery import ContentDiscoveryClient
from .facade import BackendClient
from .movies import MoviesClient
from .user_interactions import UserInteractionsClient

__all__ = [
    "BackendClient",
    "BaseBackendClient",
    "MoviesClient",
    "UserInteractionsClient",
    "ContentDiscoveryClient",
    "BackendClientError",
]
