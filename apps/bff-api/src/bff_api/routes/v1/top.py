"""Top movies routes for BFF API."""

from typing import Any, Dict, Optional, Union, cast

import httpx
from config.logging import get_logger
from fast_core.responses import ResponseBuilder
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from bff_api.dependencies import get_backend_client
from bff_api.services.clients import BackendClient
from bff_api.utils.auth import extract_user_id_from_token

logger = get_logger(__name__)
router = APIRouter(tags=["top"])

***REMOVED*** Initialize response builder for consistent API responses
responses = ResponseBuilder(
    config={
        "pagination": {
            "default_limit": 20,
            "max_limit": 100,
        },
    }
)

***REMOVED*** Security scheme for optional authentication
security = HTTPBearer(auto_error=False)


async def _get_movies(
    backend: BackendClient,
    page: int = 1,
    limit: int = 20,
    **filters: Any,
) -> Dict[str, Any]:
    """Get movies from backend with filters.

    Args:
        backend: Backend client
        page: Page number for pagination
        limit: Number of items per page
        **filters: Additional filter parameters

    Returns:
        Movies response from backend

    Raises:
        ExternalServiceException: If request fails
    """
    return await backend.get_movies(
        page=page,
        limit=limit,
        **filters,
    )


async def _get_user_movie_interaction(
    backend: BackendClient,
    user_id: int,
    movie_id: int,
    jwt_token: str,
) -> Optional[Dict[str, Any]]:
    """Get user's interaction with a specific movie.

    Args:
        backend: Backend client
        user_id: User ID
        movie_id: Movie ID
        jwt_token: JWT token for authentication

    Returns:
        User interaction data or None if not found

    Raises:
        ExternalServiceException: If request fails
    """
    try:
        result = await backend.get_user_movie_interaction(user_id, movie_id, jwt_token)
        return result
    except Exception as e:
        ***REMOVED*** Handle 404 case for not found interactions
        if "404" in str(e):
            return None
        raise


