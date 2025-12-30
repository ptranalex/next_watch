"""
Search service for handling search operations.

This service provides self-contained search functionality using Redis-based indices.
It does NOT make real-time calls to Backend API during search operations.
All data should be precomputed and stored in Redis via CLI commands.
"""

from typing import Any

from config.logging import get_logger
from fast_core.errors import optional_service_handler

from search_api.config.app import SearchAPIConfig
from search_api.schemas import (
    SearchResponse,
    SearchResult,
    Suggestion,
    SuggestionsResponse,
    TextSuggestion,
    TextSuggestionsResponse,
)
from search_api.services.exceptions import SearchServiceException
from search_api.services.suggestion_engine import SuggestionEngine

logger = get_logger(__name__)


class SearchService:
    """Main search service for handling search operations."""

    def __init__(self, config: SearchAPIConfig):
        self.config = config
        # Remove backend_client - Search API should be self-contained
        # Initialize Redis-backed suggestion engine
        self.suggestion_engine = SuggestionEngine(
            redis_url=config.redis_url,
            max_connections=config.redis_max_connections,
            suggestion_key_prefix=config.redis_suggestion_key_prefix,
            entity_key_prefix=config.redis_entity_key_prefix,
            search_result_prefix=config.redis_search_result_prefix,
            suggestion_cache_ttl=config.suggestion_cache_ttl,
            substring_min_length=config.suggestion_substring_min_len,
            substring_time_budget_ms=config.suggestion_substring_budget_ms,
            substring_scan_page_limit=config.suggestion_substring_scan_pages,
        )

    @optional_service_handler(
        service_name="redis-search",
        logger=logger,
        fallback_value={
            "movies": [],
            "total": 0,
            "page": 1,
            "per_page": 20,
            "has_next": False,
            "has_prev": False,
        },
    )
    async def search_movies(
        self,
        query: str,
        page: int = 1,
        limit: int = 20,
        genre_id: int | None = None,
        actor_id: int | None = None,
        sort_by: str = "title",
        sort_desc: bool = False,
        imdb_rating: float | None = None,
        rotten_tomatoes_rating: int | None = None,
        metacritic_rating: int | None = None,
        year: int | None = None,
        start_year: int | None = None,
        end_year: int | None = None,
    ) -> dict[str, Any]:
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
            Search results with movies data from Redis (graceful fallback if Redis unavailable)

        Note:
            Uses graceful degradation - returns empty results if Redis is unavailable
            instead of failing the entire search operation.
        """
        # Validate inputs
        if not query or not query.strip():
            raise SearchServiceException("Search query cannot be empty")

        if page < 1:
            raise SearchServiceException("Page number must be >= 1")

        if limit < 1 or limit > self.config.max_suggestions:
            raise SearchServiceException(
                f"Limit must be between 1 and {self.config.max_suggestions}"
            )

        # Apply search-specific limits
        search_limit = min(limit, self.config.max_suggestions)

        logger.info(
            f"Searching movies in Redis: query='{query}', page={page}, limit={search_limit}"
        )

        # Initialize Redis connection if not already done
        await self.suggestion_engine.initialize()

        # Use suggestion engine to search for movies
        movie_suggestions = await self.suggestion_engine.get_ranked_suggestions(
            query=query.strip(),
            limit=search_limit * 3,  # Get more to allow filtering
            fallback_to_fuzzy=True,
        )

        # Filter to movies only
        movies = [s for s in movie_suggestions if s.get("type") == "movie"]

        # Apply pagination
        start_idx = (page - 1) * search_limit
        end_idx = start_idx + search_limit
        paginated_movies = movies[start_idx:end_idx]

        # Convert to expected response format
        results = []
        for movie in paginated_movies:
            movie_result = {
                "id": movie.get("id", 0),
                "title": movie.get("text", ""),
                "release_year": movie.get("year"),
                "poster_url": movie.get("image_path"),
                "vote_average": movie.get("additional_info", {}).get("vote_average"),
                "popularity": movie.get("popularity"),
                "overview": movie.get("additional_info", {}).get("overview"),
                "genres": movie.get("additional_info", {}).get("genres", []),
                "imdb_rating": movie.get("additional_info", {}).get("imdb_rating"),
                "runtime": movie.get("additional_info", {}).get("runtime"),
            }
            results.append(movie_result)

        # Calculate pagination info
        total = len(movies)
        total_pages = (total + search_limit - 1) // search_limit if total > 0 else 1
        has_next = page < total_pages
        has_prev = page > 1

        logger.info(f"Redis movie search completed: {total} total results, {len(results)} returned")

        return {
            "movies": results,
            "total": total,
            "page": page,
            "per_page": search_limit,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
        }

    @optional_service_handler(
        service_name="redis-suggestions",
        logger=logger,
        fallback_value=SuggestionsResponse(suggestions=[], total=0),
    )
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
            Suggestions response from Redis (graceful fallback if Redis unavailable)

        Note:
            Uses graceful degradation - returns empty suggestions if Redis is unavailable
            instead of failing the suggestion operation.
        """
        # Validate inputs
        if not query or len(query.strip()) < self.config.min_query_length:
            return SuggestionsResponse(suggestions=[], total=0)

        if len(query) > self.config.max_query_length:
            query = query[: self.config.max_query_length]

        # Apply suggestion-specific limits
        suggestion_limit = min(limit, self.config.max_suggestions)

        logger.info(f"Getting suggestions from Redis: query='{query}', limit={suggestion_limit}")

        # Initialize Redis connection if not already done
        await self.suggestion_engine.initialize()

        # Get enhanced entity suggestions from Redis
        redis_suggestions = await self.suggestion_engine.get_entity_suggestions(
            query=query.strip(),
            limit=suggestion_limit,
        )

        # Convert to our suggestion format
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

    @optional_service_handler(
        service_name="redis-text-suggestions",
        logger=logger,
        fallback_value=TextSuggestionsResponse(suggestions=[], total=0),
    )
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
            Text suggestions response from Redis (graceful fallback if Redis unavailable)

        Note:
            Uses graceful degradation - returns empty suggestions if Redis is unavailable
            instead of failing the suggestion operation.
        """
        # Validate inputs
        if not query or len(query.strip()) < self.config.min_query_length:
            return TextSuggestionsResponse(suggestions=[], total=0)

        if len(query) > self.config.max_query_length:
            query = query[: self.config.max_query_length]

        # Apply suggestion-specific limits
        suggestion_limit = min(limit, self.config.max_suggestions)

        logger.info(
            f"Getting text suggestions from Redis: query='{query}', limit={suggestion_limit}"
        )

        # Initialize Redis connection if not already done
        await self.suggestion_engine.initialize()

        # Get ranked entity suggestions from Redis
        redis_suggestions = await self.suggestion_engine.get_ranked_suggestions(
            query=query.strip(),
            limit=suggestion_limit,
            fallback_to_fuzzy=True,
        )

        # Convert to our TextSuggestion format
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

    @optional_service_handler(
        service_name="redis-multi-search",
        logger=logger,
        fallback_value=SearchResponse(
            suggestions=[],
            total=0,
            page=1,
            per_page=20,
            total_pages=1,
            has_next=False,
            has_prev=False,
        ),
    )
    async def search_all_entities(
        self,
        query: str,
        page: int = 1,
        limit: int = 20,
        types: list[str] | None = None,
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
            Multi-entity search response from Redis (graceful fallback if Redis unavailable)

        Note:
            Uses graceful degradation - returns empty results if Redis is unavailable
            instead of failing the search operation.
        """
        # Validate inputs
        if not query or not query.strip():
            raise SearchServiceException("Search query cannot be empty")

        if page < 1:
            raise SearchServiceException("Page number must be >= 1")

        if limit < 1 or limit > self.config.max_suggestions:
            raise SearchServiceException(
                f"Limit must be between 1 and {self.config.max_suggestions}"
            )

        # Apply search-specific limits
        search_limit = min(limit, self.config.max_suggestions)

        logger.info(
            f"Searching all entities in Redis: query='{query}', page={page}, limit={search_limit}, types={types}"
        )

        # Initialize Redis connection if not already done
        await self.suggestion_engine.initialize()

        # Get suggestions from Redis
        all_suggestions = await self.suggestion_engine.get_ranked_suggestions(
            query=query.strip(),
            limit=search_limit * 5,  # Get more to allow filtering and pagination
            fallback_to_fuzzy=True,
        )

        # Filter by types if specified
        if types:
            filtered_suggestions = [s for s in all_suggestions if s.get("type") in types]
        else:
            filtered_suggestions = all_suggestions

        # Apply pagination
        start_idx = (page - 1) * search_limit
        end_idx = start_idx + search_limit
        paginated_suggestions = filtered_suggestions[start_idx:end_idx]

        # Convert to SearchResult format
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

        # Calculate pagination info
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
