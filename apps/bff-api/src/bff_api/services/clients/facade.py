"""Facade client that combines all specialized backend clients."""

from typing import Any, Dict, List, Optional

from config.logging import get_logger

from bff_api.config.app import BFFAPIConfig
from bff_api.services.clients.content_discovery import ContentDiscoveryClient
from bff_api.services.clients.movies import MoviesClient
from bff_api.services.clients.user_interactions import UserInteractionsClient

logger = get_logger(__name__)


class BackendClient(MoviesClient, UserInteractionsClient, ContentDiscoveryClient):
    """
    Unified backend client that combines all specialized clients.

    This facade provides a single interface to all backend API operations,
    maintaining backward compatibility while internally using specialized clients.

    Inherits from:
    - MoviesClient: Movie-related operations (get_movie, search_movies, etc.)
    - UserInteractionsClient: User interaction operations (watchlist, liked, watched)
    - ContentDiscoveryClient: Content discovery (genres, actors)
    """

    def __init__(self, config: BFFAPIConfig) -> None:
        """Initialize the unified backend client.

        Args:
            config: Configuration instance
        """
        ***REMOVED*** Initialize all parent classes
        super().__init__(config)
        logger.info(
            "Initialized unified BackendClient with all specialized clients",
            service="bff",
            component="backend_client",
        )

    async def close(self) -> None:
        """Close all HTTP clients."""
        ***REMOVED*** Only need to call close once since all parents share the same _client
        await super().close()
        logger.info("Closed BackendClient connections", service="bff", component="backend_client")
