"""
Search service for handling search operations.

This service provides self-contained search functionality using Redis-based indices.
It does NOT make real-time calls to Backend API during search operations.
All data should be precomputed and stored in Redis via CLI commands.
"""

import asyncio
from typing import Any, Dict, List, Optional

from config.logging import get_logger

from search_api.config.app import SearchAPIConfig
from search_api.schemas.search import (
    SearchResponse,
    SearchResult,
    Suggestion,
    SuggestionsResponse,
    TextSuggestion,
    TextSuggestionsResponse,
)
from search_api.services.suggestion_engine import SuggestionEngine

logger = get_logger(__name__)


class SearchServiceException(Exception):
    """Exception raised when search operations fail."""

    pass


class SearchService:
    """Main search service for handling search operations."""

    def __init__(self, config: SearchAPIConfig):
        self.config = config
        ***REMOVED*** Remove backend_client - Search API should be self-contained
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
        """Search movies using Redis-based search index.

        This method searches movies from precomputed Redis indices only.
        It does NOT call Backend API during search operations.

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
            Search results with movies data from Redis

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
                f"Searching movies in Redis: query='{query}', page={page}, limit={search_limit}"
            )

            ***REMOVED*** Initialize Redis connection if not already done
            await self.suggestion_engine.initialize()

            ***REMOVED*** Use suggestion engine to search for movies
            movie_suggestions = await self.suggestion_engine.get_ranked_suggestions(
                query=query.strip(),
                limit=search_limit * 3,  ***REMOVED*** Get more to allow filtering
                fallback_to_fuzzy=True,
            )

            ***REMOVED*** Filter to movies only
            movies = [s for s in movie_suggestions if s.get("type") == "movie"]

            ***REMOVED*** Apply pagination
            start_idx = (page - 1) * search_limit
            end_idx = start_idx + search_limit
            paginated_movies = movies[start_idx:end_idx]

            ***REMOVED*** Convert to expected response format
            results = []
            for movie in paginated_movies:
                movie_data = {
                    "id": movie.get("id"),
                    "title": movie.get("text"),
                    "overview": movie.get("additional_info", {}).get("overview"),
                    "release_date": movie.get("additional_info", {}).get("release_date"),
                    "poster_url": movie.get("image_path"),
                    "backdrop_url": movie.get("additional_info", {}).get("backdrop_url"),
                    "vote_average": movie.get("additional_info", {}).get("vote_average"),
                    "popularity": movie.get("popularity"),
                    "imdb_rating": movie.get("additional_info", {}).get("imdb_rating"),
                    "runtime": movie.get("additional_info", {}).get("runtime"),
                    "genres": movie.get("additional_info", {}).get("genres", []),
                }
                results.append(movie_data)

            ***REMOVED*** Calculate pagination info
            total = len(movies)
            total_pages = (total + search_limit - 1) // search_limit
            has_next = page < total_pages
            has_prev = page > 1

            response = {
                "results": results,
                "total": total,
                "page": page,
                "per_page": search_limit,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev,
                "search_metadata": {
                    "query": query.strip(),
                    "search_type": "movie",
                    "cached": True,
                    "source": "redis_index",
                },
            }

            logger.info(
                f"Redis movie search completed: {total} total movies, {len(results)} returned"
            )
            return response

        except Exception as e:
            logger.error(f"Error during Redis movie search: {e}")
            raise SearchServiceException(f"Movie search operation failed: {e}")

    async def get_suggestions(
        self,
        query: str,
        limit: int = 10,
    ) -> SuggestionsResponse:
        """Get search suggestions from Redis index only.

        This method gets suggestions from precomputed Redis indices only.
        It does NOT call Backend API during suggestion operations.

        Args:
            query: Search query string
            limit: Maximum number of suggestions

        Returns:
            Suggestions response from Redis

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

            logger.info(
                f"Getting suggestions from Redis: query='{query}', limit={suggestion_limit}"
            )

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
            return response

        except Exception as e:
            logger.error(f"Error during Redis suggestions: {e}")
            raise SearchServiceException(f"Suggestions operation failed: {e}")

    async def get_text_suggestions(
        self,
        query: str,
        limit: int = 10,
    ) -> TextSuggestionsResponse:
        """Get enhanced text-based suggestions from Redis index only.

        This method gets text suggestions from precomputed Redis indices only.
        It does NOT call Backend API during suggestion operations.

        Args:
            query: Search query prefix
            limit: Maximum number of suggestions

        Returns:
            Text suggestions response from Redis

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

            logger.info(
                f"Getting text suggestions from Redis: query='{query}', limit={suggestion_limit}"
            )

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
            return response

        except Exception as e:
            logger.error(f"Error during Redis text suggestions: {e}")
            raise SearchServiceException(f"Text suggestions operation failed: {e}")

    async def search_all_entities(
        self,
        query: str,
        page: int = 1,
        limit: int = 20,
        types: Optional[List[str]] = None,
    ) -> SearchResponse:
        """Search across all entity types using Redis index only.

        This method searches all entities from precomputed Redis indices only.
        It does NOT call Backend API during search operations.

        Args:
            query: Search query string
            page: Page number for pagination
            limit: Number of results per page
            types: Optional list of entity types to include

        Returns:
            Multi-entity search response from Redis

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
                f"Searching all entities in Redis: query='{query}', page={page}, limit={search_limit}, types={types}"
            )

            ***REMOVED*** Initialize Redis connection if not already done
            await self.suggestion_engine.initialize()

            ***REMOVED*** Get suggestions from Redis
            all_suggestions = await self.suggestion_engine.get_ranked_suggestions(
                query=query.strip(),
                limit=search_limit * 5,  ***REMOVED*** Get more to allow filtering and pagination
                fallback_to_fuzzy=True,
            )

            ***REMOVED*** Filter by types if specified
            if types:
                filtered_suggestions = [s for s in all_suggestions if s.get("type") in types]
            else:
                filtered_suggestions = all_suggestions

            ***REMOVED*** Apply pagination
            start_idx = (page - 1) * search_limit
            end_idx = start_idx + search_limit
            paginated_suggestions = filtered_suggestions[start_idx:end_idx]

            ***REMOVED*** Convert to SearchResult format
            suggestions_data = []
            for sugg in paginated_suggestions:
                suggestion_obj = SearchResult(
                    id=sugg.get("id", 0),
                    name=sugg.get("text", ""),
                    type=sugg.get("type", "unknown"),
                    image_path=sugg.get("image_path"),
                    year=sugg.get("year"),
                    popularity=sugg.get("popularity"),
                    additional_info=sugg.get("additional_info"),
                )
                suggestions_data.append(suggestion_obj)

            ***REMOVED*** Calculate pagination info
            total = len(filtered_suggestions)
            total_pages = (total + search_limit - 1) // search_limit
            has_next = page < total_pages
            has_prev = page > 1

            response = SearchResponse(
                suggestions=suggestions_data,
                total=total,
                page=page,
                per_page=search_limit,
                total_pages=total_pages,
                has_next=has_next,
                has_prev=has_prev,
            )

            logger.info(
                f"Redis multi-entity search completed: {total} total results, {len(suggestions_data)} returned"
            )
            return response

        except Exception as e:
            logger.error(f"Error during Redis multi-entity search: {e}")
            raise SearchServiceException(f"Multi-entity search operation failed: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the search service.

        Only checks Redis health since we don't use Backend API during search.

        Returns:
            Health status information
        """
        try:
            ***REMOVED*** Check Redis suggestion engine health only
            redis_health = await self.suggestion_engine.health_check()

            return {
                "search_service": "healthy",
                "redis_cache": redis_health.get("status", "unknown"),
                "features": {
                    "movie_search": redis_health.get("status") == "healthy",
                    "suggestions": redis_health.get("status") == "healthy",
                    "text_suggestions": redis_health.get("status") == "healthy",
                    "multi_entity_search": redis_health.get("status") == "healthy",
                    "redis_caching": redis_health.get("status") == "healthy",
                    "enhanced_suggestions": redis_health.get("status") == "healthy",
                },
                "data_sources": {
                    "redis_index": redis_health.get("status", "unknown"),
                    "precomputed_data": True,
                    "real_time_backend_calls": False,  ***REMOVED*** Explicitly false
                },
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "search_service": "unhealthy",
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
                "data_sources": {
                    "redis_index": "unknown",
                    "precomputed_data": False,
                    "real_time_backend_calls": False,
                },
            }
