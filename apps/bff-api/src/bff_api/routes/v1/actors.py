"""Actor-related routes for BFF API."""

from typing import Any, cast

from cache.decorators import redis_cache
from cache.keys import build_filtered_key, build_paginated_key
from config.logging import get_logger
from fast_core.errors import ExternalServiceException
from fast_core.responses import ResponseBuilder
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from bff_api.core.metrics import get_bff_metrics
from bff_api.dependencies import get_backend_client
from bff_api.services.clients import BackendClient
from bff_api.utils.auth import extract_user_id_from_token

logger = get_logger(__name__)
router = APIRouter(tags=["actors"])

# Initialize response builder for consistent API responses
responses = ResponseBuilder(
    config={
        "pagination": {
            "default_limit": 20,
            "max_limit": 100,
        },
    }
)

# Security scheme for optional authentication
security = HTTPBearer(auto_error=False)


@redis_cache(
    ttl=1800,  # 30 minutes - actor data changes infrequently
    key_builder=lambda actor_id, page, limit, backend, credentials=None: build_paginated_key(
        "screen:actor", [actor_id], page, limit, prefix=""
    ),
)
async def _get_actor_screen_data(
    actor_id: int,
    page: int,
    limit: int,
    backend: BackendClient,
    credentials: HTTPAuthorizationCredentials | None = None,
) -> dict[str, Any]:
    """Internal cached function for actor screen aggregation."""
    logger.debug(
        "Building actor screen data",
        actor_id=actor_id,
        page=page,
        limit=limit,
        service="bff",
        component="actor_screen_data",
    )

    # Get actor details
    actor = await backend.get_actor(actor_id)
    if not actor:
        raise HTTPException(status_code=404, detail="Actor not found")

    # Get actor's movies with pagination support
    movies_response = await backend.get_movies(page=page, limit=limit, actor_id=actor_id)

    # Extract pagination data
    movies = movies_response.get("results", [])
    total_count = movies_response.get("total", 0)
    current_page = movies_response.get("page", page)
    per_page = movies_response.get("per_page", limit)
    total_pages = movies_response.get("total_pages", 0)
    has_next = movies_response.get("has_next", False)
    has_prev = movies_response.get("has_prev", False)

    # For anonymous users, set all interaction fields to false
    logger.debug(
        "Setting default interaction values for actor movies",
        actor_id=actor_id,
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

    # Return as dictionary for caching
    actor_screen_data = {
        "actor": actor,
        "movies": {
            "total": total_count,
            "page": current_page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
            "results": movies,
        },
    }

    logger.debug(
        "Successfully built actor screen data",
        actor_id=actor_id,
        service="bff",
        component="actor_screen_data",
    )

    return actor_screen_data


def _build_actor_movies_cache_key(
    actor_id: int,
    page: int,
    limit: int,
    genre_id: int | None,
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
    """Build cache key for actor movies list with all parameters using cache library utilities."""
    filters = {
        "page": page,
        "limit": limit,
        "genre_id": genre_id,
        "sort_by": sort_by,
        "sort_desc": sort_desc,
        "imdb_rating": imdb_rating,
        "rotten_tomatoes_rating": rotten_tomatoes_rating,
        "metacritic_rating": metacritic_rating,
        "year": year,
        "start_year": start_year,
        "end_year": end_year,
    }
    return build_filtered_key(
        "screen:actor", f"{actor_id}:movies", filters, user_id=user_id, prefix=""
    )


@redis_cache(
    ttl=900,
    key_builder=_build_actor_movies_cache_key,  # 15 minutes for filtered movie lists
)
async def _get_actor_movies_data(
    actor_id: int,
    page: int,
    limit: int,
    genre_id: int | None,
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
    """Internal cached function for actor movies list aggregation."""
    logger.debug(
        "Building actor movies data",
        actor_id=actor_id,
        page=page,
        limit=limit,
        user_id=user_id,
        service="bff",
        component="actor_movies_data",
    )

    # Build filter parameters
    filters: dict[str, Any] = {"actor_id": actor_id}  # Always include actor_id filter
    if genre_id is not None:
        filters["genre_id"] = genre_id
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

    # Get movies from backend
    movies_response = await backend.get_movies(page=page, limit=limit, **filters)

    # Extract pagination data
    movies = movies_response.get("results", [])
    total_count = movies_response.get("total", 0)
    current_page = movies_response.get("page", page)
    per_page = movies_response.get("per_page", limit)
    total_pages = movies_response.get("total_pages", 0)
    has_next = movies_response.get("has_next", False)
    has_prev = movies_response.get("has_prev", False)

    # For anonymous users, set all interaction fields to false
    logger.debug(
        "Setting default interaction values for actor movies",
        actor_id=actor_id,
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

    # Return as dictionary for caching
    movies_data = {
        "total": total_count,
        "page": current_page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev,
        "results": movies,
    }

    logger.debug(
        "Successfully built actor movies data",
        actor_id=actor_id,
        service="bff",
        component="actor_movies_data",
    )

    return movies_data


@router.get("/actors/{actor_id}")
async def get_actor_screen(
    actor_id: int = Path(..., description="Actor ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    backend: BackendClient = Depends(get_backend_client),
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict[str, Any]:
    """Get aggregated data for actor detail screen.

    Fetches complete actor information including their movies and metadata.

    Args:
        actor_id: Actor ID to fetch details for
        page: Page number for pagination
        limit: Number of items per page
        backend: Backend client dependency
        credentials: Optional Bearer token for authentication

    Returns:
        Aggregated actor detail screen data

    Raises:
        HTTPException: 404 if actor not found, 502 if backend unavailable
    """
    # Record movie request metrics
    metrics = get_bff_metrics()
    if metrics:
        metrics.record_movie_request("actor", "started")

    # Extract user ID from JWT token if provided
    user_id = None
    logger.debug(
        "Processing actor screen request",
        actor_id=actor_id,
        has_credentials=bool(credentials),
        service="bff",
        endpoint="actor_screen",
    )

    if credentials and credentials.credentials:
        user_id = extract_user_id_from_token(credentials.credentials)
        logger.debug(
            "User authenticated for actor screen",
            actor_id=actor_id,
            user_id=user_id,
            service="bff",
            endpoint="actor_screen",
        )
    else:
        logger.debug(
            "Anonymous user accessing actor screen",
            actor_id=actor_id,
            service="bff",
            endpoint="actor_screen",
        )

    try:
        # Use the cached function - decorator handles all cache logic
        actor_screen_dict = await _get_actor_screen_data(
            actor_id, page, limit, backend, credentials
        )

        # Handle user interactions for authenticated users (not cached due to user-specific nature)
        if user_id and credentials:
            movies = actor_screen_dict["movies"]["results"]
            logger.debug(
                "Fetching user interactions for actor movies",
                actor_id=actor_id,
                user_id=user_id,
                movie_count=len(movies),
                service="bff",
                component="user_interactions",
            )
            for movie in movies:
                movie_id = movie.get("id")
                if movie_id:
                    try:
                        interaction_data = await backend.get_user_movie_interaction(
                            user_id, movie_id, jwt_token=credentials.credentials
                        )
                        if interaction_data:
                            # Map user interaction data directly to movie fields
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
                            # Set default values if no interaction data exists
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
                            "Failed to get user interaction for actor movie",
                            actor_id=actor_id,
                            movie_id=movie_id,
                            user_id=user_id,
                            error=str(e),
                            service="bff",
                            component="user_interactions",
                        )
                        # Set default values if fetching interaction data fails
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

        # Record successful movie request metrics
        if metrics:
            metrics.record_movie_request("actor", "success")

        # Use ResponseBuilder detail pattern for consistent response structure
        response = responses.detail(
            item=actor_screen_dict["actor"],
            related={
                "movies": actor_screen_dict["movies"],
            },
            context={
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total_movies": actor_screen_dict["movies"]["total"],
                },
                "personalized": bool(user_id),
            },
            metadata={
                "service_info": {
                    "aggregated_from": ["backend-api"],
                    "user_authenticated": bool(user_id),
                },
                "api_version": "v1",
                "response_pattern": "detail",
                "actor_context": {
                    "actor_id": actor_id,
                },
            },
        )
        return cast(dict[str, Any], response)

    except ExternalServiceException as e:
        # Record error metrics
        if metrics:
            metrics.record_movie_request("actor", "service_error")

        logger.error(f"Backend error for actor {actor_id}: {e}")
        if "404" in str(e):
            raise HTTPException(status_code=404, detail="Actor not found")
        raise HTTPException(status_code=502, detail="Backend service unavailable")


@router.get("/actors/{actor_id}/movies")
async def get_actor_movies(
    actor_id: int = Path(..., description="Actor ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    genre_id: int | None = Query(None, description="Filter by genre ID"),
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
    backend: BackendClient = Depends(get_backend_client),
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict[str, Any]:
    """Get paginated list of movies for a specific actor with filters.

    Provides paginated movie listings for an actor with support for filtering by genre,
    ratings, release year, and sorting by various criteria with user personalization.

    Args:
        actor_id: Actor ID to fetch movies for
        page: Page number for pagination
        limit: Number of items per page
        genre_id: Optional genre filter
        sort_by: Sort field (title, release_date, imdb_rating, rotten_tomatoes_rating, metacritic_rating)
        sort_desc: Sort in descending order
        imdb_rating: Minimum IMDb rating filter
        rotten_tomatoes_rating: Minimum Rotten Tomatoes rating filter
        metacritic_rating: Minimum Metacritic rating filter
        year: Release year filter
        start_year: Start release year filter (inclusive)
        end_year: End release year filter (inclusive)
        backend: Backend client dependency
        credentials: Optional Bearer token for authentication

    Returns:
        Paginated movie list with metadata

    Raises:
        HTTPException: If backend service is unavailable (502)
    """
    # Extract user ID from JWT token if provided
    user_id = None
    logger.debug(
        "Processing actor movies request",
        actor_id=actor_id,
        has_credentials=bool(credentials),
        service="bff",
        endpoint="actor_movies",
    )

    if credentials and credentials.credentials:
        user_id = extract_user_id_from_token(credentials.credentials)
        logger.debug(
            "User authenticated for actor movies",
            actor_id=actor_id,
            user_id=user_id,
            service="bff",
            endpoint="actor_movies",
        )
    else:
        logger.debug(
            "Anonymous user accessing actor movies",
            actor_id=actor_id,
            service="bff",
            endpoint="actor_movies",
        )

    try:
        # Use the cached function - decorator handles all cache logic
        movies_data_dict = await _get_actor_movies_data(
            actor_id=actor_id,
            page=page,
            limit=limit,
            genre_id=genre_id,
            sort_by=sort_by,
            sort_desc=sort_desc,
            imdb_rating=imdb_rating,
            rotten_tomatoes_rating=rotten_tomatoes_rating,
            metacritic_rating=metacritic_rating,
            year=year,
            start_year=start_year,
            end_year=end_year,
            user_id=user_id,
            backend=backend,
            credentials=credentials,
        )

        # Handle user interactions for authenticated users (not cached due to user-specific nature)
        if user_id and credentials:
            movies = movies_data_dict["results"]
            logger.debug(f"🔄 Fetching user interactions for {len(movies)} movies")
            for movie in movies:
                movie_id = movie.get("id")
                if movie_id:
                    try:
                        interaction_data = await backend.get_user_movie_interaction(
                            user_id, movie_id, jwt_token=credentials.credentials
                        )
                        if interaction_data:
                            # Map user interaction data directly to movie fields
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
                            # Set default values if no interaction data exists
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
                        logger.warning(f"Failed to get user interaction for movie {movie_id}: {e}")
                        # Set default values if fetching interaction data fails
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

        # Use ResponseBuilder paginated pattern for consistent response structure
        filters_applied = {
            "actor_id": actor_id,
            "genre_id": genre_id,
            "sort_by": sort_by,
            "sort_desc": sort_desc,
            "imdb_rating": imdb_rating,
            "rotten_tomatoes_rating": rotten_tomatoes_rating,
            "metacritic_rating": metacritic_rating,
            "year": year,
            "start_year": start_year,
            "end_year": end_year,
        }

        response = responses.paginated(
            items=movies_data_dict["results"],
            page=movies_data_dict["page"],
            limit=movies_data_dict["per_page"],
            total=movies_data_dict["total"],
            metadata={
                "filters_applied": filters_applied,
                "service_info": {
                    "aggregated_from": ["backend-api"],
                    "user_authenticated": bool(user_id),
                    "user_personalized": bool(user_id),
                },
                "api_version": "v1",
                "response_pattern": "paginated",
                "collection_type": "actor_movies",
                "actor_context": {
                    "actor_id": actor_id,
                },
            },
        )
        return cast(dict[str, Any], response)

    except ExternalServiceException as e:
        logger.error(f"Backend error for actor {actor_id} movies: {e}")
        raise HTTPException(status_code=502, detail="Backend service unavailable")
