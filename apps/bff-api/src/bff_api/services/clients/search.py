"""Search API client for BFF service.

This client handles communication with the dedicated Search API service
for search suggestions and related operations.
"""

from typing import Any

from config.logging import get_logger
from fast_core.dependencies.client_factory import ServiceClientConfig
from fast_core.errors import (
    ValidationException,
    service_error_handler,
)
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .base import BackendClientTransientError, BaseBackendClient

logger = get_logger(__name__)


class SearchAPIClient(BaseBackendClient):
    """HTTP client for communicating with Search API service.

    Extends BaseBackendClient with Search API-specific methods and configurations.
    """

    def __init__(
        self, config: ServiceClientConfig, bff_config: Any | None = None
    ) -> None:
        """Initialize Search API client."""
        super().__init__(config, bff_config)
        ***REMOVED*** Override service name for proper error attribution
        self.service_name = "search-api"

    @service_error_handler("search-api", logger)
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(BackendClientTransientError),
    )
    async def _make_request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make HTTP request with Search API-specific error handling.

        This method is needed because @service_error_handler uses hardcoded service names.
        All other logic is identical to BaseBackendClient._make_request.
        """
        ***REMOVED*** Delegate to parent implementation, which handles all the HTTP logic
        return await super()._make_request(method, path, params, data, headers)

    @service_error_handler("search-api", logger, "get_suggestions")
    async def get_suggestions(
        self,
        query: str,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Get basic search suggestions from Search API.

        Args:
            query: Search query string
            limit: Maximum number of suggestions to return

        Returns:
            Basic suggestions response

        Raises:
            ValidationException: If parameters are invalid
            ExternalServiceException: If Search API is unavailable
        """
        ***REMOVED*** Validate parameters
        if not query or not query.strip():
            raise ValidationException("Search query cannot be empty")
        if limit <= 0 or limit > 50:
            raise ValidationException("Limit must be between 1 and 50")

        logger.debug(
            "Fetching basic suggestions from Search API",
            query=query,
            limit=limit,
            service="bff",
            component="search_client",
        )

        response = await self._make_request(
            "GET",
            self._build_api_path("/search/suggestions"),
            params={
                "query": query.strip(),
                "limit": limit,
            },
        )

        logger.debug(
            "Successfully fetched basic suggestions",
            total=response.get("total", 0),
            query=query,
            service="bff",
            component="search_client",
        )

        return response

    @service_error_handler("search-api", logger, "get_text_suggestions")
    async def get_text_suggestions(
        self,
        query: str,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Get enhanced text-based suggestions from Search API.

        Args:
            query: Search query prefix
            limit: Maximum number of suggestions to return

        Returns:
            Enhanced text suggestions with rich metadata

        Raises:
            ValidationException: If parameters are invalid
            ExternalServiceException: If Search API is unavailable
        """
        ***REMOVED*** Validate parameters
        if not query or not query.strip():
            raise ValidationException("Search query cannot be empty")
        if limit <= 0 or limit > 50:
            raise ValidationException("Limit must be between 1 and 50")

        logger.debug(
            "Fetching text suggestions from Search API",
            query=query,
            limit=limit,
            service="bff",
            component="search_client",
        )

        response = await self._make_request(
            "GET",
            self._build_api_path("/search/suggestions/text"),
            params={
                "query": query.strip(),
                "limit": limit,
            },
        )

        logger.debug(
            "Successfully fetched text suggestions",
            total=response.get("total", 0),
            query=query,
            service="bff",
            component="search_client",
        )

        return response

    @service_error_handler("search-api", logger, "search_all_entities")
    async def search_all_entities(
        self,
        query: str,
        page: int = 1,
        limit: int = 20,
        types: list[str] | None = None,
    ) -> dict[str, Any]:
        """Search across all entity types through Search API.

        Args:
            query: Search query string
            page: Page number for pagination
            limit: Number of results per page
            types: Optional list of entity types to include

        Returns:
            Multi-entity search results

        Raises:
            ValidationException: If parameters are invalid
            ExternalServiceException: If Search API is unavailable
        """
        ***REMOVED*** Validate parameters
        if not query or not query.strip():
            raise ValidationException("Search query cannot be empty")
        if page <= 0:
            raise ValidationException("Page number must be a positive integer")
        if limit <= 0 or limit > 100:
            raise ValidationException("Limit must be between 1 and 100")

        logger.debug(
            "Searching all entities through Search API",
            query=query,
            page=page,
            limit=limit,
            types=types,
            service="bff",
            component="search_client",
        )

        params: dict[str, str | int | list[str]] = {
            "query": query.strip(),
            "page": page,
            "limit": limit,
        }

        if types:
            params["types"] = types

        response = await self._make_request(
            "GET",
            self._build_api_path("/search/all"),
            params=params,
        )

        logger.debug(
            "Successfully searched all entities",
            total=response.get("total", 0),
            page=page,
            query=query,
            service="bff",
            component="search_client",
        )

        return response

    async def health_check(self) -> dict[str, Any]:
        """Check the health of the Search API service.

        Returns:
            Health status information

        Raises:
            ExternalServiceException: If Search API is unavailable
        """
        try:
            logger.debug(
                "Checking Search API health",
                service="bff",
                component="search_client",
            )

            response = await self._make_request("GET", "/health")

            logger.debug(
                "Search API health check successful",
                status=response.get("status", "unknown"),
                search_service=response.get("service", "unknown"),
                service="bff",
                component="search_client",
            )

            ***REMOVED*** Return response with URL included for consistency with fast-core health checks
            return {
                "service": self.name,
                "status": "healthy",
                "url": self.base_url,
                **response,
            }

        except Exception as e:
            logger.error(
                "Search API health check failed",
                error=str(e),
                service="bff",
                component="search_client",
                exc_info=True,
            )
            return {
                "service": self.name,
                "status": "error",
                "error": str(e),
                "url": self.base_url,
            }
