"""Facade client that combines all specialized backend clients."""

from config.logging import get_logger
from fast_core.dependencies.client_factory import ServiceClientConfig

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
    Now works with Fast Core's Service Client Factory for better lifecycle management.

    Inherits from:
    - MoviesClient: Movie-related operations (get_movie, search_movies, etc.)
    - UserInteractionsClient: User interaction operations (watchlist, liked, watched)
    - ContentDiscoveryClient: Content discovery (genres, actors)
    """

    def __init__(self, config: ServiceClientConfig, bff_config: BFFAPIConfig | None = None) -> None:
        """Initialize the unified backend client.

        Args:
            config: Service client configuration from Fast Core
            bff_config: BFF-specific configuration (optional, uses global settings if not provided)
        """
        ***REMOVED*** Initialize all parent classes with the new signature
        super().__init__(config, bff_config)

        logger.debug(
            "Initialized unified BackendClient with all specialized clients using Service Client Factory",
            service="bff",
            component="backend_client",
        )

    ***REMOVED*** Inherit close() and health_check() methods from BaseBackendClient (via parents)
