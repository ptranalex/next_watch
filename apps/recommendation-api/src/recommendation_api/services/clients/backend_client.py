"""Main backend client facade for recommendation API."""

from config.logging import get_logger

from recommendation_api.services.clients.movies import MoviesClient

logger = get_logger(__name__)


class BackendClient(MoviesClient):
    """
    Unified backend client for recommendation API.

    This facade provides a single interface to all backend API operations,
    currently focused on movie operations for recommendations.

    Inherits from:
    - MoviesClient: Movie-related operations (get_movie, search_movies, etc.)
    """

    def __init__(self):
        """Initialize the unified backend client."""
        super().__init__()
        logger.info("Initialized BackendClient for recommendation API")

    async def close(self) -> None:
        """Close HTTP client connections."""
        await super().close()
        logger.info("Closed BackendClient connections")