@router.get("/top")
async def get_top_movies(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    genre_id: Optional[int] = Query(None, description="Filter by genre ID"),
    actor_id: Optional[int] = Query(None, description="Filter by actor TMDB ID"),
    sort_by: Optional[str] = Query(
        "imdb_rating",
        description="Sort by field (title, release_date, imdb_rating, rotten_tomatoes_rating, metacritic_rating)",
    ),
    sort_desc: Optional[bool] = Query(True, description="Sort in descending order"),
    imdb_rating: Optional[float] = Query(
        None, ge=0, le=10, description="Filter by minimum IMDb rating"
    ),
    rotten_tomatoes_rating: Optional[int] = Query(
        None, ge=0, le=100, description="Filter by minimum Rotten Tomatoes rating"
    ),
    metacritic_rating: Optional[int] = Query(
        None, ge=0, le=100, description="Filter by minimum Metacritic rating"
    ),
    year: Optional[int] = Query(None, description="Filter by release year"),
    start_year: Optional[int] = Query(None, description="Filter by start year (inclusive)"),
    end_year: Optional[int] = Query(None, description="Filter by end year (inclusive)"),
    backend: BackendClient = Depends(get_backend_client),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """Get top-rated movies with filters.

    Provides a curated list of top movies with default high-quality filters
    and support for additional filtering by genre, actor, ratings, release year,
    and sorting by various criteria with user personalization.

    This endpoint is optimized for discovery of high-quality content by default
    applying a minimum IMDb rating filter and sorting by rating.

    Args:
        page: Page number for pagination
        limit: Number of items per page
        genre_id: Optional genre filter
        actor_id: Optional actor TMDB ID filter
        sort_by: Sort field (defaults to imdb_rating for top movies)
        sort_desc: Sort in descending order (defaults to True for highest rated first)
        imdb_rating: Minimum IMDb rating filter
        rotten_tomatoes_rating: Minimum Rotten Tomatoes rating filter
        metacritic_rating: Minimum Metacritic rating filter
        year: Release year filter
        start_year: Start release year filter (inclusive)
        end_year: End release year filter (inclusive)
        backend: Backend HTTP client dependency
        credentials: Optional Bearer token for authentication

    Returns:
        Paginated list of top movies with metadata

    Raises:
        HTTPException: If backend service is unavailable (502)
    """
    ***REMOVED*** Extract user ID from JWT token if provided
    user_id = None
    logger.debug(f"🔍 Debugging token extraction for top movies")
    logger.debug(f"📋 Credentials present: {bool(credentials)}")

    if credentials and credentials.credentials:
        logger.debug(f"🔑 Token present: {bool(credentials.credentials)}")
        logger.debug(f"🔑 Token preview: {credentials.credentials[:20]}...")

        ***REMOVED*** Temporarily enable debug logging for JWT extraction
        auth_logger = logging.getLogger("bff_api.utils.auth")
        original_level = auth_logger.level
        auth_logger.setLevel(logging.DEBUG)

        user_id = extract_user_id_from_token(credentials.credentials)

        ***REMOVED*** Restore original logging level
        auth_logger.setLevel(original_level)

        logger.debug(f"👤 Extracted user_id: {user_id}")
    else:
        logger.debug("❌ No credentials or token found - treating as anonymous user")

    try:
        ***REMOVED*** Build filter parameters for top movies
        filters: Dict[str, Any] = {}
        if genre_id is not None:
            filters["genre_id"] = genre_id
        if actor_id is not None:
            filters["actor_id"] = actor_id
        if sort_by:
            filters["sort_by"] = sort_by
        if sort_desc is not None:
            filters["sort_desc"] = sort_desc
        if imdb_rating is not None:
            filters["imdb_rating"] = imdb_rating
        if rotten_tomatoes_rating is not None:
            filters["rotten_tomatoes_rating"] = rotten_tomatoes_rating
        if metacritic_rating is not None:
            filters["metacritic_rating"] = metacritic_rating
        if year is not None:
            filters["year"] = year
        if start_year is not None:
            filters["start_year"] = start_year
        if end_year is not None:
            filters["end_year"] = end_year

        logger.debug(f"🎬 Fetching top movies with filters: {filters}")

        ***REMOVED*** Get top movies from backend
        movies_response = await _get_movies(backend, page=page, limit=limit, **filters)

        ***REMOVED*** Extract pagination data from backend's standardized format
        movies = movies_response.get("results", [])
        total_count = movies_response.get("total", 0)
        current_page = movies_response.get("page", page)
        per_page = movies_response.get("per_page", limit)
        total_pages = movies_response.get("total_pages", 0)
        has_next = movies_response.get("has_next", False)
        has_prev = movies_response.get("has_prev", False)

        ***REMOVED*** If user is authenticated, fetch user interactions for each movie
        if user_id and credentials:
            logger.debug(f"🔄 Fetching user interactions for {len(movies)} top movies")
            for movie in movies:
                movie_id = movie.get("id")
                if movie_id:
                    try:
                        interaction_data = await _get_user_movie_interaction(
                            backend, user_id, movie_id, jwt_token=credentials.credentials
                        )
                        if interaction_data:
                            ***REMOVED*** Map user interaction data directly to movie fields
                            ***REMOVED*** for frontend compatibility
                            movie["liked"] = interaction_data.get("liked", False)
                            movie["watched"] = interaction_data.get("watched", False)
                            movie["in_watchlist"] = interaction_data.get("in_watchlist", False)

                            ***REMOVED*** Also include complete user_interactions object for reference
                            movie["user_interactions"] = {
                                "in_watchlist": interaction_data.get("in_watchlist", False),
                                "is_favorite": interaction_data.get("liked", False),
                                "user_rating": interaction_data.get("rating"),
                                "watch_progress": interaction_data.get("watch_progress", 0),
                                "is_watched": interaction_data.get("watched", False),
                            }
                        else:
                            ***REMOVED*** Set default values if no interaction data exists
                            movie["liked"] = False
                            movie["watched"] = False
                            movie["in_watchlist"] = False

                            movie["user_interactions"] = {
                                "in_watchlist": False,
                                "is_favorite": False,
                                "user_rating": None,
                                "watch_progress": 0,
                                "is_watched": False,
                            }
                    except Exception as e:
                        logger.warning(
                            f"Failed to get user interaction for top movie {movie_id}: {e}"
                        )
                        ***REMOVED*** Set default values if fetching interaction data fails
                        movie["liked"] = False
                        movie["watched"] = False
                        movie["in_watchlist"] = False

                        movie["user_interactions"] = {
                            "in_watchlist": False,
                            "is_favorite": False,
                            "user_rating": None,
                            "watch_progress": 0,
                            "is_watched": False,
                        }
        else:
            ***REMOVED*** For anonymous users, set all interaction fields to false
            logger.debug(
                "No user authenticated - setting default interaction values for top movies"
            )
            for movie in movies:
                movie["liked"] = False
                movie["watched"] = False
                movie["in_watchlist"] = False
                movie["user_interactions"] = {
                    "in_watchlist": False,
                    "is_favorite": False,
                    "user_rating": None,
                    "watch_progress": 0,
                    "is_watched": False,
                }

        logger.debug(f"✅ Returning {len(movies)} top movies (page {current_page}/{total_pages})")

        ***REMOVED*** Use ResponseBuilder paginated pattern for consistent response structure
        response = responses.paginated(
            items=movies,
            page=current_page,
            limit=per_page,
            total=total_count,
            metadata={
                "filters_applied": filters,
                "service_info": {
                    "aggregated_from": ["backend-api"],
                    "user_authenticated": bool(user_id),
                    "user_personalized": bool(user_id),
                },
                "api_version": "v1",
                "response_pattern": "paginated",
                "collection_type": "top_movies",
            },
        )
        return cast(Dict[str, Any], response)

    except Exception as e:
        logger.error(
            "Backend error for top_movies", error=str(e), service="bff", endpoint="top_movies"
        )
        raise HTTPException(status_code=502, detail="Backend service unavailable")
