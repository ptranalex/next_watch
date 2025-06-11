"""Facade client that combines all specialized backend clients."""

import logging
from typing import Dict, List, Optional, Any

from bff_api.config.app import Config

from .movies import MoviesClient
from .user_interactions import UserInteractionsClient
from .content_discovery import ContentDiscoveryClient

logger = logging.getLogger(__name__)


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

    def __init__(self, config: Config):
        """Initialize the unified backend client.

        Args:
            config: Configuration instance
        """
        ***REMOVED*** Initialize all parent classes with the same config
        super().__init__(config)
        logger.info("Initialized unified BackendClient with all specialized clients")

    async def close(self) -> None:
        """Close all HTTP clients."""
        ***REMOVED*** Only need to call close once since all parents share the same _client
        await super().close()
        logger.info("Closed BackendClient connections")
