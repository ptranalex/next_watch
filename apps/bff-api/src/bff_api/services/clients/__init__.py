"""Backend API clients for BFF service."""

from .base import BaseBackendClient, BackendClientError
from .movies import MoviesClient
from .user_interactions import UserInteractionsClient
from .content_discovery import ContentDiscoveryClient
from .facade import BackendClient

__all__ = [
    "BackendClient",
    "BaseBackendClient",
    "MoviesClient",
    "UserInteractionsClient",
    "ContentDiscoveryClient",
    "BackendClientError",
]
