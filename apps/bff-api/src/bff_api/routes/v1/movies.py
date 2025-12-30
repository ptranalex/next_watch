"""Movie-related routes for BFF API."""

import asyncio
import time
from typing import Any, cast

from cache.decorators import redis_cache
from cache.keys import build_cache_key, build_filtered_key
from config.logging import get_logger
from fast_core.dependencies import get_pagination
from fast_core.dependencies.common import PaginationParams
from fast_core.errors.exceptions import (
    APIException,
    ExternalServiceException,
    ResourceNotFoundException,
)
from fast_core.responses import ResponseBuilder
from fast_core.security.rate_limit import rate_limit
from fastapi import APIRouter, BackgroundTasks, Depends, Path, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from bff_api.core.metrics import get_bff_metrics
from bff_api.dependencies import get_backend_client
from bff_api.dependencies.service_clients import get_recommendation_client
from bff_api.services.clients import BackendClient
from bff_api.services.clients.recommendation import RecommendationClient
from bff_api.services.smart_warming import BFFSmartWarming, get_smart_warming_dependency
from bff_api.utils.auth import extract_user_id_from_token

logger = get_logger(__name__)
router = APIRouter(tags=["movies"])

# Security scheme for optional authentication
security = HTTPBearer(auto_error=False)

# Initialize response builder for consistent API responses
responses = ResponseBuilder(
    config={
        "pagination": {
            "default_limit": 20,
            "max_limit": 100,
        },
        "detail": {
            "include_metadata": True,
        },
    }
)


