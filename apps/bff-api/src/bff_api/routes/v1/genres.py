"""Genre-related routes for BFF API."""

from typing import Any

from cache.decorators import redis_cache
from cache.keys import build_filtered_key
from config.logging import get_logger
from fast_core.dependencies import get_pagination
from fast_core.dependencies.common import PaginationParams
from fast_core.errors import ExternalServiceException
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from bff_api.core.metrics import get_bff_metrics
from bff_api.dependencies import get_backend_client
from bff_api.schemas.screen_schemas import GenreScreenData
from bff_api.services.clients import BackendClient
from bff_api.utils.auth import extract_user_id_from_token

logger = get_logger(__name__)
router = APIRouter(tags=["genres"])

***REMOVED*** Security scheme for optional authentication
security = HTTPBearer(auto_error=False)


def _build_genre_screen_cache_key(
    genre_id: int,
    page: int,
    limit: int,
    actor_id: int | None,
    sort_by: str | None,
    sort_desc: bool | None,
    imdb_rating: float | None,
    rotten_tomatoes_rating: int | None,
    metacritic_rating: int | None,
    year: int | None,
    start_year: int | None,
    end_year: int | None,
    user_id: int | None,
    backend: BackendClient,
    credentials: HTTPAuthorizationCredentials | None = None,
) -> str:
    """Build cache key for genre screen with all parameters using cache library utilities."""
    filters = {
        "page": page,
        "limit": limit,
        "actor_id": actor_id,
        "sort_by": sort_by,
        "sort_desc": sort_desc,
        "imdb_rating": imdb_rating,
        "rotten_tomatoes_rating": rotten_tomatoes_rating,
        "metacritic_rating": metacritic_rating,
        "year": year,
        "start_year": start_year,
        "end_year": end_year,
    }
    return build_filtered_key("screen:genre", str(genre_id), filters, user_id=user_id, prefix="")


