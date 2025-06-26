"""Search service for Search API.

This module provides the main search service that orchestrates
search operations, caching, and result formatting.
"""

from typing import Any, Dict, List, Optional

from config.logging import get_logger

from search_api.config.app import SearchAPIConfig
from search_api.services.backend_client import BackendAPIClient, BackendAPIException
from search_api.services.suggestion_engine import SuggestionEngine
from search_api.schemas.search import (
    SearchResponse,
    Suggestion,
    SuggestionsResponse,
    TextSuggestion,
    TextSuggestionsResponse,
)

logger = get_logger(__name__)


class SearchServiceException(Exception):
    """Exception raised by the Search Service."""

    pass


class SearchService:
    """Main search service for handling search operations."""

    def __init__(self, config: SearchAPIConfig):
        self.config = config
        self.backend_client = BackendAPIClient(config)
        ***REMOVED*** Initialize Redis-backed suggestion engine
        self.suggestion_engine = SuggestionEngine(redis_url=config.redis_url, pool_size=10)

    async def search_movies(
        self,
        query: str,
        page: int = 1,
        limit: int = 20,
        genre_id: Optional[int] = None,
        actor_id: Optional[int] = None,
        sort_by: str = "title",
        sort_desc: bool = False,
        imdb_rating: Optional[float] = None,
        rotten_tomatoes_rating: Optional[int] = None,
        metacritic_rating: Optional[int] = None,
        year: Optional[int] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Search movies with comprehensive filtering.

        Args:
            query: Search query string
            page: Page number for pagination
            limit: Number of results per page
            genre_id: Optional genre filter
            actor_id: Optional actor filter (TMDB ID)
            sort_by: Field to sort by
            sort_desc: Sort in descending order
            imdb_rating: Minimum IMDb rating filter
            rotten_tomatoes_rating: Minimum RT rating filter
            metacritic_rating: Minimum Metacritic rating filter
            year: Release year filter
            start_year: Start year filter (inclusive)
            end_year: End year filter (inclusive)

        Returns:
            Search results with movies data

        Raises:
            SearchServiceException: If search operation fails
        """
        try:
            ***REMOVED*** Validate inputs
            if not query or not query.strip():
                raise SearchServiceException("Search query cannot be empty")

            if page < 1:
                raise SearchServiceException("Page number must be >= 1")

            if limit < 1 or limit > self.config.max_suggestions:
                raise SearchServiceException(
                    f"Limit must be between 1 and {self.config.max_suggestions}"
                )

            ***REMOVED*** Apply search-specific limits
            search_limit = min(limit, self.config.max_suggestions)

            logger.info(f"Searching movies: query='{query}', page={page}, limit={search_limit}")

            ***REMOVED*** Call Backend API for movie search
            result = await self.backend_client.search_movies(
                query=query.strip(),
                page=page,
                limit=search_limit,
                genre_id=genre_id,
                actor_id=actor_id,
                sort_by=sort_by,
                sort_desc=sort_desc,
                imdb_rating=imdb_rating,
                rotten_tomatoes_rating=rotten_tomatoes_rating,
                metacritic_rating=metacritic_rating,
                year=year,
                start_year=start_year,
                end_year=end_year,
            )

            ***REMOVED*** Add search metadata
            if isinstance(result, dict):
                result["search_metadata"] = {
                    "query": query.strip(),
                    "search_type": "movie",
                    "cached": False,  ***REMOVED*** TODO: Implement caching
                    "response_time_ms": None,  ***REMOVED*** TODO: Add timing
                }

            logger.info(f"Movie search completed: {result.get('total', 0)} results found")
            return result

        except BackendAPIException as e:
            logger.error(f"Backend API error during movie search: {e}")
            raise SearchServiceException(f"Search backend unavailable: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during movie search: {e}")
            raise SearchServiceException(f"Search operation failed: {e}")

    async def get_suggestions(
        self,
        query: str,
        limit: int = 10,
    ) -> SuggestionsResponse:
        """Get search suggestions across all entity types.

        Args:
            query: Search query string
            limit: Maximum number of suggestions

        Returns:
            Suggestions response

        Raises:
            SearchServiceException: If suggestion operation fails
        """
        try:
            ***REMOVED*** Validate inputs
            if not query or len(query.strip()) < self.config.min_query_length:
                return SuggestionsResponse(suggestions=[], total=0)

            if len(query) > self.config.max_query_length:
                query = query[: self.config.max_query_length]

            ***REMOVED*** Apply suggestion-specific limits
            suggestion_limit = min(limit, self.config.max_suggestions)

            logger.info(f"Getting suggestions: query='{query}', limit={suggestion_limit}")

            ***REMOVED*** Try Redis-backed suggestions first
            try:
                ***REMOVED*** Initialize Redis connection if not already done
                await self.suggestion_engine.initialize()

                ***REMOVED*** Get enhanced entity suggestions from Redis
                redis_suggestions = await self.suggestion_engine.get_entity_suggestions(
                    query=query.strip(),
                    limit=suggestion_limit,
                )

                ***REMOVED*** Convert to our suggestion format
                suggestions_data = []
                for i, sugg in enumerate(redis_suggestions):
                    suggestion_obj = Suggestion(
                        id=sugg.get("id", i),
                        name=sugg.get("text", ""),
                        type=sugg.get("type", "movie"),
                        image_path=sugg.get("image_path"),
                    )
                    suggestions_data.append(suggestion_obj)

                total = len(suggestions_data)

                response = SuggestionsResponse(suggestions=suggestions_data, total=total)

                logger.info(f"Redis suggestions completed: {total} suggestions found")

            except Exception as redis_error:
                logger.warning(f"Redis suggestions failed, falling back to backend: {redis_error}")

                ***REMOVED*** Fallback to Backend API
                result = await self.backend_client.get_search_suggestions(
                    query=query.strip(),
                    limit=suggestion_limit,
                )

                ***REMOVED*** Convert to our response model
                suggestions_data = result.get("suggestions", [])
                total = result.get("total", len(suggestions_data))

                response = SuggestionsResponse(suggestions=suggestions_data, total=total)

                logger.info(f"Backend suggestions completed: {total} suggestions found")
            return response

        except BackendAPIException as e:
            logger.error(f"Backend API error during suggestions: {e}")
            raise SearchServiceException(f"Suggestions backend unavailable: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during suggestions: {e}")
            raise SearchServiceException(f"Suggestions operation failed: {e}")

    async def get_text_suggestions(
        self,
        query: str,
        limit: int = 10,
    ) -> TextSuggestionsResponse:
        """Get enhanced text-based suggestions.

        Args:
            query: Search query prefix
            limit: Maximum number of suggestions

        Returns:
            Text suggestions response

        Raises:
            SearchServiceException: If suggestion operation fails
        """
        try:
            ***REMOVED*** Validate inputs
            if not query or len(query.strip()) < self.config.min_query_length:
                return TextSuggestionsResponse(suggestions=[], total=0)

            if len(query) > self.config.max_query_length:
                query = query[: self.config.max_query_length]

            ***REMOVED*** Apply suggestion-specific limits
            suggestion_limit = min(limit, self.config.max_suggestions)

            logger.info(f"Getting text suggestions: query='{query}', limit={suggestion_limit}")

            ***REMOVED*** Try Redis-backed ranked suggestions first
            try:
                ***REMOVED*** Initialize Redis connection if not already done
                await self.suggestion_engine.initialize()

                ***REMOVED*** Get ranked entity suggestions from Redis
                redis_suggestions = await self.suggestion_engine.get_ranked_suggestions(
                    query=query.strip(),
                    limit=suggestion_limit,
                    fallback_to_fuzzy=True,
                )

                ***REMOVED*** Convert to our TextSuggestion format
                suggestions_data = []
                for sugg in redis_suggestions:
                    suggestion_obj = TextSuggestion(
                        text=sugg.get("text", ""),
                        type=sugg.get("type", "movie"),
                        id=sugg.get("id"),
                        image_path=sugg.get("image_path"),
                        year=sugg.get("year"),
                        popularity=sugg.get("popularity"),
                        is_partial=sugg.get("is_partial", False),
                        search_type=sugg.get("search_type", "unknown"),
                        additional_info=sugg.get("additional_info", {}),
                    )
                    suggestions_data.append(suggestion_obj)

                total = len(suggestions_data)

                response = TextSuggestionsResponse(suggestions=suggestions_data, total=total)

                logger.info(f"Redis text suggestions completed: {total} suggestions found")

            except Exception as redis_error:
                logger.warning(
                    f"Redis text suggestions failed, falling back to backend: {redis_error}"
                )

                ***REMOVED*** Fallback to Backend API
                result = await self.backend_client.get_text_suggestions(
                    query=query.strip(),
                    limit=suggestion_limit,
                )

                ***REMOVED*** Convert to our response model
                suggestions_data = result.get("suggestions", [])
                total = result.get("total", len(suggestions_data))

                response = TextSuggestionsResponse(suggestions=suggestions_data, total=total)

                logger.info(f"Backend text suggestions completed: {total} suggestions found")
            return response

        except BackendAPIException as e:
            logger.error(f"Backend API error during text suggestions: {e}")
            raise SearchServiceException(f"Text suggestions backend unavailable: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during text suggestions: {e}")
            raise SearchServiceException(f"Text suggestions operation failed: {e}")

    async def search_all_entities(
        self,
        query: str,
        page: int = 1,
        limit: int = 20,
        types: Optional[List[str]] = None,
    ) -> SearchResponse:
        """Search across all entity types (movies, actors, directors).

        Args:
            query: Search query string
            page: Page number for pagination
            limit: Number of results per page
            types: Optional list of entity types to include

        Returns:
            Multi-entity search response

        Raises:
            SearchServiceException: If search operation fails
        """
        try:
            ***REMOVED*** Validate inputs
            if not query or not query.strip():
                raise SearchServiceException("Search query cannot be empty")

            if page < 1:
                raise SearchServiceException("Page number must be >= 1")

            if limit < 1 or limit > self.config.max_suggestions:
                raise SearchServiceException(
                    f"Limit must be between 1 and {self.config.max_suggestions}"
                )

            ***REMOVED*** Apply search-specific limits
            search_limit = min(limit, self.config.max_suggestions)

            logger.info(
                f"Searching all entities: query='{query}', page={page}, limit={search_limit}, types={types}"
            )

            ***REMOVED*** Call Backend API for multi-entity search
            result = await self.backend_client.search_all_entities(
                query=query.strip(),
                page=page,
                limit=search_limit,
                types=types,
            )

            ***REMOVED*** Convert to our response model
            suggestions_data = result.get("suggestions", [])
            total = result.get("total", 0)
            per_page = result.get("per_page", search_limit)
            total_pages = result.get("total_pages", 0)
            has_next = result.get("has_next", False)
            has_prev = result.get("has_prev", False)

            response = SearchResponse(
                suggestions=suggestions_data,
                total=total,
                page=page,
                per_page=per_page,
                total_pages=total_pages,
                has_next=has_next,
                has_prev=has_prev,
            )

            logger.info(f"Multi-entity search completed: {total} results found")
            return response

        except BackendAPIException as e:
            logger.error(f"Backend API error during multi-entity search: {e}")
            raise SearchServiceException(f"Search backend unavailable: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during multi-entity search: {e}")
            raise SearchServiceException(f"Search operation failed: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Check the health of search service dependencies.

        Returns:
            Health status information
        """
        try:
            ***REMOVED*** Check Backend API health
            backend_health = await self.backend_client.health_check()

            ***REMOVED*** Check Redis suggestion engine health
            redis_health = await self.suggestion_engine.health_check()

            return {
                "search_service": "healthy",
                "backend_api": backend_health.get("status", "unknown"),
                "redis_cache": redis_health.get("status", "unknown"),
                "features": {
                    "movie_search": True,
                    "suggestions": True,
                    "text_suggestions": True,
                    "multi_entity_search": True,
                    "redis_caching": redis_health.get("status") == "healthy",
                    "enhanced_suggestions": redis_health.get("status") == "healthy",
                },
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "search_service": "unhealthy",
                "backend_api": "unknown",
                "redis_cache": "unknown",
                "error": str(e),
                "features": {
                    "movie_search": False,
                    "suggestions": False,
                    "text_suggestions": False,
                    "multi_entity_search": False,
                    "redis_caching": False,
                    "enhanced_suggestions": False,
                },
            }