def _build_movies_list_cache_key(
    page: int,
    limit: int,
    genre_id: int | None,
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
    """Build cache key for movies list with all parameters using cache library utilities."""
    filters = {
        "page": page,
        "limit": limit,
        "genre_id": genre_id,
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
    return build_filtered_key("screen:movies", "list", filters, user_id=user_id, prefix="")


def _build_static_movie_cache_key(movie_id: int, version: str | None = None) -> str:
    """Build cache key for static movie data with optional versioning.

    Args:
        movie_id: Movie ID
        version: Optional version string (timestamp, hash, or version number)

    Returns:
        Versioned cache key for static movie data
    """
    if version:
        return f"static:movie:{movie_id}:v{version}"
    else:
        # Fallback to non-versioned key for backward compatibility
        return build_cache_key("screen:movie:static", [movie_id], prefix="")


def _extract_movie_version(movie_data: dict[str, Any]) -> str | None:
    """Extract version information from movie data for cache versioning.

    Tries multiple version strategies in order of preference:
    1. updated_at timestamp
    2. content hash of core fields
    3. fallback to current timestamp

    Args:
        movie_data: Movie data dictionary from backend

    Returns:
        Version string for cache key, or None if no version available
    """
    import hashlib
    import time

    # Strategy 1: Use updated_at timestamp if available
    if "updated_at" in movie_data and movie_data["updated_at"]:
        try:
            # Convert to timestamp if it's a datetime string
            updated_at = movie_data["updated_at"]
            if isinstance(updated_at, str):
                from datetime import datetime

                dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                return str(int(dt.timestamp()))
            return str(updated_at)
        except Exception:
            pass

    # Strategy 2: Use version field if available
    if "version" in movie_data and movie_data["version"]:
        return str(movie_data["version"])

    # Strategy 3: Create content hash from core movie fields
    try:
        # Hash core static fields that rarely change
        core_fields = {
            "id": movie_data.get("id"),
            "title": movie_data.get("title"),
            "release_date": movie_data.get("release_date"),
            "runtime": movie_data.get("runtime"),
            "imdb_rating": movie_data.get("imdb_rating"),
            "overview": movie_data.get("overview"),
        }
        content = str(sorted(core_fields.items()))
        hash_obj = hashlib.md5(content.encode())
        return hash_obj.hexdigest()[:12]  # Short hash
    except Exception:
        pass

    # Strategy 4: Fallback to current timestamp (least preferred)
    # This essentially disables forever caching but maintains functionality
    return str(int(time.time()))


def _build_user_movie_interactions_cache_key(movie_id: int, user_id: int | None) -> str:
    """Build cache key for user-specific movie interactions."""
    user_part = str(user_id) if user_id is not None else "anon"
    return f"screen:movie:user:{movie_id}:user:{user_part}"


def _build_static_movies_list_cache_key(
    page: int,
    limit: int,
    genre_id: int | None,
    actor_id: int | None,
    sort_by: str | None,
    sort_desc: bool | None,
    imdb_rating: float | None,
    rotten_tomatoes_rating: int | None,
    metacritic_rating: int | None,
    year: int | None,
    start_year: int | None,
    end_year: int | None,
    version: str | None = None,
) -> str:
    """Build cache key for static movies list data with optional versioning."""
    if version:
        # Create a hash of all filter parameters for versioned key
        import hashlib

        filters = {
            "page": page,
            "limit": limit,
            "genre_id": genre_id,
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
        # Create a short hash of the filter parameters
        filter_content = str(sorted(filters.items()))
        filter_hash = hashlib.md5(filter_content.encode()).hexdigest()[:8]
        return f"static:movies_list:{filter_hash}:v{version}"
    else:
        # Fallback to non-versioned key
        filters = {
            "page": page,
            "limit": limit,
            "genre_id": genre_id,
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
        return build_filtered_key("screen:movies:static", "list", filters, prefix="")


def _build_user_movies_batch_cache_key(movie_ids: list[int], user_id: int | None) -> str:
    """Build cache key for user interactions with a batch of movies."""
    # Use a simple string-based approach instead of build_cache_key
    user_part = str(user_id) if user_id is not None else "anon"
    movie_ids_part = "-".join(str(mid) for mid in movie_ids)
    return f"screen:movies:user:batch:{user_part}:{movie_ids_part}"


@redis_cache(
    ttl=30 * 24 * 3600,  # 30 days for static content - "cache forever" approach
    key_builder=lambda movie_id,
    backend,
    recommendation_client,
    version=None: _build_static_movie_cache_key(movie_id, version),
)
async def _get_static_movie_data(
    movie_id: int,
    backend: BackendClient,
    recommendation_client: RecommendationClient,
    version: str | None = None,
) -> dict[str, Any]:
    """Internal cached function for static movie data."""
    logger.debug(
        "Building static movie data",
        movie_id=movie_id,
        service="bff",
        component="static_data",
    )

    # 🚀 PERFORMANCE: Fetch all static data in parallel instead of sequentially
    logger.debug(
        "Starting parallel API calls for movie data",
        movie_id=movie_id,
        service="bff",
        component="static_data_parallel",
    )

    # Execute all API calls in parallel for maximum performance
    movie_task = backend.get_movie(movie_id)
    movie_cast_task = backend.get_movie_cast(movie_id)
    trailers_task = backend.get_movie_trailers(movie_id)
    similar_movies_task = recommendation_client.get_similar_movies(
        movie_id,
        limit=20,
        min_score=0.01,
    )

    # Wait for all calls to complete
    movie, movie_cast, trailers, similar_movies = await asyncio.gather(
        movie_task,
        movie_cast_task,
        trailers_task,
        similar_movies_task,
        return_exceptions=True,
    )

    # Handle any exceptions from parallel calls
    if isinstance(movie, BaseException):
        logger.error("Failed to get movie data", movie_id=movie_id, error=str(movie))
        raise movie
    if isinstance(movie_cast, BaseException):
        logger.warning("Failed to get movie cast", movie_id=movie_id, error=str(movie_cast))
        movie_cast = []  # Fallback to empty cast
    if isinstance(trailers, BaseException):
        logger.warning("Failed to get movie trailers", movie_id=movie_id, error=str(trailers))
        trailers = []  # Fallback to empty trailers
    if isinstance(similar_movies, BaseException):
        logger.warning("Failed to get similar movies", movie_id=movie_id, error=str(similar_movies))
        similar_movies = []  # Fallback to empty similar movies

    logger.debug(
        "Completed parallel API calls for movie data",
        movie_id=movie_id,
        service="bff",
        component="static_data_parallel",
    )

    # Enrich similar movies with basic details (no user data)
    if similar_movies:
        similar_movie_ids: list[int] = []
        for similar_item in similar_movies:
            movie_id_value = similar_item.get("id")
            if movie_id_value is not None and isinstance(movie_id_value, (int, str)):
                try:
                    similar_movie_ids.append(int(movie_id_value))
                except (ValueError, TypeError):
                    logger.warning(
                        "Invalid movie ID in similar movies",
                        invalid_id=movie_id_value,
                        service="bff",
                        component="similar_movies",
                    )

        if similar_movie_ids:
            try:
                # Fetch movie details in bulk (without user data)
                movies_response = await backend.get_movies_bulk(
                    movie_ids=similar_movie_ids,
                    page=1,
                    limit=len(similar_movie_ids),
                )
                similar_movies = movies_response.get("results", [])
            except Exception as e:
                logger.warning(
                    "Failed to enrich similar movies",
                    error=str(e),
                    service="bff",
                    component="similar_movies",
                )

    # Build the static data response
    static_data = {
        "movie": movie,
        "cast": movie_cast,
        "trailers": trailers,
        "similar_movies": similar_movies,
    }

    logger.debug(
        "Successfully built static movie data",
        movie_id=movie_id,
        service="bff",
        component="static_data",
    )

    return static_data


async def _get_versioned_static_movie_data(
    movie_id: int,
    backend: BackendClient,
    recommendation_client: RecommendationClient,
) -> dict[str, Any]:
    """Get static movie data with automatic version detection.

    This function implements the "cache forever" strategy by:
    1. Fetching movie data to determine version
    2. Using versioned cache key for the actual static data
    3. Falling back to non-versioned cache if version detection fails

    Args:
        movie_id: Movie ID
        backend: Backend client
        recommendation_client: Recommendation client

    Returns:
        Static movie data with versioned caching
    """
    logger.debug(
        "Getting versioned static movie data",
        movie_id=movie_id,
        service="bff",
        component="versioned_static_data",
    )

    try:
        # First, get basic movie data to determine version
        movie = await backend.get_movie(movie_id)
        version = _extract_movie_version(movie)

        logger.debug(
            "Extracted movie version",
            movie_id=movie_id,
            version=version,
            service="bff",
            component="versioned_static_data",
        )

        # Use versioned cache key for the full static data
        return await _get_static_movie_data(
            movie_id, backend, recommendation_client, version=version
        )

    except Exception as e:
        logger.warning(
            "Failed to get versioned movie data, falling back to non-versioned",
            movie_id=movie_id,
            error=str(e),
            service="bff",
            component="versioned_static_data",
        )

        # Fallback to non-versioned caching
        return await _get_static_movie_data(movie_id, backend, recommendation_client, version=None)


@redis_cache(
    ttl=300,  # 5 minutes for user interactions (watchlist/favorites) - balance freshness vs performance
    key_builder=lambda movie_id,
    user_id,
    backend,
    credentials: _build_user_movie_interactions_cache_key(movie_id, user_id),
)
async def _get_user_movie_interactions(
    movie_id: int,
    user_id: int | None,
    backend: BackendClient,
    credentials: HTTPAuthorizationCredentials | None = None,
) -> dict[str, Any]:
    """Internal cached function for user-specific movie interactions."""
    logger.debug(
        "Fetching user movie interactions",
        movie_id=movie_id,
        user_id=user_id,
        service="bff",
        component="user_data",
    )

    # Default user interactions
    user_interactions_dict: dict[str, Any] = {
        "in_watchlist": False,
        "is_favorite": False,
        "user_rating": None,
        "watch_progress": 0,
        "is_watched": False,
    }

    # Get user interactions for authenticated users
    if user_id and credentials:
        try:
            interaction_data = await backend.get_user_movie_interaction(
                user_id, movie_id, jwt_token=credentials.credentials
            )
            if interaction_data:
                user_interactions_dict = {
                    "in_watchlist": interaction_data.get("in_watchlist", False),
                    "is_favorite": interaction_data.get("liked", False),
                    "user_rating": interaction_data.get("rating"),
                    "watch_progress": interaction_data.get("watch_progress", 0),
                    "is_watched": interaction_data.get("watched", False),
                }
        except Exception as e:
            logger.warning(
                "Failed to get user interactions",
                user_id=user_id,
                movie_id=movie_id,
                error=str(e),
                service="bff",
            )

    return user_interactions_dict


async def _enrich_similar_movies_with_user_data(
    similar_movies: list[dict[str, Any]],
    user_id: int | None,
    backend: BackendClient,
    credentials: HTTPAuthorizationCredentials | None = None,
) -> list[dict[str, Any]]:
    """Enrich similar movies with user interaction data."""
    if not user_id or not credentials or not similar_movies:
        # For anonymous users, set default interaction values
        for movie in similar_movies:
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
        return similar_movies

        # Extract movie IDs from similar movies
    movie_ids = [movie.get("id") for movie in similar_movies if movie.get("id") is not None]
    # Filter to ensure we only have valid integers
    valid_movie_ids = [mid for mid in movie_ids if isinstance(mid, int)]

    if not valid_movie_ids:
        # No valid movie IDs, return with default values
        for movie in similar_movies:
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
        return similar_movies

    # Use batch method to get all interactions at once
    try:
        batch_interactions = await backend.get_user_movie_interactions_batch(
            user_id, valid_movie_ids, jwt_token=credentials.credentials
        )

        # Enrich each movie with its interaction data
        for movie in similar_movies:
            movie_id = movie.get("id")
            if movie_id and movie_id in batch_interactions:
                interaction_data = batch_interactions[movie_id]
                if interaction_data:
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
                    # Set default values
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
                # Set default values if movie_id not found in batch
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
            "Failed to get batch user interactions for similar movies",
            movie_count=len(valid_movie_ids),
            error=str(e),
            service="bff",
        )
        # Set default values for all movies on error
        for movie in similar_movies:
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

    return similar_movies


async def _get_movie_screen_data(
    movie_id: int,
    user_id: int | None,
    backend: BackendClient,
    recommendation_client: RecommendationClient,
    credentials: HTTPAuthorizationCredentials | None = None,
) -> dict[str, Any]:
    """Compose movie screen data from separate cached components."""
    logger.debug(
        "Composing movie screen data",
        movie_id=movie_id,
        user_id=user_id,
        service="bff",
        component="screen_data",
    )

    # Get static data with versioned caching (30-day TTL - "cache forever" approach)
    static_data = await _get_versioned_static_movie_data(movie_id, backend, recommendation_client)

    # Get user interactions (cached separately with shorter TTL)
    user_interactions = await _get_user_movie_interactions(movie_id, user_id, backend, credentials)

    # Enrich similar movies with user data if authenticated
    similar_movies = await _enrich_similar_movies_with_user_data(
        static_data["similar_movies"], user_id, backend, credentials
    )

    # Combine the data for the final response
    screen_data = {
        "movie": static_data["movie"],
        "cast": static_data["cast"],
        "trailers": static_data["trailers"],
        "similar_movies": similar_movies,
        "user_interactions": user_interactions,
    }

    logger.debug(
        "Successfully composed movie screen data",
        movie_id=movie_id,
        user_id=user_id,
        service="bff",
        component="screen_data",
    )

    return screen_data


@rate_limit(
    requests=200, window=60
)  # 200 requests per minute (higher for individual movie requests)
@router.get("/movies/{movie_id}")
async def get_movie_screen(
    background_tasks: BackgroundTasks,
    movie_id: int = Path(..., description="Movie ID"),
    backend: BackendClient = Depends(get_backend_client),
    recommendation_client: RecommendationClient = Depends(get_recommendation_client),
    smart_warming: BFFSmartWarming = Depends(get_smart_warming_dependency),
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict[str, Any]:
    """Get aggregated data for movie detail screen.

    Fetches complete movie information including cast, similar movies,
    and user-specific interaction data for the movie detail view.

    Args:
        movie_id: Movie ID to fetch details for
        backend: Backend client dependency
        credentials: Optional Bearer token for authentication

    Returns:
        Aggregated movie detail screen data

    Raises:
        ResourceNotFoundException: If movie not found
        ExternalServiceException: If backend service unavailable
    """
    # Record movie request metrics
    metrics = get_bff_metrics()
    if metrics:
        metrics.record_movie_request("detail", "started")

    # Extract user ID from JWT token if provided
    user_id = None
    logger.debug(
        "Processing movie detail request",
        movie_id=movie_id,
        has_credentials=bool(credentials),
        service="bff",
        endpoint="movie_detail",
    )

    if credentials and credentials.credentials:
        user_id = extract_user_id_from_token(credentials.credentials)
        logger.debug(
            "User authenticated for movie detail",
            movie_id=movie_id,
            user_id=user_id,
            service="bff",
            endpoint="movie_detail",
        )
    else:
        logger.debug(
            "Anonymous user accessing movie detail",
            movie_id=movie_id,
            service="bff",
            endpoint="movie_detail",
        )

    try:
        # Record aggregation operation start
        aggregation_start = time.time()

        # Use the cached function - decorator handles all cache logic
        screen_data_dict = await _get_movie_screen_data(
            movie_id, user_id, backend, recommendation_client, credentials
        )

        # Record aggregation operation completion
        aggregation_duration = time.time() - aggregation_start
        if metrics:
            metrics.record_aggregation_operation(
                operation="movie_detail_aggregation",
                service_count=2,  # backend-api + recommendation-api
                duration=aggregation_duration,
            )

        # Use ResponseBuilder detail pattern for consistent response structure
        response = responses.detail(
            item=screen_data_dict["movie"],
            related={
                "cast": screen_data_dict["cast"],
                "trailers": screen_data_dict["trailers"],
                "similar_movies": screen_data_dict["similar_movies"],
            },
            context={
                "user_interactions": screen_data_dict["user_interactions"],
                "personalized": bool(user_id),
            },
            metadata={
                "service_info": {
                    "aggregated_from": ["backend-api", "recommendation-api"],
                    "user_authenticated": bool(user_id),
                },
                "api_version": "v1",
                "response_pattern": "detail",
            },
        )

        # Record successful movie request metrics
        if metrics:
            metrics.record_movie_request("detail", "success")

        # 🔥 SMART WARMING: Trigger intelligent warming based on movie viewing
        await smart_warming.warm_movie_interaction(
            background_tasks=background_tasks,
            movie_id=movie_id,
            user_id=user_id,
            interaction_type="viewed",
            genre_id=screen_data_dict.get("movie", {}).get("genre_id"),
            has_similar_movies=len(screen_data_dict.get("similar_movies", [])) > 0,
        )

        return cast(dict[str, Any], response)

    except ResourceNotFoundException as e:
        # Record error metrics
        if metrics:
            metrics.record_movie_request("detail", "not_found")

        logger.debug(
            "Movie not found",
            movie_id=movie_id,
            error=str(e),
            service="bff",
            endpoint="movie_detail",
        )
        raise ResourceNotFoundException(
            detail=f"Movie with ID {movie_id} not found",
            resource_id=str(movie_id),
            resource_type="movie",
        )
    except ExternalServiceException as e:
        # Record error metrics
        if metrics:
            metrics.record_movie_request("detail", "service_error")

        logger.error(
            "Backend error for movie detail",
            movie_id=movie_id,
            error=str(e),
            service="bff",
            endpoint="movie_detail",
        )
        if "404" in str(e):
            raise ResourceNotFoundException(
                detail="Movie not found",
                resource_id=str(movie_id),
                resource_type="movie",
            )
        raise ExternalServiceException(
            detail="Backend service unavailable",
            service_name="backend-api",
            error_code="SERVICE_UNAVAILABLE",
        )
    except Exception as e:
        # Record error metrics
        if metrics:
            metrics.record_movie_request("detail", "error")

        logger.error(
            "Unexpected error in movie detail endpoint",
            movie_id=movie_id,
            error=str(e),
            service="bff",
            endpoint="movie_detail",
        )
        raise APIException(
            detail="Internal server error", status_code=500, error_code="INTERNAL_ERROR"
        )


@redis_cache(
    ttl=7
    * 24
    * 3600,  # 7 days for static movies list - shorter than individual movies due to list dynamics
    key_builder=lambda page,
    limit,
    genre_id,
    actor_id,
    sort_by,
    sort_desc,
    imdb_rating,
    rotten_tomatoes_rating,
    metacritic_rating,
    year,
    start_year,
    end_year,
    backend,
    version=None: _build_static_movies_list_cache_key(
        page,
        limit,
        genre_id,
        actor_id,
        sort_by,
        sort_desc,
        imdb_rating,
        rotten_tomatoes_rating,
        metacritic_rating,
        year,
        start_year,
        end_year,
        version,
    ),
)
async def _get_static_movies_list_data(
    page: int,
    limit: int,
    genre_id: int | None,
    actor_id: int | None,
    sort_by: str | None,
    sort_desc: bool | None,
    imdb_rating: float | None,
    rotten_tomatoes_rating: int | None,
    metacritic_rating: int | None,
    year: int | None,
    start_year: int | None,
    end_year: int | None,
    backend: BackendClient,
    version: str | None = None,
) -> dict[str, Any]:
    """Internal cached function for static movies list data."""
    logger.debug(
        "Building static movies list data",
        page=page,
        limit=limit,
        version=version,
        service="bff",
        component="static_list_data",
    )

    # Build filter parameters
    kwargs: dict[str, Any] = {"page": page, "limit": limit}

    # Add optional filters
    if genre_id is not None:
        kwargs["genre_id"] = genre_id
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

    # Get movies from backend without user-specific data
    movies_response = await backend.get_movies(**kwargs)

    # Extract pagination data from backend's standardized format
    movies = movies_response.get("results", [])
    total_count = movies_response.get("total", 0)
    current_page = movies_response.get("page", page)
    per_page = movies_response.get("per_page", limit)
    total_pages = movies_response.get("total_pages", 0)
    has_next = movies_response.get("has_next", False)
    has_prev = movies_response.get("has_prev", False)

    # Build the static movies list response
    list_data = {
        "total": total_count,
        "page": current_page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev,
        "results": movies,
    }

    logger.debug(
        "Successfully built static movies list data",
        page=page,
        limit=limit,
        total_movies=len(movies),
        service="bff",
        component="static_list_data",
    )

    return list_data


@redis_cache(
    ttl=180,  # 3 minutes for batch user interactions - slightly shorter for list consistency
    key_builder=lambda movie_ids, user_id, backend, credentials: _build_user_movies_batch_cache_key(
        movie_ids, user_id
    ),
)
async def _get_user_movies_batch_interactions(
    movie_ids: list[int],
    user_id: int | None,
    backend: BackendClient,
    credentials: HTTPAuthorizationCredentials | None = None,
) -> dict[int, dict[str, Any]]:
    """Internal cached function for user interactions with a batch of movies."""
    logger.debug(
        "Fetching user interactions for movie batch",
        movie_count=len(movie_ids),
        user_id=user_id,
        service="bff",
        component="batch_user_data",
    )

    # Initialize empty result dict
    interactions_by_movie_id: dict[int, dict[str, Any]] = {}

    # Default interaction values
    default_interaction = {
        "in_watchlist": False,
        "is_favorite": False,
        "user_rating": None,
        "watch_progress": 0,
        "is_watched": False,
        "liked": False,
        "watched": False,
    }

    # For anonymous users, return default values for all movies
    if not user_id or not credentials:
        for movie_id in movie_ids:
            interactions_by_movie_id[movie_id] = default_interaction.copy()
        return interactions_by_movie_id

    # For authenticated users, use the new batch endpoint
    try:
        # Use the batch method from the client
        batch_interactions = await backend.get_user_movie_interactions_batch(
            user_id, movie_ids, jwt_token=credentials.credentials
        )

        # Convert the batch response to the expected format
        for movie_id in movie_ids:
            interaction_data = batch_interactions.get(movie_id)
            if interaction_data:
                interactions_by_movie_id[movie_id] = {
                    "in_watchlist": interaction_data.get("in_watchlist", False),
                    "is_favorite": interaction_data.get("liked", False),
                    "user_rating": interaction_data.get("rating"),
                    "watch_progress": interaction_data.get("watch_progress", 0),
                    "is_watched": interaction_data.get("watched", False),
                    "liked": interaction_data.get("liked", False),
                    "watched": interaction_data.get("watched", False),
                }
            else:
                interactions_by_movie_id[movie_id] = default_interaction.copy()

    except Exception as e:
        logger.warning(
            "Failed to get batch user interactions",
            movie_count=len(movie_ids),
            user_id=user_id,
            error=str(e),
            service="bff",
            component="batch_user_data",
        )
        # Fallback to default values for all movies
        for movie_id in movie_ids:
            interactions_by_movie_id[movie_id] = default_interaction.copy()

    return interactions_by_movie_id


async def _get_movies_list_data(
    page: int,
    limit: int,
    genre_id: int | None,
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
    """Compose movies list data from separate cached components."""
    logger.debug(
        "Composing movies list data",
        page=page,
        limit=limit,
        user_id=user_id,
        service="bff",
        component="list_data",
    )

    # Get static movies list data (cached separately with longer TTL)
    static_data = await _get_static_movies_list_data(
        page=page,
        limit=limit,
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
        backend=backend,
    )

    # Extract movie IDs from the results
    movie_ids = [movie.get("id") for movie in static_data["results"] if movie.get("id")]

    # Get user interactions for the batch of movies (cached separately with shorter TTL)
    if movie_ids:
        user_interactions = await _get_user_movies_batch_interactions(
            movie_ids, user_id, backend, credentials
        )

        # Enrich movies with user interaction data
        for movie in static_data["results"]:
            movie_id = movie.get("id")
            if movie_id and movie_id in user_interactions:
                interaction = user_interactions[movie_id]
                movie.update(
                    {
                        "liked": interaction.get("liked", False),
                        "watched": interaction.get("watched", False),
                        "in_watchlist": interaction.get("in_watchlist", False),
                        "user_interactions": {
                            "in_watchlist": interaction.get("in_watchlist", False),
                            "is_favorite": interaction.get("is_favorite", False),
                            "user_rating": interaction.get("user_rating"),
                            "watch_progress": interaction.get("watch_progress", 0),
                            "is_watched": interaction.get("is_watched", False),
                        },
                    }
                )
            else:
                # Set default values if no interaction data exists
                movie.update(
                    {
                        "liked": False,
                        "watched": False,
                        "in_watchlist": False,
                        "user_interactions": {
                            "in_watchlist": False,
                            "is_favorite": False,
                            "user_rating": None,
                            "watch_progress": 0,
                            "is_watched": False,
                        },
                    }
                )

    logger.debug(
        "Successfully composed movies list data",
        page=page,
        limit=limit,
        user_id=user_id,
        total_movies=len(static_data["results"]),
        service="bff",
        component="list_data",
    )

    return static_data


@rate_limit(requests=100, window=60)
@router.get("/movies")
async def get_movies_list(
    pagination: PaginationParams = get_pagination(max_page_size=100),
    genre_id: int | None = Query(None, description="Filter by genre ID"),
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
    backend: BackendClient = Depends(get_backend_client),
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict[str, Any]:
    """Get paginated list of movies with filters.

    Provides paginated movie listings with support for filtering by genre,
    actor, ratings, release year, and sorting by various criteria with
    user personalization.

    Args:
        pagination: Pagination parameters (page, limit) from fast-core dependency
        genre_id: Optional genre filter
        actor_id: Optional actor TMDB ID filter
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
        ExternalServiceException: If backend service is unavailable
    """
    # Record movie request metrics
    metrics = get_bff_metrics()
    if metrics:
        metrics.record_movie_request("list", "started")

    # Extract user ID from JWT token if provided
    user_id = None
    logger.info(
        "Processing movies list request",
        page=pagination.page,
        limit=pagination.limit,
        has_credentials=bool(credentials),
        service="bff",
        endpoint="movies_list",
    )

    if credentials and credentials.credentials:
        user_id = extract_user_id_from_token(credentials.credentials)
        logger.debug(
            "User authenticated for movies list",
            user_id=user_id,
            service="bff",
            endpoint="movies_list",
        )
    else:
        logger.debug(
            "Anonymous user accessing movies list",
            service="bff",
            endpoint="movies_list",
        )

    try:
        # Compose movies list data from separate cached components
        list_data_dict = await _get_movies_list_data(
            page=pagination.page,
            limit=pagination.limit,
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
            user_id=user_id,
            backend=backend,
            credentials=credentials,
        )

        # Use ResponseBuilder paginated pattern for consistent response structure
        response = responses.paginated(
            items=list_data_dict["results"],
            page=list_data_dict["page"],
            limit=list_data_dict["per_page"],
            total=list_data_dict["total"],
            metadata={
                "filters_applied": {
                    "genre_id": genre_id,
                    "actor_id": actor_id,
                    "sort_by": sort_by,
                    "sort_desc": sort_desc,
                    "imdb_rating": imdb_rating,
                    "rotten_tomatoes_rating": rotten_tomatoes_rating,
                    "metacritic_rating": metacritic_rating,
                    "year": year,
                    "start_year": start_year,
                    "end_year": end_year,
                },
                "service_info": {
                    "aggregated_from": ["backend-api"],
                    "user_authenticated": bool(user_id),
                    "user_personalized": bool(user_id),
                },
                "api_version": "v1",
                "response_pattern": "paginated",
            },
        )

        # Record successful movie request metrics
        if metrics:
            metrics.record_movie_request("list", "success")

        return cast(dict[str, Any], response)

    except ExternalServiceException as e:
        # Record error metrics
        if metrics:
            metrics.record_movie_request("list", "service_error")

        logger.error(
            "Backend error for movies list",
            error=str(e),
            service="bff",
            endpoint="movies_list",
            exc_info=True,  # Include stack trace for internal errors
        )
        raise ExternalServiceException(
            detail="Backend service unavailable",
            service_name="backend-api",
            error_code="SERVICE_UNAVAILABLE",
        )
    except Exception as e:
        # Record error metrics
        if metrics:
            metrics.record_movie_request("list", "error")

        logger.error(
            "Unexpected error in movies list endpoint",
            error=str(e),
            service="bff",
            endpoint="movies_list",
            exc_info=True,  # Include stack trace for internal errors
        )
        raise APIException(
            detail="Internal server error", status_code=500, error_code="INTERNAL_ERROR"
        )


# Example of how to use cache invalidation in an endpoint that updates user interactions
"""
# Example implementation - not actual code
@router.post("/movies/{movie_id}/interactions")
async def update_movie_interaction(
    movie_id: int,
    interaction_data: Dict[str, Any],
    backend: BackendClient,
    credentials: HTTPAuthorizationCredentials,
) -> Dict[str, Any]:
    # Extract user ID from JWT token
    user_id = extract_user_id_from_token(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        # Update interaction in backend
        updated_interaction = await backend.update_interaction(
            user_id, movie_id, interaction_data,
            jwt_token=credentials.credentials
        )

        # Invalidate user-specific cache for this movie
        await invalidate_user_movie_cache(movie_id, user_id)

        return {
            "status": "success",
            "interaction": updated_interaction
        }

    except Exception as e:
        logger.error("Error updating interaction", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
"""


# Best Practices for Separating Static and User Data Caching:
#
# 1. Two-Layer Caching Approach:
#    - Static data (movies, cast, trailers) is cached with longer TTL (1 hour+)
#    - User-specific data (interactions, preferences) is cached with shorter TTL (5 minutes)
#
# 2. Cache Key Design:
#    - Static data keys: "screen:movie:static:{movie_id}"
#    - User data keys: "screen:movie:user:{movie_id}:user:{user_id}"
#    - Batch user data: "screen:movies:user:batch:{user_id}:{movie_ids}"
#
# 3. Cache Invalidation Strategy:
#    - For user interaction changes: Invalidate only user-specific cache
#    - For movie data changes: Invalidate static data cache
#    - Use targeted invalidation based on the specific data that changed
#
# 4. Implementation Notes:
#    - The cache.manager module needs a get_cache_manager function
#    - You may need to implement this function if it doesn't exist
#    - The RedisProvider needs to implement delete_pattern for pattern-based invalidation


# Note: The following functions assume the existence of a get_cache_manager function
# in the cache.manager module. You may need to implement this function if it doesn't exist.
# For now, we're wrapping the import in a try-except block to avoid errors.


async def invalidate_user_movie_cache(movie_id: int, user_id: int) -> None:
    """Invalidate user-specific cache for a movie when interactions change.

    This function should be called whenever a user's interaction with a movie changes,
    such as adding to watchlist, marking as watched, liking, etc.

    Args:
        movie_id: ID of the movie whose cache should be invalidated
        user_id: ID of the user whose interaction changed
    """
    logger.debug(
        "Invalidating user movie cache",
        movie_id=movie_id,
        user_id=user_id,
        service="bff",
        component="cache_invalidation",
    )

    try:
        # Import the cache manager here to avoid circular imports
        try:
            # Import from BFF API's cache service
            from bff_api.services.cache_service import get_cache_manager

            cache_manager = get_cache_manager()

            # Invalidate specific user-movie interaction cache
            user_movie_key = _build_user_movie_interactions_cache_key(movie_id, user_id)
            await cache_manager.delete_key(user_movie_key)

            # Invalidate batch caches containing this movie for this user
            batch_pattern = f"screen:movies:user:batch:{user_id}:*"

            # Use delete_pattern if available, otherwise log a warning
            if hasattr(cache_manager, "delete_pattern"):
                await cache_manager.delete_pattern(batch_pattern)
            else:
                logger.warning(
                    "Cache manager does not support pattern deletion",
                    service="bff",
                    component="cache_invalidation",
                )

            logger.debug(
                "Successfully invalidated user movie cache",
                movie_id=movie_id,
                user_id=user_id,
                service="bff",
                component="cache_invalidation",
            )
        except ImportError:
            logger.warning(
                "Cache manager not available, skipping cache invalidation",
                service="bff",
                component="cache_invalidation",
            )
    except Exception as e:
        logger.error(
            "Failed to invalidate user movie cache",
            movie_id=movie_id,
            user_id=user_id,
            error=str(e),
            service="bff",
            component="cache_invalidation",
            exc_info=True,
        )


async def invalidate_static_movie_cache(movie_id: int) -> None:
    """Invalidate static movie data cache when movie information changes.

    This function should be called whenever movie data changes,
    such as updating movie details, cast, trailers, etc.

    Args:
        movie_id: ID of the movie whose cache should be invalidated
    """
    logger.debug(
        "Invalidating static movie cache",
        movie_id=movie_id,
        service="bff",
        component="cache_invalidation",
    )

    try:
        # Import the cache manager here to avoid circular imports
        try:
            # Import from BFF API's cache service
            from bff_api.services.cache_service import get_cache_manager

            cache_manager = get_cache_manager()

            # Invalidate static movie data cache
            static_movie_key = _build_static_movie_cache_key(movie_id)
            await cache_manager.delete_key(static_movie_key)

            logger.debug(
                "Successfully invalidated static movie cache",
                movie_id=movie_id,
                service="bff",
                component="cache_invalidation",
            )
        except ImportError:
            logger.warning(
                "Cache manager not available, skipping cache invalidation",
                service="bff",
                component="cache_invalidation",
            )
    except Exception as e:
        logger.error(
            "Failed to invalidate static movie cache",
            movie_id=movie_id,
            error=str(e),
            service="bff",
            component="cache_invalidation",
            exc_info=True,
        )


# Note: The cache invalidation implementation uses the BFF API's cache service
# to get a properly configured cache manager. This ensures that the cache
# invalidation functions have access to the correct Redis instance and
# configuration settings.
#
# The implementation follows these best practices:
# 1. Imports the cache manager lazily to avoid circular imports
# 2. Uses the BFF API's cache settings for consistent configuration
# 3. Handles errors gracefully to prevent cache issues from breaking the API
# 4. Uses pattern-based deletion for efficient batch invalidation
# 5. Provides separate functions for static and user-specific data