@redis_cache(ttl=900, key_builder=_build_genre_screen_cache_key)  ***REMOVED*** 15 minutes for genre movie lists
async def _get_genre_screen_data(
    genre_id: int,
    page: int,
    limit: int,
    actor_id: int | None,
    sort_by: str | None,
    sort_desc: bool | None,
    imdb_rating: float | None,
    rotten_tomatoes_rating: int | None,
    metacritic_rating: int | None,
    year: int | None,
    start_year: int | None,
    end_year: int | None,
    user_id: int | None,
    backend: BackendClient,
    credentials: HTTPAuthorizationCredentials | None = None,
) -> dict[str, Any]:
    """Internal cached function for genre screen aggregation."""
    logger.debug(
        "Building genre screen data",
        genre_id=genre_id,
        page=page,
        limit=limit,
        user_id=user_id,
        service="bff",
        component="genre_screen_data",
    )

    ***REMOVED*** Get genre details from backend
    try:
        genre_response = await backend.get_genre(genre_id)
        logger.debug(
            "Retrieved genre details",
            genre_id=genre_id,
            genre_name=genre_response.get("name", "unknown"),
            service="bff",
            component="genres",
        )
    except ExternalServiceException as e:
        if "404" in str(e):
            raise HTTPException(status_code=404, detail="Genre not found")
        logger.error(
            "Failed to get genre details",
            genre_id=genre_id,
            error=str(e),
            service="bff",
            component="genres",
        )
        raise HTTPException(status_code=502, detail="Backend service unavailable")

    ***REMOVED*** Get movies for this genre with filters
    kwargs: dict[str, Any] = {"genre_id": genre_id}
    if actor_id is not None:
        kwargs["actor_id"] = actor_id
    if sort_by is not None:
        kwargs["sort_by"] = sort_by
    if sort_desc is not None:
        kwargs["sort_desc"] = sort_desc
    if imdb_rating is not None:
        kwargs["imdb_rating"] = imdb_rating
    if rotten_tomatoes_rating is not None:
        kwargs["rotten_tomatoes_rating"] = rotten_tomatoes_rating
    if metacritic_rating is not None:
        kwargs["metacritic_rating"] = metacritic_rating
    if year is not None:
        kwargs["year"] = year
    if start_year is not None:
        kwargs["start_year"] = start_year
    if end_year is not None:
        kwargs["end_year"] = end_year

    movies_response = await backend.get_movies(
        page=page,
        limit=limit,
        user_id=user_id,
        **kwargs,
    )

    ***REMOVED*** Extract pagination data from backend's standardized format
    movies = movies_response.get("results", [])
    total_count = movies_response.get("total", 0)
    current_page = movies_response.get("page", page)
    per_page = movies_response.get("per_page", limit)
    total_pages = movies_response.get("total_pages", 0)
    has_next = movies_response.get("has_next", False)
    has_prev = movies_response.get("has_prev", False)

    ***REMOVED*** For anonymous users, set all interaction fields to false
    logger.debug(
        "Setting default interaction values for genre movies",
        genre_id=genre_id,
        movie_count=len(movies),
        service="bff",
        component="user_interactions",
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

    ***REMOVED*** Return as dictionary for caching
    genre_screen_data = {
        "genre": genre_response,
        "total": total_count,
        "page": current_page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev,
        "results": movies,
    }

    logger.debug(
        "Successfully built genre screen data",
        genre_id=genre_id,
        service="bff",
        component="genre_screen_data",
    )

    return genre_screen_data


@router.get("/genres/{genre_id}", response_model=GenreScreenData)
async def get_genre_screen(
    genre_id: int = Path(..., description="Genre ID"),
    pagination: PaginationParams = get_pagination(max_page_size=100),
    actor_id: int | None = Query(None, description="Filter by actor TMDB ID"),
    sort_by: str | None = Query(
        None,
        description="Sort by field (title, release_date, imdb_rating, rotten_tomatoes_rating, metacritic_rating)",
    ),
    sort_desc: bool | None = Query(True, description="Sort in descending order"),
    imdb_rating: float | None = Query(
        None, ge=0, le=10, description="Filter by minimum IMDb rating"
    ),
    rotten_tomatoes_rating: int | None = Query(
        None, ge=0, le=100, description="Filter by minimum Rotten Tomatoes rating"
    ),
    metacritic_rating: int | None = Query(
        None, ge=0, le=100, description="Filter by minimum Metacritic rating"
    ),
    year: int | None = Query(None, description="Filter by release year"),
    start_year: int | None = Query(None, description="Filter by start year (inclusive)"),
    end_year: int | None = Query(None, description="Filter by end year (inclusive)"),
    user_id: int | None = Query(None, description="User ID for personalized content"),
    backend: BackendClient = Depends(get_backend_client),
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> GenreScreenData:
    """Get aggregated data for genre screen.

    Provides movies filtered by specific genre with pagination support,
    additional filtering by actor, ratings, release year, and sorting
    options with optional user personalization.

    Args:
        genre_id: Genre ID to filter movies by
        pagination: Pagination parameters (page, limit) from fast-core dependency
        actor_id: Optional actor TMDB ID for filtering
        sort_by: Sort field (title, release_date, imdb_rating, rotten_tomatoes_rating, metacritic_rating)
        sort_desc: Sort in descending order
        imdb_rating: Minimum IMDb rating filter
        rotten_tomatoes_rating: Minimum Rotten Tomatoes rating filter
        metacritic_rating: Minimum Metacritic rating filter
        year: Release year filter
        start_year: Start release year filter (inclusive)
        end_year: End release year filter (inclusive)
        user_id: Optional user ID for personalized content (deprecated - use JWT token)
        backend: Backend client dependency
        credentials: Optional Bearer token for authentication

    Returns:
        Aggregated genre screen data with movies and metadata

    Raises:
        HTTPException: 404 if genre not found, 502 if backend unavailable
    """
    ***REMOVED*** Record movie request metrics
    metrics = get_bff_metrics()
    if metrics:
        metrics.record_movie_request("genre", "started")

    ***REMOVED*** Extract user ID from JWT token if provided (overrides query parameter)
    extracted_user_id = None
    logger.debug(
        "Processing genre screen request",
        genre_id=genre_id,
        has_credentials=bool(credentials),
        service="bff",
        endpoint="genre_screen",
    )

    if credentials and credentials.credentials:
        extracted_user_id = extract_user_id_from_token(credentials.credentials)
        logger.debug(
            "User authenticated for genre screen",
            genre_id=genre_id,
            user_id=extracted_user_id,
            service="bff",
            endpoint="genre_screen",
        )
    else:
        logger.debug(
            "Anonymous user accessing genre screen",
            genre_id=genre_id,
            service="bff",
            endpoint="genre_screen",
        )

    ***REMOVED*** Use extracted user ID from token, fallback to query parameter
    final_user_id = extracted_user_id or user_id

    try:
        ***REMOVED*** Use the cached function - decorator handles all cache logic
        genre_screen_dict = await _get_genre_screen_data(
            genre_id=genre_id,
            page=pagination.page,
            limit=pagination.limit,
            actor_id=actor_id,
            sort_by=sort_by,
            sort_desc=sort_desc,
            imdb_rating=imdb_rating,
            rotten_tomatoes_rating=rotten_tomatoes_rating,
            metacritic_rating=metacritic_rating,
            year=year,
            start_year=start_year,
            end_year=end_year,
            user_id=final_user_id,
            backend=backend,
            credentials=credentials,
        )

        ***REMOVED*** Handle user interactions for authenticated users (not cached due to user-specific nature)
        if final_user_id and credentials:
            movies = genre_screen_dict["results"]
            logger.debug(
                "Fetching user interactions for genre movies",
                genre_id=genre_id,
                user_id=final_user_id,
                movie_count=len(movies),
                service="bff",
                component="user_interactions",
            )
            for movie in movies:
                movie_id = movie.get("id")
                if movie_id:
                    try:
                        interaction_data = await backend.get_user_movie_interaction(
                            final_user_id, movie_id, jwt_token=credentials.credentials
                        )
                        if interaction_data:
                            ***REMOVED*** Map user interaction data directly to movie fields
                            movie["liked"] = interaction_data.get("liked", False)
                            movie["watched"] = interaction_data.get("watched", False)
                            movie["in_watchlist"] = interaction_data.get("in_watchlist", False)
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
                            "Failed to get user interaction for genre movie",
                            genre_id=genre_id,
                            movie_id=movie_id,
                            user_id=final_user_id,
                            error=str(e),
                            service="bff",
                            component="user_interactions",
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

        ***REMOVED*** Record successful movie request metrics
        if metrics:
            metrics.record_movie_request("genre", "success")

        ***REMOVED*** Convert dictionary back to Pydantic model
        return GenreScreenData(**genre_screen_dict)

    except ExternalServiceException as e:
        ***REMOVED*** Record error metrics
        if metrics:
            metrics.record_movie_request("genre", "service_error")

        logger.error(
            "Backend error for genre screen",
            genre_id=genre_id,
            error=str(e),
            service="bff",
            endpoint="genre_screen",
        )
        if "404" in str(e):
            raise HTTPException(status_code=404, detail="Genre not found")
        raise HTTPException(status_code=502, detail="Backend service unavailable")
